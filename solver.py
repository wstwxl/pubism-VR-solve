"""
solver.py — DLX 精确覆盖求解器
实现 Knuth 的 Algorithm X + Dancing Links，用于求解三维积木拼图。
"""

from rotations import normalize


# ============================================================
# Dancing Links 数据结构
# ============================================================

class DLXNode:
    """Dancing Links 节点"""
    __slots__ = ['left', 'right', 'up', 'down', 'column', 'row_id']

    def __init__(self, column=None, row_id=None):
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.column = column
        self.row_id = row_id


class ColumnHeader(DLXNode):
    """列头节点，附加名称和计数"""
    __slots__ = ['size', 'name']

    def __init__(self, name):
        super().__init__()
        self.column = self
        self.size = 0
        self.name = name


class DLX:
    """
    Dancing Links 实现的 Algorithm X 求解器。
    """

    def __init__(self):
        self.header = ColumnHeader("header")
        self.columns = {}       # name -> ColumnHeader
        self.solution = []
        self.solutions = []
        self._col_list = []     # 有序列列表

    def add_columns(self, col_names):
        """添加列（宇宙集元素）"""
        prev = self.header
        for name in col_names:
            col = ColumnHeader(name)
            self.columns[name] = col
            self._col_list.append(col)
            # 水平插入
            col.right = self.header
            col.left = prev
            prev.right = col
            self.header.left = col
            prev = col

    def add_row(self, row_id, col_names):
        """
        添加一行（一个子集）。
        
        参数:
            row_id:    行标识符（用于追溯解）
            col_names: 该行覆盖的列名列表
        """
        first = None
        for name in col_names:
            col = self.columns[name]
            node = DLXNode(column=col, row_id=row_id)
            # 垂直插入到列底部
            node.down = col
            node.up = col.up
            col.up.down = node
            col.up = node
            col.size += 1
            # 水平链接同一行的节点
            if first is None:
                first = node
                node.left = node
                node.right = node
            else:
                node.right = first
                node.left = first.left
                first.left.right = node
                first.left = node

    def _cover(self, col):
        """覆盖一列"""
        col.right.left = col.left
        col.left.right = col.right
        i = col.down
        while i is not col:
            j = i.right
            while j is not i:
                j.down.up = j.up
                j.up.down = j.down
                j.column.size -= 1
                j = j.right
            i = i.down

    def _uncover(self, col):
        """取消覆盖一列"""
        i = col.up
        while i is not col:
            j = i.left
            while j is not i:
                j.column.size += 1
                j.down.up = j
                j.up.down = j
                j = j.left
            i = i.up
        col.right.left = col
        col.left.right = col

    def _choose_column(self):
        """选择大小最小的列（S heuristic）"""
        min_size = float('inf')
        chosen = None
        col = self.header.right
        while col is not self.header:
            if col.size < min_size:
                min_size = col.size
                chosen = col
                if min_size <= 1:
                    break
            col = col.right
        return chosen

    def search(self, find_all=False):
        """
        Algorithm X 搜索。
        
        参数:
            find_all: 如果为 True，查找所有解；否则找到第一个解即停止
        
        返回:
            bool — 是否找到（至少一个）解
        """
        if self.header.right is self.header:
            # 所有列已覆盖 → 找到一个解
            self.solutions.append(list(self.solution))
            return not find_all  # 如果不需要全部解，返回 True 表示停止

        col = self._choose_column()
        if col is None or col.size == 0:
            return False

        self._cover(col)

        row = col.down
        while row is not col:
            self.solution.append(row.row_id)

            # 覆盖该行涉及的所有其他列
            j = row.right
            while j is not row:
                self._cover(j.column)
                j = j.right

            if self.search(find_all):
                if not find_all:
                    self._uncover(col)
                    return True

            # 回溯
            self.solution.pop()
            j = row.left
            while j is not row:
                self._uncover(j.column)
                j = j.left

            row = row.down

        self._uncover(col)
        return False


