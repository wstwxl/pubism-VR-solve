"""
solve_from_json.py — 从 JSON 文件读取积木和目标，自动求解并可视化
用法：python solve_from_json.py puzzle_data.json
"""

import sys
import json
from pieces import Piece
from solver import PuzzleSolver
from visualizer import visualize_solution


def load_puzzle(json_path):
    """从 JSON 文件加载拼图数据"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pieces = []
    for pd in data['pieces']:
        coords = [tuple(c) for c in pd['cells']]
        if len(coords) == 0:
            continue
        # 归一化坐标（让最小值为 0）
        min_x = min(c[0] for c in coords)
        min_y = min(c[1] for c in coords)
        min_z = min(c[2] for c in coords)
        coords = [(c[0] - min_x, c[1] - min_y, c[2] - min_z) for c in coords]
        pieces.append(Piece(
            name=pd.get('name', f'积木{len(pieces)+1}'),
            coords=coords,
            color=pd.get('color', None)
        ))

    target = set()
    for c in data['target']['cells']:
        target.add(tuple(c))

    return pieces, target


def main():
    if len(sys.argv) < 2:
        print("用法: python solve_from_json.py <puzzle_data.json>")
        print("请先用 editor.html 创建积木和目标结构，导出 JSON 文件。")
        sys.exit(1)

    json_path = sys.argv[1]
    print(f"正在加载: {json_path}")

    pieces, target = load_puzzle(json_path)

    print(f"\n已加载 {len(pieces)} 块积木，目标结构 {len(target)} 格")
    piece_total = sum(len(p.coords) for p in pieces)
    print(f"积木总格数: {piece_total}")

    if piece_total != len(target):
        print(f"\n⚠ 警告：积木总格数 ({piece_total}) ≠ 目标格数 ({len(target)})")
        print("  这意味着可能无解。")

    print()
    for p in pieces:
        print(f"  {p}")
    print()

    # 求解
    solver = PuzzleSolver(pieces, target)
    solutions = solver.solve(find_all=False)

    if solutions:
        print(f"✓ 找到解！")
        visualize_solution(solutions[0], pieces, target, title="拼图解")
    else:
        print("✗ 无解。请检查积木与目标结构是否正确。")


if __name__ == '__main__':
    main()
