import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

# Placeholder constants and functions (Replace these with your actual implementations)
PARAMS = {
    'Standard': ['Radius', 'Conic', 'SemiDiameter'],
    'EvenAsphere': ['Radius', 'Conic', 'AsphereTerm', 'AsphereParams', 'SemiDiameter'],
    'OffsetCircle': ['Radius', 'OffsetX', 'OffsetZ', 'SemiDiameter'],
    'Line': ['EndZ', 'SemiDiameter'],
}

def standard_sag(r, params, z0):
    Radius = params['Radius']
    Conic = params['Conic']
    return z0 + (r**2) / (Radius * (1 + np.sqrt(1 - (1 + Conic) * (r/Radius)**2)))

def even_asphere_sag(r, params, z0):
    Radius = params['Radius']
    Conic = params['Conic']
    AsphereParams = params['AsphereParams']
    z = standard_sag(r, {'Radius': Radius, 'Conic': Conic}, z0)
    for i, A in enumerate(AsphereParams):
        z += A * r**(2*(i+2))
    return z

def offset_circle_sag(r, params, z0):
    return z0 + np.sqrt(params['Radius']**2 - (r - params['OffsetX'])**2) + params['OffsetZ']

def line_sag(r, params, z0):
    return np.linspace(z0, params['EndZ'], len(r))

TYPE_TO_FUNCTION = {
    'Standard': standard_sag,
    'EvenAsphere': even_asphere_sag,
    'OffsetCircle': offset_circle_sag,
    'Line': line_sag,
}

def plot_jfl_segments_with_arrows(segments):
    fig, ax = plt.subplots(figsize=(8, 6))
    for key, data in segments.items():
        ax.plot(data[:, 0], data[:, 1], label=key)
    ax.legend()
    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    ax.set_title('JFL Segments')
    ax.grid(True)
    return fig

def build_jfl_string(segments):
    jfl_string = "JFL Data\n"
    for key, data in segments.items():
        jfl_string += f"{key}\n"
        for point in data:
            jfl_string += f"{point[0]:.6f} {point[1]:.6f}\n"
        jfl_string += "END\n"
    return jfl_string

