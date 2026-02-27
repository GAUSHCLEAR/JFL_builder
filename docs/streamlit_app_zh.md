# Streamlit 应用文档

## 概述
`streamlit_app.py` 是一个基于 [Streamlit](https://streamlit.io/) 构建的 Web 应用程序，用于生成接触镜车床加工所需的 JFL (Job File Layout) 文件。它提供了一个交互式界面，供用户输入镜片参数、可视化镜片几何形状并导出数据。

## 功能特性
*   **轴对称 JFL 生成器**：专为生成旋转对称镜片的 JFL 文件而设计。
*   **交互式输入**：用户可以定义三个表面的参数：前表面、后表面和边缘。
*   **分段表面定义**：每个表面可以由多个弧段组成，每个弧段由特定的面型和参数定义。
*   **支持的面型**：
    *   `Standard` (标准面)：球面和非球面 (曲率半径, Conic系数)。
    *   `EvenAsphere` (偶次非球面)：偶次非球面 (曲率半径, Conic系数, 非球面项系数)。
    *   `OffsetCircle` (离轴球面)：偏心球面 (曲率半径, Conic系数, 偏心距)。
    *   `Line` (直线)：直线段 (终点矢高)。
*   **可视化**：
    *   生成镜片弧段的 2D 截面图。
    *   可视化方向箭头以指示加工路径。
*   **导出**：
    *   **JFL 文件**：生成并下载用于车床加工的 `.JFL` 文件。
    *   **JSON 文件**：将设计参数导出为 `.json` 文件，以便保存和重新加载配置。

## 使用方法
1.  **启动应用**：使用 streamlit 运行脚本：
    ```bash
    streamlit run streamlit_app.py
    ```
2.  **输入镜片参数**：
    *   设置 `镜片中心厚度` 和 `镜片加工直径`。
    *   在标签页 ("前表面", "后表面", "边缘") 之间切换以定义每个表面。
    *   设置每个表面的起始 X 和 Z 坐标。
    *   定义每个表面的 `弧段数`。
3.  **定义弧段**：
    *   对于每个弧段，选择 `面型` (Standard, EvenAsphere, OffsetCircle, Line)。
    *   输入所选类型的具体参数 (如 Radius, Conic, Semi-Diameter 等)。
    *   *注意*：半口径 (Semi-Diameter) 决定了该弧段的径向范围。
4.  **可视化**：当您修改参数（或输入完整后），图表会自动更新。
5.  **下载**：
    *   点击 "下载JFL文件" 获取机器可读的 JFL 文件。
    *   点击 "下载参数JSON文件" 保存您的设计。

## 代码结构
*   **导入**：使用 `streamlit`, `numpy`, `matplotlib`, `parse_jfl`, 和 `sag_calculator`。
*   **配置**：将页面布局设置为宽屏模式。
*   **输入部分**：使用 `st.columns`, `st.tabs`, 和 `st.expander` 来组织输入控件。
*   **矢高计算**：遍历表面和弧段，调用 `sag_calculator.py` 中的函数 (`TYPE_TO_FUNCTION`)，根据径向坐标 (r) 计算 Z 坐标。
*   **绘图**：使用 `parse_jfl.py` 中的 `plot_jfl_segments_with_arrows` 函数来可视化几何形状。
*   **导出逻辑**：
    *   使用 `build_jfl_string` 构建 JFL 字符串。
    *   构建 JSON 字典并对其进行序列化，用于 JSON 下载。

## 依赖项
*   `streamlit`
*   `numpy`
*   `matplotlib`
*   `parse_jfl.py` (本地模块)
*   `sag_calculator.py` (本地模块)