# ============================================================
# 拼图求解器
# ============================================================

class PuzzleSolver:
    """
    三维积木拼图求解器。
    将积木拼图问题转化为精确覆盖问题，利用 DLX 求解。
    """

    def __init__(self, pieces, target):
        """
        参数:
            pieces: list of Piece 对象
            target: set of (x,y,z) 目标结构的坐标集合
        """
        self.pieces = pieces
        self.target = set(target)
        self.solutions = []  # 解列表

    def _enumerate_placements(self, piece, piece_index):
        """
        枚举一块积木在目标结构中的所有合法放置。
        
        返回:
            list of (row_id, covered_cells)
            row_id = (piece_index, placement_index)
            covered_cells = frozenset of (x,y,z)
        """
        placements = []
        orientations = piece.get_unique_orientations()
        
        placement_idx = 0
        for ori in orientations:
            # 对每种姿态，尝试在目标中的每个位置平移
            # 计算能放置的偏移量范围
            for anchor in self.target:
                # 以姿态的第一个格为基准，平移到 anchor
                ref = ori[0]
                dx = anchor[0] - ref[0]
                dy = anchor[1] - ref[1]
                dz = anchor[2] - ref[2]
                
                translated = frozenset(
                    (x + dx, y + dy, z + dz) for x, y, z in ori
                )
                
                # 检查是否完全在目标内
                if translated.issubset(self.target):
                    row_id = (piece_index, placement_idx)
                    placements.append((row_id, translated))
                    placement_idx += 1

        # 去重（不同偏移可能产生相同放置）
        seen = set()
        unique_placements = []
        for row_id, cells in placements:
            if cells not in seen:
                seen.add(cells)
                unique_placements.append((row_id, cells))
        
        return unique_placements

    def solve(self, find_all=False, max_solutions=0):
        """
        求解拼图。
        
        参数:
            find_all:       是否查找所有解
            max_solutions:  最多查找多少个解（0 = 无限制，仅当 find_all=True 时有效）
        
        返回:
            list of solutions，每个 solution 是 dict: {piece_index: frozenset_of_cells}
        """
        # 1. 列名 = 每个积木的标识 + 目标中的每个格子
        piece_col_names = [f"P{i}" for i in range(len(self.pieces))]
        cell_col_names = [f"C{x},{y},{z}" for x, y, z in sorted(self.target)]
        all_col_names = piece_col_names + cell_col_names

        # 2. 构建 DLX 矩阵
        dlx = DLX()
        dlx.add_columns(all_col_names)

        # 3. 枚举所有积木的所有合法放置，添加为行
        all_placements = []  # (row_id, piece_index, cells)
        
        print("正在生成所有合法放置...")
        for i, piece in enumerate(self.pieces):
            pls = self._enumerate_placements(piece, i)
            print(f"  积木 '{piece.name}': {len(pls)} 种合法放置")
            for row_id, cells in pls:
                global_row_id = len(all_placements)
                all_placements.append((global_row_id, i, cells))
                
                # 该行覆盖的列：积木标识 + 格子
                covered_cols = [f"P{i}"]
                covered_cols.extend(f"C{x},{y},{z}" for x, y, z in cells)
                dlx.add_row(global_row_id, covered_cols)

        total_placements = len(all_placements)
        print(f"总计 {total_placements} 种放置，开始求解...\n")

        # 4. 求解
        if find_all:
            dlx.search(find_all=True)
            raw_solutions = dlx.solutions
            if max_solutions > 0:
                raw_solutions = raw_solutions[:max_solutions]
        else:
            dlx.search(find_all=False)
            raw_solutions = dlx.solutions

        # 5. 解析结果
        self.solutions = []
        for raw_sol in raw_solutions:
            solution = {}
            for global_row_id in raw_sol:
                _, piece_idx, cells = all_placements[global_row_id]
                solution[piece_idx] = cells
            self.solutions.append(solution)

        return self.solutions