# Main application class
class LensGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("轴对称 JFL 生成器")
        self.geometry("1200x800")
        self.step = 0.0025
        self.format = "%.3f"
        self.lens_semidiameter = 5.3  # Default value, will be updated
        self.surface_id_list = ['前表面', '后表面', '边缘']
        self.surface_tabs = {}
        self.surface_data = {}
        self.create_widgets()

    def create_widgets(self):
        # Create main frames
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left frame components
        self.create_input_frame()

        # Right frame components
        self.figure = plt.Figure(figsize=(6, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_input_frame(self):
        # Create a canvas with scrollbar for the left frame
        canvas = tk.Canvas(self.left_frame)
        scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=canvas.yview)
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

        # Lens parameters
        lens_params_frame = ttk.LabelFrame(scrollable_frame, text="输入镜片参数")
        lens_params_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(lens_params_frame, text="镜片中心厚度").grid(row=0, column=0, sticky=tk.W)
        self.lens_thickness_var = tk.DoubleVar(value=0.2)
        ttk.Entry(lens_params_frame, textvariable=self.lens_thickness_var).grid(row=0, column=1)

        ttk.Label(lens_params_frame, text="镜片加工直径").grid(row=1, column=0, sticky=tk.W)
        self.lens_diameter_var = tk.DoubleVar(value=10.6)
        ttk.Entry(lens_params_frame, textvariable=self.lens_diameter_var).grid(row=1, column=1)

        # Update semidiameter when diameter changes
        self.lens_diameter_var.trace('w', self.update_semidiameter)

        # Surface tabs
        self.surface_notebook = ttk.Notebook(scrollable_frame)
        self.surface_notebook.pack(fill=tk.BOTH, expand=True)

        for surface_id in self.surface_id_list:
            self.create_surface_tab(surface_id)

        # Buttons
        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(buttons_frame, text="生成并绘图", command=self.generate_and_plot).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="下载JFL文件", command=self.download_jfl).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="下载参数JSON文件", command=self.download_json).pack(side=tk.LEFT, padx=5)

    def update_semidiameter(self, *args):
        self.lens_semidiameter = self.lens_diameter_var.get() / 2
        # Update any semidiameter fields if necessary

    def create_surface_tab(self, surface_id):
        tab = ttk.Frame(self.surface_notebook)
        self.surface_notebook.add(tab, text=surface_id)
        self.surface_tabs[surface_id] = tab
        self.surface_data[surface_id] = {}
        self.populate_surface_tab(surface_id, tab)

    def populate_surface_tab(self, surface_id, tab):
        # Starting points
        ttk.Label(tab, text=f"{surface_id}起始点 X坐标").grid(row=0, column=0, sticky=tk.W)
        start_x = tk.DoubleVar(value=0.0 if surface_id != '边缘' else self.lens_semidiameter - 1.0)
        ttk.Entry(tab, textvariable=start_x).grid(row=0, column=1)
        self.surface_data[surface_id]['start_x'] = start_x

        ttk.Label(tab, text=f"{surface_id}起始点 Z坐标").grid(row=1, column=0, sticky=tk.W)
        default_z = {"前表面": 0.0, "后表面": self.lens_thickness_var.get(), "边缘": 3.0}[surface_id]
        start_z = tk.DoubleVar(value=default_z)
        ttk.Entry(tab, textvariable=start_z).grid(row=1, column=1)
        self.surface_data[surface_id]['start_z'] = start_z

        # Number of segments
        ttk.Label(tab, text=f"{surface_id}弧段数").grid(row=2, column=0, sticky=tk.W)
        num_segments = tk.IntVar(value=1)
        ttk.Entry(tab, textvariable=num_segments).grid(row=2, column=1)
        self.surface_data[surface_id]['num_segments'] = num_segments

        # Segments frame
        segments_frame = ttk.Frame(tab)
        segments_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W)
        self.surface_data[surface_id]['segments_frame'] = segments_frame
        self.surface_data[surface_id]['segments_widgets'] = []

        # Update segments when num_segments changes
        num_segments.trace('w', lambda *args, sid=surface_id: self.update_segments(sid))

        # Initialize segments
        self.update_segments(surface_id)

    def update_segments(self, surface_id):
        # Clear existing widgets
        for widget in self.surface_data[surface_id]['segments_widgets']:
            widget.destroy()
        self.surface_data[surface_id]['segments_widgets'].clear()

        num_segments = self.surface_data[surface_id]['num_segments'].get()
        segments_frame = self.surface_data[surface_id]['segments_frame']

        for seg_index in range(num_segments):
            segment_frame = ttk.LabelFrame(segments_frame, text=f"第{seg_index + 1}弧段")
            segment_frame.pack(fill=tk.X, padx=5, pady=5)
            self.surface_data[surface_id]['segments_widgets'].append(segment_frame)
            self.create_segment_widgets(surface_id, seg_index, segment_frame)

    def create_segment_widgets(self, surface_id, seg_index, frame):
        # Surface type
        ttk.Label(frame, text="面型").grid(row=0, column=0, sticky=tk.W)
        surface_type = tk.StringVar(value='Standard')
        type_options = ['Standard', 'EvenAsphere', 'OffsetCircle', 'Line']
        ttk.OptionMenu(frame, surface_type, 'Standard', *type_options,
                       command=lambda *args, sid=surface_id, si=seg_index: self.update_segment_params(sid, si)).grid(row=0, column=1)
        self.surface_data[surface_id].setdefault('segments', []).append({'type': surface_type})

        # Parameters frame
        params_frame = ttk.Frame(frame)
        params_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        self.surface_data[surface_id]['segments'][seg_index]['params_frame'] = params_frame
        self.surface_data[surface_id]['segments'][seg_index]['params_vars'] = {}

        # Initialize parameters
        self.update_segment_params(surface_id, seg_index)

    def update_segment_params(self, surface_id, seg_index):
        segment = self.surface_data[surface_id]['segments'][seg_index]
        params_frame = segment['params_frame']

        # Clear existing parameter widgets
        for widget in params_frame.winfo_children():
            widget.destroy()
        segment['params_vars'].clear()

        surface_type = segment['type'].get()
        params = PARAMS[surface_type]

        for param in params:
            ttk.Label(params_frame, text=param).pack(side=tk.TOP, anchor=tk.W)
            if param == 'AsphereParams':
                asphere_term = segment['params_vars'].get('AsphereTerm', tk.IntVar(value=1))
                self.create_asphere_params(params_frame, segment, asphere_term.get())
            elif param == 'AsphereTerm':
                param_var = tk.IntVar(value=1)
                ttk.Entry(params_frame, textvariable=param_var).pack(side=tk.TOP, fill=tk.X)
                param_var.trace('w', lambda *args, sid=surface_id, si=seg_index: self.update_asphere_params(sid, si))
                segment['params_vars'][param] = param_var
            else:
                param_var = tk.DoubleVar(value=0.0)
                ttk.Entry(params_frame, textvariable=param_var).pack(side=tk.TOP, fill=tk.X)
                segment['params_vars'][param] = param_var

        # Trigger plot update
        self.generate_and_plot()

    def create_asphere_params(self, params_frame, segment, asphere_term):
        asphere_frame = ttk.Frame(params_frame)
        asphere_frame.pack(side=tk.TOP, fill=tk.X)
        segment['params_vars']['AsphereParams'] = []
        for i in range(asphere_term):
            ttk.Label(asphere_frame, text=f"A{(i + 1) * 2}").grid(row=i, column=0, sticky=tk.W)
            param_var = tk.DoubleVar(value=0.0)
            ttk.Entry(asphere_frame, textvariable=param_var).grid(row=i, column=1, sticky=tk.W)
            segment['params_vars']['AsphereParams'].append(param_var)

    def update_asphere_params(self, surface_id, seg_index):
        segment = self.surface_data[surface_id]['segments'][seg_index]
        params_frame = segment['params_frame']
        asphere_term = segment['params_vars']['AsphereTerm'].get()
        self.create_asphere_params(params_frame, segment, asphere_term)
        self.generate_and_plot()


    def generate_and_plot(self):
        try:
            lens_semidiameter = self.lens_diameter_var.get() / 2
            surface_sag = [{} for _ in range(len(self.surface_id_list))]
            for i, surface_id in enumerate(self.surface_id_list):
                start_x = self.surface_data[surface_id]['start_x'].get()
                start_z = self.surface_data[surface_id]['start_z'].get()
                num_segments = self.surface_data[surface_id]['num_segments'].get()

                r0 = start_x
                z0 = start_z
                r = np.arange(r0, lens_semidiameter, self.step)
                z = np.zeros_like(r)
                z[0] = z0

                for seg_index in range(num_segments):
                    segment = self.surface_data[surface_id]['segments'][seg_index]
                    surface_type = segment['type'].get()
                    params_vars = segment['params_vars']
                    params = {param: var.get() if not isinstance(var, list) else [v.get() for v in var]
                              for param, var in params_vars.items()}

                    func = TYPE_TO_FUNCTION[surface_type]

                    ROI_index = (r > r0) & (r <= params['SemiDiameter'])
                    r_ROI = r[ROI_index]
                    if len(r_ROI) == 0:
                        continue

                    z_ROI = func(r_ROI, params, z0)
                    z[ROI_index] = z_ROI
                    z0 = z_ROI[-1]
                    r0 = params['SemiDiameter']
                    surface_sag[i]['r'] = r
                    surface_sag[i]['z'] = z

            # Prepare segments for plotting
            segments = {
                'F_XZ': np.vstack([surface_sag[0]['r'][::-1], surface_sag[0]['z'][::-1]]).T,
                'B_XZ': np.vstack([surface_sag[1]['r'][::-1], surface_sag[1]['z'][::-1]]).T,
                'E_XZ': np.vstack([surface_sag[2]['r'], surface_sag[2]['z']]).T,
            }

            # Plotting
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            for key, data in segments.items():
                ax.plot(data[:, 0], data[:, 1], label=key)
            ax.legend()
            ax.set_xlabel('X')
            ax.set_ylabel('Z')
            ax.set_title('JFL Segments')
            ax.grid(True)
            ax.axis('equal')
            self.canvas.draw()

            # Store segments for file saving
            self.segments = segments

        except Exception as e:
            messagebox.showerror("错误", f"生成图表时出错：{str(e)}")

    def download_jfl(self):
        if not hasattr(self, 'segments'):
            messagebox.showwarning("提示", "请先生成并绘图。")
            return
        jfl_string = build_jfl_string(self.segments)
        file_path = filedialog.asksaveasfilename(defaultextension=".JFL", filetypes=[("JFL files", "*.JFL")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(jfl_string)
            messagebox.showinfo("提示", "JFL文件已保存。")

    def download_json(self):
        params_dict = {}
        params_dict["lens"] = {
            "lens_thickness": self.lens_thickness_var.get(),
            "lens_diameter": self.lens_diameter_var.get(),
            "lens_semidiameter": self.lens_diameter_var.get() / 2
        }
        for surface_id in self.surface_id_list:
            params_dict[surface_id] = {
                "start_point_x": self.surface_data[surface_id]['start_x'].get(),
                "start_point_z": self.surface_data[surface_id]['start_z'].get(),
                "num_of_segments": self.surface_data[surface_id]['num_segments'].get(),
                "segments": []
            }
            for seg_index in range(self.surface_data[surface_id]['num_segments'].get()):
                segment = self.surface_data[surface_id]['segments'][seg_index]
                surface_type = segment['type'].get()
                params_vars = segment['params_vars']
                params = {param: var.get() if not isinstance(var, list) else [v.get() for v in var]
                          for param, var in params_vars.items()}
                params_dict[surface_id]["segments"].append({
                    "type": surface_type,
                    "params": params
                })

        json_string = json.dumps(params_dict, indent=4)
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(json_string)
            messagebox.showinfo("提示", "参数JSON文件已保存。")

if __name__ == "__main__":
    app = LensGeneratorApp()
    app.mainloop()