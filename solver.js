/**
 * solver.js — DLX 精确覆盖求解器 (JavaScript 版)
 * 从 Python 版本移植，实现完全在浏览器中求解三维积木拼图。
 */

// ============================================================
// 旋转工具 — 生成 24 种三维旋转矩阵
// ============================================================

function generateAllRotationMatrices() {
    const matrices = [];
    const perms = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];
    const signCombos = [];
    for (const a of [1, -1]) for (const b of [1, -1]) for (const c of [1, -1]) signCombos.push([a, b, c]);

    for (const perm of perms) {
        for (const sign of signCombos) {
            const mat = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
            for (let i = 0; i < 3; i++) mat[i][perm[i]] = sign[i];
            const det = mat[0][0] * (mat[1][1] * mat[2][2] - mat[1][2] * mat[2][1])
                - mat[0][1] * (mat[1][0] * mat[2][2] - mat[1][2] * mat[2][0])
                + mat[0][2] * (mat[1][0] * mat[2][1] - mat[1][1] * mat[2][0]);
            if (det > 0) matrices.push(mat);
        }
    }
    return matrices;
}

const ALL_ROTATIONS = generateAllRotationMatrices(); // 24 种

function rotateCoords(coords, matrix) {
    return coords.map(([x, y, z]) => [
        matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z,
        matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z,
        matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z,
    ]);
}

function normalizeCoords(coords) {
    if (coords.length === 0) return '[]';
    let minX = Infinity, minY = Infinity, minZ = Infinity;
    for (const [x, y, z] of coords) {
        if (x < minX) minX = x;
        if (y < minY) minY = y;
        if (z < minZ) minZ = z;
    }
    const norm = coords.map(([x, y, z]) => [x - minX, y - minY, z - minZ]);
    norm.sort((a, b) => a[0] - b[0] || a[1] - b[1] || a[2] - b[2]);
    return JSON.stringify(norm);
}

function getUniqueOrientations(coords) {
    const seen = new Set();
    const orientations = [];
    for (const mat of ALL_ROTATIONS) {
        const rotated = rotateCoords(coords, mat);
        const key = normalizeCoords(rotated);
        if (!seen.has(key)) {
            seen.add(key);
            orientations.push(JSON.parse(key));
        }
    }
    return orientations;
}

// ============================================================
// Dancing Links 数据结构
// ============================================================

class DLXNode {
    constructor(column, rowId) {
        this.left = this;
        this.right = this;
        this.up = this;
        this.down = this;
        this.column = column || this;
        this.rowId = rowId;
    }
}

class ColumnHeader extends DLXNode {
    constructor(name) {
        super();
        this.column = this;
        this.size = 0;
        this.name = name;
    }
}

class DLX {
    constructor() {
        this.header = new ColumnHeader('header');
        this.columns = {};
        this.solution = [];
        this.solutions = [];
    }

    addColumns(colNames) {
        let prev = this.header;
        for (const name of colNames) {
            const col = new ColumnHeader(name);
            this.columns[name] = col;
            col.right = this.header;
            col.left = prev;
            prev.right = col;
            this.header.left = col;
            prev = col;
        }
    }

    addRow(rowId, colNames) {
        let first = null;
        for (const name of colNames) {
            const col = this.columns[name];
            if (!col) continue;
            const node = new DLXNode(col, rowId);
            node.down = col;
            node.up = col.up;
            col.up.down = node;
            col.up = node;
            col.size++;
            if (first === null) {
                first = node;
                node.left = node;
                node.right = node;
            } else {
                node.right = first;
                node.left = first.left;
                first.left.right = node;
                first.left = node;
            }
        }
    }

    _cover(col) {
        col.right.left = col.left;
        col.left.right = col.right;
        let i = col.down;
        while (i !== col) {
            let j = i.right;
            while (j !== i) {
                j.down.up = j.up;
                j.up.down = j.down;
                j.column.size--;
                j = j.right;
            }
            i = i.down;
        }
    }

    _uncover(col) {
        let i = col.up;
        while (i !== col) {
            let j = i.left;
            while (j !== i) {
                j.column.size++;
                j.down.up = j;
                j.up.down = j;
                j = j.left;
            }
            i = i.up;
        }
        col.right.left = col;
        col.left.right = col;
    }

    _chooseColumn() {
        let minSize = Infinity;
        let chosen = null;
        let col = this.header.right;
        while (col !== this.header) {
            if (col.size < minSize) {
                minSize = col.size;
                chosen = col;
                if (minSize <= 1) break;
            }
            col = col.right;
        }
        return chosen;
    }

