import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from parse_jfl import * 
from sag_calculator import * 
import json 



step = 0.0025
format = "%.3f"

st.set_page_config( 
    layout="wide",menu_items=None)



st.markdown("## 轴对称 JFL 生成器")
st.markdown("### 输入镜片参数")
column_input, column_output = st.columns([1,2])
column_output.markdown("""
本工具用于生成JFL文件，用于向车床提供加工数据
* 加工镜片需要有3个面，前表面，后表面和边缘来描述。
  * 按行业习惯，通常用XZ坐标系，Z轴为光轴，X轴为光轴垂直方向
* 每个面可以有多个弧段，每个弧段可以是不同的面型
    * 每一个弧段需要指定其半口径SemiDiameter,即弧段边缘到光轴的距离
* 本工具支持的面型有：
    * 标准面Standard：球面和非球面，需要输入曲率半径和非球面系数
    * 偶次非球面EvenAsphere：需要输入偶次项的个数和每项的系数
    * 离轴球面OffsetCircle：需要输入偏心距和球面半径
    * 直线Line：需要输入直线终点的矢高
"""
)
col1, col2 = column_input.columns(2)
lens_thickness = col1.number_input("镜片中心厚度",format = format, min_value=0.1, max_value=2.0, value=0.2)
lens_diameter = col2.number_input("镜片加工直径", format = format,min_value=1.0, max_value=100.0, value=10.6)
# step = st.number_input("加工步长", min_value=0.001, max_value=0.1, value=0.0025)
plot_placeholder = column_output.empty()

lens_semidiameter = lens_diameter / 2
surface_id_list=['前表面','后表面','边缘']

tabs = column_input.tabs(surface_id_list)

for tab, surface_id in zip(tabs,surface_id_list):
    with tab:
        st.markdown(f"### 输入{surface_id}参数")
        start_point_x = st.number_input(
            f"{surface_id}起始点 X坐标", 
            min_value=0.0, max_value=10.0, 
            value=0.0 if surface_id != '边缘' else lens_semidiameter-1.0,
            format = format,
            key=f"{surface_id}_start_point_x")
        start_point_z = st.number_input(
            f"{surface_id}起始点 Z坐标", 
            min_value=-10.0, max_value=10.0, 
            value={"前表面":0.0,"后表面":lens_thickness,"边缘":3.0}[surface_id], 
            format = format,
            key=f"{surface_id}_start_point_z")

        num_of_segments = st.number_input(
            f"{surface_id}弧段数", min_value=1, max_value=10, value=1,
            key=f"{surface_id}_弧段数")
        for seg in range(num_of_segments):
            with st.expander(f"第{seg+1}弧段", expanded=True):
                col1, col2 = st.columns(2)
                type = st.selectbox("面型", 
                    ['Standard','EvenAsphere', 'OffsetCircle',  'Line'],
                    key = f"{surface_id}_type_{seg}")
                # col2.info(f"{HELP_STRING['surface_explain'][type]}", icon="ℹ️")

                params = PARAMS[type]
                for param in params:
                    col1, col2 = st.columns(2)
                    if param == 'AsphereParams':
                        asphere_term = st.session_state[
                            f"{surface_id}_AsphereTerm_{seg}"]
                        asphere_params = []
                        for i in range(asphere_term):
                            asphere_params.append(
                                st.number_input(f"A{(i+1)*2}", 
                                    format = "%.3e",
                                    key=f"{surface_id}_{param}_{seg}_{i}"))
                        st.session_state[f"{surface_id}_{param}_{seg}"] = asphere_params
                    elif param == 'AsphereTerm':
                        st.number_input(param, 
                            key=f"{surface_id}_{param}_{seg}", min_value=1, max_value=10, value=1)
                    else:
                        default_value = {
                            "Radius": 10.0,
                            "Conic": 0.0,
                            'SemiDiameter': lens_semidiameter,
                        }
                        st.number_input(param, 
                            format = format,
                            key=f"{surface_id}_{param}_{seg}",
                            value = default_value.get(param, 0.0))
                    # col2.info(f"* {HELP_STRING['params_explain'][param]}")
                
# st.markdown('---')
# 绘图部分

surface_sag = [{} for i in range(len(surface_id_list))]

try:
    for i, surface_id in enumerate(surface_id_list):
        r0 = st.session_state[f"{surface_id}_start_point_x"]
        z0 = st.session_state[f"{surface_id}_start_point_z"]
        r = np.arange(r0, lens_semidiameter, step)
        z = np.zeros_like(r)
        z[0] = z0
        for seg in range(st.session_state[f"{surface_id}_弧段数"]):
            ROI_index = (r > r0) & (r <= st.session_state[f"{surface_id}_SemiDiameter_{seg}"])
            r_ROI = r[ROI_index]

            type = st.session_state[f"{surface_id}_type_{seg}"]
            func = TYPE_TO_FUNCTION[type]
            params = {
                param: st.session_state[f"{surface_id}_{param}_{seg}"]
                for param in PARAMS[type]
            }
            z_ROI = func(r_ROI, params, z0)
            z[ROI_index] = z_ROI
            z0 = z_ROI[-1]
            r0 = st.session_state[f"{surface_id}_SemiDiameter_{seg}"]   
            surface_sag[i]['r'] = r
            surface_sag[i]['z'] = z

except:
    pass 

# 结果输出
st.markdown('---')
st.markdown("### 输出结果")
try:
    segments={
        'F_XZ':np.vstack([surface_sag[0]['r'][::-1],surface_sag[0]['z'][::-1]]).T,
        'B_XZ':np.vstack([surface_sag[1]['r'][::-1],surface_sag[1]['z'][::-1]]).T,
        'E_XZ':np.vstack([surface_sag[2]['r'],surface_sag[2]['z']]).T,
    }

    fig = plot_jfl_segments_with_arrows(segments)
    plt.axis('equal')
    plot_placeholder.pyplot(fig)

    jfl_string=build_jfl_string(segments)
    download_button1 = st.download_button(
        label="下载JFL文件",
        data=jfl_string,
        file_name="lens.JFL",
        mime="text/plain",
    )
    
except:
    st.error("请填写完整参数")

params_dict = {}
params_dict["lens"] = {
    "lens_thickness": lens_thickness,
    "lens_diameter": lens_diameter,
    "lens_semidiameter": lens_semidiameter
}
for i, surface_id in enumerate(surface_id_list):
    params_dict[surface_id] = {
        "start_point_x": st.session_state[f"{surface_id}_start_point_x"],
        "start_point_z": st.session_state[f"{surface_id}_start_point_z"],
        "num_of_segments": st.session_state[f"{surface_id}_弧段数"],
        "segments": []
    } 
    for seg in range(st.session_state[f"{surface_id}_弧段数"]):
        
        type = st.session_state[f"{surface_id}_type_{seg}"]
        params_dict[surface_id]["segments"].append({
            "type": type,
            "params": {
                param: st.session_state[f"{surface_id}_{param}_{seg}"]
                for param in PARAMS[type]
            }
        })

# st.json(params_dict)
json_string = json.dumps(params_dict, indent=4)
download_button2 = st.download_button(
    label="下载参数JSON文件",
    data=json_string,
    file_name="lens.json",
    mime="application/json",
)
        