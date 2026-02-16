"""
main.py — 三维积木拼图求解器入口
内置 Soma Cube 示例，同时展示如何自定义积木和目标结构。
"""

from pieces import Piece, create_box_target, create_target_from_layers, SOMA_PIECES, SOMA_TARGET
from solver import PuzzleSolver
from visualizer import visualize_solution, visualize_pieces


def solve_soma_cube():
    """
    求解 Soma Cube（索玛立方体）：
    7 块不规则积木拼成 3×3×3 的立方体。
    """
    print("=" * 50)
    print("  Soma Cube 求解器")
    print("  7 块积木 → 3×3×3 立方体")
    print("=" * 50)
    print()

    pieces = SOMA_PIECES
    target = SOMA_TARGET

    # 打印积木信息
    for p in pieces:
        print(f"  {p}")
    print()

    # 求解（只找第一个解，速度快）
    solver = PuzzleSolver(pieces, target)
    solutions = solver.solve(find_all=False)

    if solutions:
        print(f"✓ 找到解！")
        print()

        # 可视化第一个解
        visualize_solution(solutions[0], pieces, target,
                           title="Soma Cube 解")
    else:
        print("✗ 无解！")


def custom_example():
    """
    自定义积木和目标结构的示例。
    展示如何定义你自己的积木和拼图。
    """
    print("=" * 50)
    print("  自定义拼图示例")
    print("  4 块积木 → 2×4×2 长方体")
    print("=" * 50)
    print()

    # 定义积木 —— 每块用坐标列表描述
    my_pieces = [
        Piece("直条", [(0,0,0), (1,0,0), (2,0,0), (3,0,0)],
              color="#e74c3c"),
        Piece("L形", [(0,0,0), (1,0,0), (2,0,0), (2,1,0)],
              color="#3498db"),
        Piece("T形", [(0,0,0), (1,0,0), (2,0,0), (1,1,0)],
              color="#2ecc71"),
        Piece("方块", [(0,0,0), (1,0,0), (0,1,0), (1,1,0)],
              color="#f39c12"),
    ]

    # 定义目标结构 —— 一个 2×4×2 长方体（共 16 格）
    # 注意：积木总格数也必须 = 16 → 4+4+4+4 = 16 ✓
    my_target = create_box_target(4, 2, 2)

    # 打印积木信息
    for p in my_pieces:
        print(f"  {p}")
    print()

    # 求解
    solver = PuzzleSolver(my_pieces, my_target)
    solutions = solver.solve(find_all=False)

    if solutions:
        print(f"✓ 找到解！")
        visualize_solution(solutions[0], my_pieces, my_target,
                           title="自定义拼图解 (4块→2×4×2)")
    else:
        print("✗ 无解！请检查积木与目标是否匹配。")


def main():
    print()
    print("三维积木拼图求解器")
    print("=" * 50)
    print("  1. Soma Cube（索玛立方体）")
    print("  2. 自定义示例（4块→2×4×2）")
    print("  3. 查看 Soma Cube 积木形状")
    print("=" * 50)

    choice = input("\n请选择 (1/2/3，默认 1): ").strip()
    if not choice:
        choice = "1"

    if choice == "1":
        solve_soma_cube()
    elif choice == "2":
        custom_example()
    elif choice == "3":
        visualize_pieces(SOMA_PIECES)
    else:
        print("无效选择。")


if __name__ == "__main__":
    main()
