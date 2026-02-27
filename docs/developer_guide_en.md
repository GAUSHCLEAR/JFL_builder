# Developer Guide

## Overview
This guide provides technical details on the underlying Python modules and project structure for developers maintaining or extending the JFL Generator tools.

## Core Modules

### 1. `sag_calculator.py`
This module contains the mathematical core for calculating surface profiles (sagittal depth or "sag").

*   **Key Functions**:
    *   `standard(r, params, z0)`: Computes sag for standard spherical/aspherical surfaces.
        *   Formula: $z = \frac{cr^2}{1+\sqrt{1-(1+k)c^2r^2}}$
        *   Handles base offset `z0`.
    *   `offset_circle(r, params, z0)`: Computes sag for an offset circle (often used for blending arcs).
        *   Formula involves a shift in the radial coordinate: $(r - r_0)^2$.
    *   `even_asphere(r, params, z0)`: Computes sag for an even-order asphere.
        *   Base conic + summation of polynomial terms ($A_2 r^2 + A_4 r^4 + \dots$).
    *   `line(r, params, z0)`: Linear interpolation between start and end points.
*   **Mappings**:
    *   `TYPE_TO_FUNCTION`: Maps string keys (e.g., 'Standard') to the corresponding function.
    *   `PARAMS`: Defines the required parameters for each surface type.

### 2. `parse_jfl.py`
This module handles input/output operations related to the proprietary JFL format and visualization.

*   **JFL Handling**:
    *   `build_jfl_string(segments)`: Converts the calculated point data into the formatted JFL string structure.
    *   `parse_jfl_file(file_path)`: Reads an existing JFL file and extracts segment data (useful for reverse engineering or validation).
*   **Visualization**:
    *   `plot_jfl_segments_with_arrows(segments)`: Uses `matplotlib` to generate 2D plots of the lens profile. It adds directional arrows to indicate the tool path or segment direction.

## Project Structure

*   `streamlit_app.py`: The main web interface (Streamlit).
*   `JFL_builder_GUI.py`: The desktop interface (Tkinter).
*   `OK5_*.html`: Standalone browser-based tools for rapid prototyping/visualizing Ortho-K lens designs.
*   `docs/`: Documentation (you are here).

## Extension Guide

### Adding a New Surface Type
1.  **Define the Math**: Implement a new sag function in `sag_calculator.py` (e.g., `toric_sag`).
2.  **Register**: Add the new type to `TYPE_TO_FUNCTION` and define its expected parameters in `PARAMS` within `sag_calculator.py`.
3.  **Update UI**:
    *   For `streamlit_app.py`, the dynamic parameter loop should automatically pick up the new params if they are in the dictionary.
    *   For `JFL_builder_GUI.py`, ensure the parameter generation logic handles any new specific fields (like list inputs for polynomial coefficients).

### Modifying the JFL Output Format
*   Edit `build_jfl_string` in `parse_jfl.py`.
*   Ensure header and footer constants match the target machine requirements.
