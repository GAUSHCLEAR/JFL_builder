# JFL Builder GUI Documentation

## Overview
`JFL_builder_GUI.py` is a desktop application built with Python's `tkinter` library. It serves as a graphical interface for designing axis-symmetric contact lenses and generating the corresponding JFL files. Unlike the Streamlit app, this is a standalone GUI application.

## Features
*   **Desktop GUI Interface**: Built using `tkinter` and `ttk` for a native desktop feel.
*   **Lens Parameter Input**:
    *   Allows configuration of lens center thickness and processing diameter.
    *   Dynamic update of the lens semi-diameter based on the input diameter.
*   **Multi-Surface Design**:
    *   Tabbed interface to manage `Front Surface`, `Back Surface`, and `Edge` parameters independently.
    *   Configurable starting coordinates (X, Z) for each surface.
    *   Support for multiple segments per surface.
*   **Dynamic Segment Management**:
    *   Users can specify the number of segments.
    *   The UI dynamically updates to show parameter fields for each segment.
*   **Surface Types**: Supports `Standard`, `EvenAsphere`, `OffsetCircle`, and `Line`.
*   **Real-time Visualization**: Embeds a `matplotlib` figure directly into the `tkinter` window to show the lens profile.
*   **File Operations**:
    *   **Generate and Plot**: Buttons to trigger calculation and rendering.
    *   **Download JFL**: Saves the design as a `.JFL` file.
    *   **Download JSON**: Saves the design parameters as a `.json` file.

## Usage
1.  **Launch the Application**:
    ```bash
    python JFL_builder_GUI.py
    ```
2.  **Configure Lens**: Enter the `Lens Center Thickness` and `Processing Diameter` in the top-left section.
3.  **Design Surfaces**:
    *   Select a tab (e.g., "前表面").
    *   Enter Start X/Z coordinates.
    *   Set the `Number of Segments`.
    *   For each segment that appears, choose the `Surface Type` and fill in the required parameters (Radius, Conic, Semi-Diameter, etc.).
4.  **Visualize**: Click the "生成并绘图" (Generate and Plot) button. The lens profile will appear in the right-hand panel.
5.  **Save**:
    *   Use "下载JFL文件" to export the manufacturing file.
    *   Use "下载参数JSON文件" to save the configuration.

## Code Structure
*   **`LensGeneratorApp` Class**: The main class inheriting from `tk.Tk`.
    *   `__init__`: Sets up the main window and initializes variables.
    *   `create_widgets`: Layouts the left (input) and right (plot) frames.
    *   `create_input_frame`: Populates the input fields and notebook tabs.
    *   `create_surface_tab`: Creates tabs for each surface.
    *   `update_segments`: Dynamically adds/removes segment input frames based on the user's count.
    *   `generate_and_plot`: Reads all inputs, performs the sag calculations (using internal placeholder logic or imported functions), and updates the matplotlib canvas.
*   **Helper Functions**:
    *   Includes placeholder implementations for sag calculations (`standard_sag`, etc.) if external modules aren't used, though it mimics the logic found in `sag_calculator.py`.
    *   `plot_jfl_segments_with_arrows`: Handles the matplotlib plotting logic.

## Dependencies
*   `tkinter` (Standard Python library)
*   `numpy`
*   `matplotlib`
