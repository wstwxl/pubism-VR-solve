"""
pieces.py — 积木定义与管理
提供 Piece 类来定义三维积木，并自动生成所有旋转姿态。
"""

from rotations import ALL_ROTATIONS, rotate_coords, normalize


class Piece:
    """
    表示一块三维积木。
    
    属性:
        name:   积木名称（用于显示）
        coords: 基础形状坐标列表 [(x,y,z), ...]
        color:  显示颜色（matplotlib 颜色字符串或 RGBA 元组）
    """

    def __init__(self, name, coords, color=None):
        """
        参数:
            name:   积木名称
            coords: 组成积木的单位格坐标列表，如 [(0,0,0), (1,0,0), (2,0,0)]
            color:  可选，matplotlib 颜色
        """
        self.name = name
        self.coords = [tuple(c) for c in coords]
        self.color = color
        self._orientations = None  # 缓存

    def get_unique_orientations(self):
        """
        计算该积木所有不重复的旋转姿态。
        
        返回:
            list of list of (x,y,z) — 每个元素是一种唯一姿态的坐标列表
        """
        if self._orientations is not None:
            return self._orientations

        seen = set()
        orientations = []
        for rot_matrix in ALL_ROTATIONS:
            rotated = rotate_coords(self.coords, rot_matrix)
            normalized = normalize(rotated)
            if normalized not in seen:
                seen.add(normalized)
                orientations.append(list(normalized))
        
        self._orientations = orientations
        return orientations

    def __repr__(self):
        return f"Piece('{self.name}', {len(self.coords)} cells, {len(self.get_unique_orientations())} orientations)"


def create_box_target(sx, sy, sz):
    """
    创建一个长方体目标结构。
    
    参数:
        sx, sy, sz: 长方体在 x, y, z 轴的尺寸
    
    返回:
        set of (x, y, z)
    """
    return {(x, y, z) for x in range(sx) for y in range(sy) for z in range(sz)}


def create_target_from_layers(layers):
    """
    从逐层的二维网格创建三维目标结构。
    每一层是一个二维列表，1 表示有方块，0 表示空。
    layers[0] 是 z=0 层，layers[1] 是 z=1 层，以此类推。
    
    示例（创建一个 L 形柱体，高 2 层）:
        layers = [
            [[1, 1],
             [1, 0]],   # z=0
            [[1, 1],
             [1, 0]],   # z=1
        ]
    
    返回:
        set of (x, y, z)
    """
    target = set()
    for z, layer in enumerate(layers):
        for y, row in enumerate(layer):
            for x, cell in enumerate(row):
                if cell:
                    target.add((x, y, z))
    return target


# ============================================================
# 预定义积木集：Soma Cube（索玛立方体）
# 7 块不规则积木拼成 3×3×3 立方体
# ============================================================

SOMA_PIECES = [
    Piece("V", [(0,0,0), (1,0,0), (0,1,0)],
          color="#e74c3c"),     # 红
    Piece("L", [(0,0,0), (1,0,0), (2,0,0), (2,1,0)],
          color="#3498db"),     # 蓝
    Piece("T", [(0,0,0), (1,0,0), (2,0,0), (1,1,0)],
          color="#2ecc71"),     # 绿
    Piece("S", [(0,0,0), (1,0,0), (1,1,0), (2,1,0)],
          color="#f39c12"),     # 橙
    Piece("A", [(0,0,0), (1,0,0), (0,1,0), (0,0,1)],
          color="#9b59b6"),     # 紫
    Piece("B", [(0,0,0), (1,0,0), (1,1,0), (1,0,1)],
          color="#1abc9c"),     # 青
    Piece("P", [(0,0,0), (1,0,0), (1,1,0), (0,0,1)],
          color="#e67e22"),     # 深橙
]

SOMA_TARGET = create_box_target(3, 3, 3)
