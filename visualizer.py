"""
visualizer.py — 三维可视化
使用 matplotlib 将拼图解以 3D 体素图展示，每块积木用不同颜色区分。
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

# 修复中文显示：尝试使用系统中文字体
_CN_FONTS = ['SimHei', 'Microsoft YaHei', 'STSong', 'STHeiti', 'Arial Unicode MS']
for _f in _CN_FONTS:
    try:
        matplotlib.font_manager.findfont(_f, fallback_to_default=False)
        matplotlib.rcParams['font.sans-serif'] = [_f] + matplotlib.rcParams['font.sans-serif']
        break
    except Exception:
        continue
matplotlib.rcParams['axes.unicode_minus'] = False  # 负号显示


def visualize_solution(solution, pieces, target, title="积木拼图解"):
    """
    可视化一个拼图解。
    
    参数:
        solution: dict {piece_index: frozenset of (x,y,z)}
        pieces:   list of Piece 对象
        target:   set of (x,y,z) 目标结构
        title:    窗口标题
    """
    # 计算边界
    all_coords = list(target)
    xs = [c[0] for c in all_coords]
    ys = [c[1] for c in all_coords]
    zs = [c[2] for c in all_coords]
    
    sx = max(xs) + 1
    sy = max(ys) + 1
    sz = max(zs) + 1

    # 创建体素数组和颜色数组
    voxels = np.zeros((sx, sy, sz), dtype=bool)
    colors = np.empty((sx, sy, sz, 4))  # RGBA
    colors[:] = [0, 0, 0, 0]  # 透明

    # 默认配色方案
    default_colors = [
        "#e74c3c", "#3498db", "#2ecc71", "#f39c12",
        "#9b59b6", "#1abc9c", "#e67e22", "#d35400",
        "#c0392b", "#2980b9", "#27ae60", "#f1c40f",
        "#8e44ad", "#16a085", "#e84393", "#6c5ce7",
    ]

    legend_entries = []

    for piece_idx, cells in solution.items():
        piece = pieces[piece_idx]
        if piece.color:
            rgba = to_rgba(piece.color, alpha=0.85)
        else:
            rgba = to_rgba(default_colors[piece_idx % len(default_colors)], alpha=0.85)

        legend_entries.append((piece.name, rgba))

        for x, y, z in cells:
            voxels[x, y, z] = True
            colors[x, y, z] = rgba

    # 绘图
    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.voxels(voxels, facecolors=colors, edgecolors='#333333', linewidth=0.5)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title, fontsize=14, fontweight='bold')

    # 设置等比例 —— 确保显示为正方体
    max_dim = max(sx, sy, sz)
    ax.set_xlim(0, max_dim)
    ax.set_ylim(0, max_dim)
    ax.set_zlim(0, max_dim)
    ax.set_box_aspect([1, 1, 1])  # 强制三轴等比例 → 正方体

    # 图例
    from matplotlib.patches import Patch
    legend_patches = [
        Patch(facecolor=rgba, edgecolor='#333', label=name)
        for name, rgba in legend_entries
    ]
    ax.legend(handles=legend_patches, loc='upper left', fontsize=9)

    plt.tight_layout()
    plt.show()


def visualize_pieces(pieces):
    """
    分别可视化每块积木的形状。
    
    参数:
        pieces: list of Piece 对象
    """
    n = len(pieces)
    cols = min(4, n)
    rows = (n + cols - 1) // cols

    fig = plt.figure(figsize=(4 * cols, 4 * rows))

    default_colors = [
        "#e74c3c", "#3498db", "#2ecc71", "#f39c12",
        "#9b59b6", "#1abc9c", "#e67e22", "#d35400",
    ]

    for idx, piece in enumerate(pieces):
        ax = fig.add_subplot(rows, cols, idx + 1, projection='3d')

        coords = piece.coords
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        zs = [c[2] for c in coords]

        sx = max(xs) + 1
        sy = max(ys) + 1
        sz = max(zs) + 1

        voxels = np.zeros((sx, sy, sz), dtype=bool)
        color = piece.color or default_colors[idx % len(default_colors)]
        facecolors = np.empty((sx, sy, sz, 4))
        facecolors[:] = to_rgba(color, alpha=0.85)

        for x, y, z in coords:
            voxels[x, y, z] = True

        ax.voxels(voxels, facecolors=facecolors, edgecolors='#333', linewidth=0.5)
        ax.set_title(f"{piece.name} ({len(coords)} 格)", fontsize=11)

        max_dim = max(sx, sy, sz, 3)
        ax.set_xlim(0, max_dim)
        ax.set_ylim(0, max_dim)
        ax.set_zlim(0, max_dim)
        ax.set_box_aspect([1, 1, 1])  # 正方体比例

    plt.suptitle("积木一览", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()
