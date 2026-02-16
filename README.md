# 🧩 三维积木拼图求解器 (Cubism VR Solve)

用多块三维积木拼出一个目标结构的自动求解器。内置可视化编辑器和 DLX 精确覆盖算法。

**在线体验**：[https://wstwxl.github.io/pubism-VR-solve/](https://wstwxl.github.io/pubism-VR-solve/)

## 功能

- **可视化编辑器**：在浏览器中逐层绘制积木和目标结构，支持 3D 预览、鼠标旋转、JSON 导入导出
- **DLX 求解器**：基于 Knuth 的 Algorithm X + Dancing Links，高效求解精确覆盖问题
- **3D 结果展示**：matplotlib 渲染拼装结果，每块积木不同颜色

## 快速开始

### 方式一：网页编辑器（推荐）

直接打开 `index.html` 或访问在线版本。

1. **编辑积木**：在"编辑积木"模式下逐块创建积木形状
2. **编辑目标**：切换到"编辑目标"模式，画出目标结构
3. **导出求解**：点击"导出并求解"下载 `puzzle_data.json`
4. **运行求解器**：

```bash
python solve_from_json.py puzzle_data.json
```

### 方式二：代码直接调用

```bash
python main.py   # 内置 Soma Cube 示例
```

## 环境配置

```bash
# Python 3.10+
pip install numpy matplotlib
```

## 项目结构

```
├── index.html           # 网页可视化编辑器（主页面）
├── solve_from_json.py   # 从 JSON 文件读取并求解
├── main.py              # 入口（内置 Soma Cube 示例）
├── solver.py            # DLX 精确覆盖求解器
├── pieces.py            # 积木定义与旋转姿态生成
├── rotations.py         # 24 种三维旋转矩阵
├── visualizer.py        # matplotlib 3D 可视化
└── requirements.txt     # 依赖
```

## 算法原理

将三维拼图建模为**精确覆盖问题**：目标结构的每个格子恰好被一块积木覆盖。使用 Dancing Links (DLX) 数据结构实现高效回溯搜索。

## License

MIT
