"""
rotations.py — 三维旋转工具
提供 24 种三维旋转矩阵，以及对坐标集合进行旋转、归一化的工具函数。
"""

import numpy as np
from itertools import product


def _generate_all_rotation_matrices():
    """
    生成 24 种三维旋转矩阵（纯旋转，不含镜像）。
    方法：枚举所有 3x3 符号排列矩阵中行列式为 +1 的正交矩阵。
    """
    matrices = []
    # 三个轴的排列 (0,1,2) 的全排列 × 每轴正负号 → 筛选行列式=+1
    axes = [0, 1, 2]
    from itertools import permutations
    for perm in permutations(axes):
        for signs in product([1, -1], repeat=3):
            mat = np.zeros((3, 3), dtype=int)
            for i in range(3):
                mat[i][perm[i]] = signs[i]
            if np.linalg.det(mat) > 0:
                matrices.append(mat)
    return matrices


# 预计算的 24 种旋转矩阵
ALL_ROTATIONS = _generate_all_rotation_matrices()


def rotate_coords(coords, matrix):
    """
    对一组三维坐标施加旋转矩阵。
    
    参数:
        coords: list of (x, y, z) 元组
        matrix: 3x3 numpy 旋转矩阵
    
    返回:
        旋转后的坐标列表 [(x, y, z), ...]
    """
    arr = np.array(coords, dtype=int)          # shape: (N, 3)
    rotated = arr @ matrix.T                   # 矩阵右乘转置 = 左乘矩阵
    return [tuple(row) for row in rotated]


def normalize(coords):
    """
    将坐标集合归一化：平移使得各轴最小值为 0。
    这样可以比较两组形状是否相同。
    
    参数:
        coords: list of (x, y, z) 元组
    
    返回:
        归一化并排序后的坐标元组的元组 (用于哈希和比较)
    """
    if not coords:
        return ()
    arr = np.array(coords, dtype=int)
    min_vals = arr.min(axis=0)
    normalized = arr - min_vals
    # 排序以获得唯一表示
    return tuple(sorted(tuple(row) for row in normalized))
