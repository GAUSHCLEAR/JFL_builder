# Streamlit App Documentation

## Overview
`streamlit_app.py` is a web-based application built with [Streamlit](https://streamlit.io/) for generating JFL (Job File Layout) files used in lathe processing for contact lenses. It provides an interactive interface for users to input lens parameters, visualize the lens geometry, and export the data.

## Features
*   **Axis-Symmetric JFL Generator**: Designed for creating JFL files for rotationally symmetric lenses.
*   **Interactive Input**: Users can define parameters for three surfaces: Front Surface, Back Surface, and Edge.
*   **Segmented Surface Definition**: Each surface can be composed of multiple segments, each defined by a specific surface type and parameters.
*   **Supported Surface Types**:
    *   `Standard`: Spherical and aspherical surfaces (Radius, Conic).
    *   `EvenAsphere`: Even-order aspheric surfaces (Radius, Conic, Asphere Terms).
    *   `OffsetCircle`: Offset spherical surfaces (Radius, Conic, Center).
    *   `Line`: Linear segments (End Z).
*   **Visualization**:
    *   Generates 2D cross-sectional plots of the lens segments.
    *   Visualizes direction arrows to indicate the processing path.
*   **Export**:
    *   **JFL File**: Generates and downloads the `.JFL` file for lathe machines.
    *   **JSON File**: Exports the design parameters as a `.json` file for saving and reloading configurations.

## Usage
1.  **Launch the App**: Run the script using streamlit:
    ```bash
    streamlit run streamlit_app.py
    ```
2.  **Input Lens Parameters**:
    *   Set the `Lens Center Thickness` and `Lens Processing Diameter`.
    *   Navigate through the tabs ("前表面", "后表面", "边缘") to define each surface.
    *   Set the starting X and Z coordinates for each surface.
    *   Define the number of segments for each surface.
3.  **Define Segments**:
    *   For each segment, select the `Surface Type` (Standard, EvenAsphere, OffsetCircle, Line).
    *   Input the specific parameters for the selected type (e.g., Radius, Conic, Semi-Diameter).
    *   *Note*: The semi-diameter determines the radial extent of the segment.
4.  **Visualize**: The plot automatically updates as you modify parameters (or upon valid input completion).
5.  **Download**:
    *   Click "下载JFL文件" to get the machine-readable JFL file.
    *   Click "下载参数JSON文件" to save your design.

## Code Structure
*   **Imports**: Uses `streamlit`, `numpy`, `matplotlib`, `parse_jfl`, and `sag_calculator`.
*   **Configuration**: Sets page layout to wide.
*   **Input Section**: Uses `st.columns`, `st.tabs`, and `st.expander` to organize inputs.
*   **Sag Calculation**: Iterates through surfaces and segments, calling functions from `sag_calculator.py` (`TYPE_TO_FUNCTION`) to compute Z-coordinates based on radial (r) inputs.
*   **Plotting**: Uses `plot_jfl_segments_with_arrows` from `parse_jfl.py` to visualize the geometry.
*   **Export Logic**:
    *   Constructs the JFL string using `build_jfl_string`.
    *   Constructs a JSON dictionary and serializes it for the JSON download.

## Dependencies
*   `streamlit`
*   `numpy`
*   `matplotlib`
*   `parse_jfl.py` (Local module)
*   `sag_calculator.py` (Local module)
