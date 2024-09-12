import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from parse_jfl import * 
from sag_calculator import * 
import json

# 创建主窗口
root = tk.Tk()
root.title("轴对称 JFL 生成器")

# 创建选项卡
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# 创建滚动条
main_frame = ttk.Frame(notebook)
main_frame.pack(fill='both', expand=True)

canvas = tk.Canvas(main_frame)
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# 全局变量
step = 0.0025
format = "%.3f"
lens_params = {}
surface_params = {}

# 创建输入组件
def create_input_frame(parent, label_text, var_type, default_value, row, col, **kwargs):
    label = ttk.Label(parent, text=label_text)
    label.grid(row=row, column=col, padx=5, pady=5, sticky=tk.W)
    var = var_type(value=default_value)
    entry = ttk.Entry(parent, textvariable=var, **kwargs)
    entry.grid(row=row, column=col+1, padx=5, pady=5)
    return var

# 镜片参数输入
lens_frame = ttk.LabelFrame(scrollable_frame, text="输入镜片参数")
lens_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

lens_thickness_var = create_input_frame(lens_frame, "镜片中心厚度", tk.DoubleVar, 0.2, 0, 0)
lens_diameter_var = create_input_frame(lens_frame, "镜片加工直径", tk.DoubleVar, 10.6, 1, 0)

# 表面参数输入
surface_id_list = ['前表面', '后表面', '边缘']
surface_vars = {}

for i, surface_id in enumerate(surface_id_list):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=surface_id)
    
    surface_vars[surface_id] = {}
    frame = ttk.LabelFrame(tab, text=f"{surface_id}参数")
    frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    start_point_x_var = create_input_frame(frame, f"{surface_id}起始点 X坐标", tk.DoubleVar, 0.0 if surface_id != '边缘' else 9.6, 0, 0)
    start_point_z_var = create_input_frame(frame, f"{surface_id}起始点 Z坐标", tk.DoubleVar, {"前表面":0.0,"后表面":0.2,"边缘":3.0}[surface_id], 1, 0)
    num_of_segments_var = create_input_frame(frame, f"{surface_id}弧段数", tk.IntVar, 1, 2, 0)
    
    surface_vars[surface_id]['start_point_x'] = start_point_x_var
    surface_vars[surface_id]['start_point_z'] = start_point_z_var
    surface_vars[surface_id]['num_of_segments'] = num_of_segments_var
    
    def create_segment_frame(surface_id, seg):
        seg_frame = ttk.LabelFrame(frame, text=f"第{seg+1}弧段")
        seg_frame.grid(row=3+seg, column=0, padx=10, pady=10, sticky=tk.W)
        
        type_var = tk.StringVar(value='Standard')
        type_label = ttk.Label(seg_frame, text="面型")
        type_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        type_combobox = ttk.Combobox(seg_frame, textvariable=type_var, values=['Standard','EvenAsphere', 'OffsetCircle',  'Line'])
        type_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        param_vars = {}
        
        def update_params(*args):
            for widget in seg_frame.winfo_children():
                if isinstance(widget, ttk.Entry) or isinstance(widget, ttk.Label):
                    widget.destroy()
            params = PARAMS[type_var.get()]
            for j, param in enumerate(params):
                param_var = tk.DoubleVar(value=0.0)
                param_label = ttk.Label(seg_frame, text=param)
                param_label.grid(row=j+1, column=0, padx=5, pady=5, sticky=tk.W)
                param_entry = ttk.Entry(seg_frame, textvariable=param_var)
                param_entry.grid(row=j+1, column=1, padx=5, pady=5)
                param_vars[param] = param_var
        
        type_combobox.bind("<<ComboboxSelected>>", update_params)
        update_params()
        
        surface_vars[surface_id][f'segment_{seg}'] = {
            'type': type_var,
            'params': param_vars
        }
    
    for seg in range(num_of_segments_var.get()):
        create_segment_frame(surface_id, seg)

# 绘图和保存文件
def plot_and_save():
    lens_thickness = lens_thickness_var.get()
    lens_diameter = lens_diameter_var.get()
    lens_semidiameter = lens_diameter / 2
    
    surface_sag = [{} for _ in range(len(surface_id_list))]
    
    try:
        for i, surface_id in enumerate(surface_id_list):
            r0 = surface_vars[surface_id]['start_point_x'].get()
            z0 = surface_vars[surface_id]['start_point_z'].get()
            r = np.arange(r0, lens_semidiameter, step)
            z = np.zeros_like(r)
            z[0] = z0
            for seg in range(surface_vars[surface_id]['num_of_segments'].get()):
                ROI_index = (r > r0) & (r <= surface_vars[surface_id][f'segment_{seg}']['params']['SemiDiameter'].get())
                r_ROI = r[ROI_index]
                
                type = surface_vars[surface_id][f'segment_{seg}']['type'].get()
                func = TYPE_TO_FUNCTION[type]
                params = {
                    param: surface_vars[surface_id][f'segment_{seg}']['params'][param].get()
                    for param in PARAMS[type]
                }
                z_ROI = func(r_ROI, params, z0)
                z[ROI_index] = z_ROI
                z0 = z_ROI[-1]
                r0 = surface_vars[surface_id][f'segment_{seg}']['params']['SemiDiameter'].get()
                surface_sag[i]['r'] = r
                surface_sag[i]['z'] = z
        
        segments = {
            'F_XZ': np.vstack([surface_sag[0]['r'][::-1], surface_sag[0]['z'][::-1]]).T,
            'B_XZ': np.vstack([surface_sag[1]['r'][::-1], surface_sag[1]['z'][::-1]]).T,
            'E_XZ': np.vstack([surface_sag[2]['r'], surface_sag[2]['z']]).T,
        }
        
        fig = plot_jfl_segments_with_arrows(segments)
        plt.axis('equal')
        plt.show()
        
        jfl_string = build_jfl_string(segments)
        json_string = json.dumps(params_dict, indent=4)
        
        # 保存JFL文件
        jfl_file = filedialog.asksaveasfilename(defaultextension=".JFL", filetypes=[("JFL files", "*.JFL")])
        if jfl_file:
            with open(jfl_file, 'w') as f:
                f.write(jfl_string)
        
        # 保存JSON文件
        json_file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if json_file:
            with open(json_file, 'w') as f:
                f.write(json_string)
    
    except Exception as e:
        messagebox.showerror("错误", str(e))

# 添加绘图和保存按钮
plot_button = ttk.Button(scrollable_frame, text="绘图并保存", command=plot_and_save)
plot_button.grid(row=2, column=0, padx=10, pady=10)

root.mainloop()