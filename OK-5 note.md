# OK‑5 综合实验室 v14——运行逻辑与界面/绘图笔记

## 一、核心运行逻辑  
1. **输入采集**  
   * 基础参数 `FlatK‧ecc‧TP‧Jessen‧BOD‧lensD‧RCwidth‧edgeLift` 通过 DOM 一次性读取。  
   * 参数对象 `vars` 同时作为 math.js 公式求值的上下文。

2. **公式求值**  
   * **曲率公式** *(bc/ac1/ac2/rc/pc)* 与 **弧段直径公式** *(bcend/rcend/ac1end/ac2end/pcend)* 按 *公式‑>数值* 流程独立计算；正则 `SAFE` 保证只含安全字符。  
   * 公式：
    BC = FlatK-TP-Jessen
    AC1 = FlatK - 2 * ecc 
    AC2 = FlatK - 3 * ecc 
    RC = FlatK+1.5*TP
    PC = FlatK-20*ecc
    BCend = BOD/2
    RCend = BOD/2+RCwidth
    AC1end = ((lensD/2-0.5)-BOD/2-RCwidth)/2+BOD/2+RCwidth
    AC2end = lensD/2-0.5
    PCend = lensD/2
   * 结果写入各自元素的 `dataset.backend` 字段，形成 “公式值” 与 “可手动输入值” 的双向通道。  

3. **锁定/联动机制**  
   * `lockFormula` 勾选时，五段曲率半径随公式实时刷新；否则以手动输入为准。  
   * `lockAC2R` 用于维持 `AC2R‑AC1R` 差值恒定。  
   * `lockSegFormula` 控制弧段终点直径是否跟随公式。  

4. **绘图准备**  
   * **段终点**：`BCend‧RCend‧AC1end‧AC2end‧PCend` 依据 `dataset.backend` 生成镜片分段模型。  
   * **曲率半径**：五段半径与 cornea 半径（由 `FlatK` 转换）共同进入光学面 `sag` 计算。  
   * **ZCubic 曲面方程**：`Z(x,R,k)` 实现旋转抛物面；角膜用 `k=‑e²`，镜片各段 `k=0`。  

5. **主循环 computeAndDraw()**  
   依次完成：读取 → 计算公式 → 更新 UI → 绘图。输入或锁定状态变化均触发该流程。  

---

## 二、界面要点  
* 响应式设计，适合手机、台式机屏幕。

| 区块 | 说明 | 特色 |
|------|------|------|
| **基础输入网格** | 数值 `step` 精度与单位提示 | 新增 `RCwidth` 参数 |
| **曲率公式区** | 可编辑文本框；支持 math.js 表达式 | 与曲率半径区配对显示/编辑 |
| **弧段直径公式区** | 五段终点公式，默认即用户给出的推导 | 同样可自由修改 |
| **数值显示区** | ① 曲率半径 ② 弧段终点直径 | 根据 *显示模式* 或 *锁定* 动态同步 |
| **控制勾选** | 三个锁；影响数据流向 | 界面立即响应，避免二义性 |
| **右侧三幅 Canvas** | 荧光图、泪膜厚度图、矢高图 | 尺寸固定 520×320；Retina 友好 |

---

## 三、绘图细节  
### 1. 矢高图 *(canvas id=sagPlot)*  
* **坐标变换**：将实际半径 `(0–PCend)` 和矢高 `(yMin–yMax)` 映射到画布留白 40 px 的框内。 注意y轴正方向向下。  
* **分段着色**：镜片五段按 `red/green/blue/red/green` 渐进，可直观看到几何结构。  
* **关键点标注**：0与五段终点各画蓝点，并标注矢高数值，转成 μm 标注，无需单位，仅保留整数。
* 坐标轴上需要标注数值，单位μm，仅保留整数  

### 2. 泪膜厚度图 *(id=tearPlot)*  
* 先求角膜‑镜片间距 `tearVals`；用 **最低值归零** 方法消除全局位移。  
* 曲线为绿色；关键点厚度转成 μm 标注，无需单位，仅保留整数。
* 曲线下方填为绿色。
* 坐标轴上需要标注数值，单位μm，仅保留整数  

### 3. 荧光素分布图 *(id=fluoresceinPlot)*  
* 将半径‑厚度表插值到整幅位图；`interpT(r)` 使用线性内插保证平滑。  
* Beer–Lambert 模型：  
  ```js
  G = I_MAX*(1-uBlack*exp(-kBL*thk));
  R = I_MAX*g_ratio*(G/I_MAX)^r_gamma
  ```  
* 非镜片区填黑，生成中心对称的绿‑黄‑红假彩色图。  
