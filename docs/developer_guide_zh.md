# 开发者指南

## 概述
本指南为维护或扩展 JFL 生成器工具的开发人员提供有关底层 Python 模块和项目结构的技术细节。

## 核心模块

### 1. `sag_calculator.py`
该模块包含计算表面轮廓（矢高或 "sag"）的核心数学逻辑。

*   **关键函数**：
    *   `standard(r, params, z0)`：计算标准球面/非球面表面的矢高。
        *   公式：$z = \frac{cr^2}{1+\sqrt{1-(1+k)c^2r^2}}$
        *   处理基础偏移 `z0`。
    *   `offset_circle(r, params, z0)`：计算偏心圆（常用于过渡弧）的矢高。
        *   公式涉及径向坐标的偏移：$(r - r_0)^2$。
    *   `even_asphere(r, params, z0)`：计算偶次非球面的矢高。
        *   基础圆锥曲线 + 多项式项求和 ($A_2 r^2 + A_4 r^4 + \dots$)。
    *   `line(r, params, z0)`：起点和终点之间的线性插值。
*   **映射**：
    *   `TYPE_TO_FUNCTION`：将字符串键（如 'Standard'）映射到相应的函数。
    *   `PARAMS`：定义每种表面类型所需的参数列表。

### 2. `parse_jfl.py`
该模块处理与专有 JFL 格式相关的输入/输出操作以及可视化功能。

*   **JFL 处理**：
    *   `build_jfl_string(segments)`：将计算出的点数据转换为格式化的 JFL 字符串结构。
    *   `parse_jfl_file(file_path)`：读取现有的 JFL 文件并提取段数据（用于逆向工程或验证）。
*   **可视化**：
    *   `plot_jfl_segments_with_arrows(segments)`：使用 `matplotlib` 生成镜片轮廓的 2D 图。它添加了方向箭头以指示刀具路径或段方向。

## 项目结构

*   `streamlit_app.py`：主 Web 界面 (Streamlit)。
*   `JFL_builder_GUI.py`：桌面界面 (Tkinter)。
*   `OK5_*.html`：用于快速原型设计/可视化角膜塑形镜设计的独立浏览器工具。
*   `docs/`：文档目录（本文档所在位置）。

## 扩展指南

### 添加新的表面类型
1.  **定义数学逻辑**：在 `sag_calculator.py` 中实现一个新的矢高函数（例如 `toric_sag`）。
2.  **注册**：在 `sag_calculator.py` 中将新类型添加到 `TYPE_TO_FUNCTION` 并在 `PARAMS` 中定义其预期参数。
3.  **更新 UI**：
    *   对于 `streamlit_app.py`，如果新参数在字典中定义，动态参数循环应能自动识别。
    *   对于 `JFL_builder_GUI.py`，确保参数生成逻辑能处理任何新的特定字段（如多项式系数的列表输入）。

### 修改 JFL 输出格式
*   编辑 `parse_jfl.py` 中的 `build_jfl_string` 函数。
*   确保页眉和页脚常量符合目标机器的要求。