    search(findAll = false) {
        if (this.header.right === this.header) {
            this.solutions.push([...this.solution]);
            return !findAll;
        }
        const col = this._chooseColumn();
        if (!col || col.size === 0) return false;

        this._cover(col);
        let row = col.down;
        while (row !== col) {
            this.solution.push(row.rowId);
            let j = row.right;
            while (j !== row) { this._cover(j.column); j = j.right; }

            if (this.search(findAll)) {
                if (!findAll) { this._uncover(col); return true; }
            }

            this.solution.pop();
            j = row.left;
            while (j !== row) { this._uncover(j.column); j = j.left; }

            row = row.down;
        }
        this._uncover(col);
        return false;
    }
}

// ============================================================
// 拼图求解器
// ============================================================

/**
 * 求解三维积木拼图
 * @param {Array} pieces - [{name, color, cells: [[x,y,z],...]}]
 * @param {Array} targetCells - [[x,y,z],...]
 * @returns {{success, solution, log, elapsed}}
 */
function solvePuzzle(pieces, targetCells) {
    const targetSet = new Set(targetCells.map(c => c.join(',')));
    const log = [];

    // 列名 = 积木标识 + 目标格子
    const pieceColNames = pieces.map((_, i) => `P${i}`);
    const cellColNames = [...targetSet].sort().map(k => `C${k}`);
    const allColNames = [...pieceColNames, ...cellColNames];

    const dlx = new DLX();
    dlx.addColumns(allColNames);

    // 枚举所有合法放置
    const allPlacements = [];

    log.push('正在生成所有合法放置...');
    for (let i = 0; i < pieces.length; i++) {
        const piece = pieces[i];
        const orientations = getUniqueOrientations(piece.cells);
        const seen = new Set();
        let count = 0;

        for (const ori of orientations) {
            for (const anchor of targetCells) {
                const ref = ori[0];
                const dx = anchor[0] - ref[0];
                const dy = anchor[1] - ref[1];
                const dz = anchor[2] - ref[2];

                const translated = ori.map(([x, y, z]) => [x + dx, y + dy, z + dz]);
                const translatedKeys = translated.map(c => c.join(','));

                if (translatedKeys.every(k => targetSet.has(k))) {
                    const placementKey = [...translatedKeys].sort().join('|');
                    if (!seen.has(placementKey)) {
                        seen.add(placementKey);
                        const globalRowId = allPlacements.length;
                        allPlacements.push({ pieceIdx: i, cells: translated });
                        const coveredCols = [`P${i}`, ...translatedKeys.map(k => `C${k}`)];
                        dlx.addRow(globalRowId, coveredCols);
                        count++;
                    }
                }
            }
        }
        log.push(`  积木 '${piece.name}': ${orientations.length} 种姿态, ${count} 种合法放置`);
    }

    log.push(`总计 ${allPlacements.length} 种放置，开始求解...`);

    const t0 = performance.now();
    dlx.search(false);
    const elapsed = ((performance.now() - t0) / 1000).toFixed(3);

    if (dlx.solutions.length > 0) {
        const solution = {};
        for (const globalRowId of dlx.solutions[0]) {
            const p = allPlacements[globalRowId];
            solution[p.pieceIdx] = p.cells;
        }
        log.push(`\n✅ 找到解！耗时 ${elapsed} 秒`);
        return { success: true, solution, log, elapsed };
    } else {
        log.push(`\n❌ 无解。耗时 ${elapsed} 秒`);
        return { success: false, solution: null, log, elapsed };
    }
}

// ============================================================
// 默认示例：Soma Cube（索玛立方体 3×3×3）
// ============================================================

const DEFAULT_PUZZLE = {
    pieces: [
        { name: 'V-三角', color: '#e74c3c', cells: [[0, 0, 0], [1, 0, 0], [0, 1, 0]] },
        { name: 'L-拐角', color: '#3498db', cells: [[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0]] },
        { name: 'T-丁字', color: '#2ecc71', cells: [[0, 0, 0], [1, 0, 0], [2, 0, 0], [1, 1, 0]] },
        { name: 'S-阶梯', color: '#f39c12', cells: [[0, 0, 0], [1, 0, 0], [1, 1, 0], [2, 1, 0]] },
        { name: 'A-立角', color: '#9b59b6', cells: [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]] },
        { name: 'B-立拐', color: '#1abc9c', cells: [[0, 0, 0], [1, 0, 0], [1, 1, 0], [1, 0, 1]] },
        { name: 'P-立阶', color: '#e67e22', cells: [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 0, 1]] },
    ],
    target: { cells: [] }
};
// 生成 3×3×3 立方体目标
for (let x = 0; x < 3; x++)
    for (let y = 0; y < 3; y++)
        for (let z = 0; z < 3; z++)
            DEFAULT_PUZZLE.target.cells.push([x, y, z]);
