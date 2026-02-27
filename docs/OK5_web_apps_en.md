# OK5 Web Tools Documentation

## Overview
The OK5 Web Tools are a suite of HTML/JavaScript-based applications for designing Orthokeratology (Ortho-K) and RGP lenses. These tools run directly in the browser and provide specialized interfaces for different aspects of lens design.

## Tools Summary

### 1. `OK5_intergrated.html` (Main Tool)
This is the most comprehensive version, integrating design calculations, formula locking, and advanced visualization.

*   **Key Features**:
    *   **Comprehensive Input Grid**: Parameters for FlatK, ecc, TP, Jessen, BOD, lensD, RCwidth, and edgeLift.
    *   **Formula-Driven Design**:
        *   **Curvature Formulas**: Editable formulas for BC, AC1, AC2, RC, and PC curves using `math.js`.
        *   **Diameter Formulas**: Editable formulas for calculating the end diameters of each zone.
    *   **Locking Mechanisms**:
        *   `Lock Formula`: Forces curvature radii to follow the calculated formula values.
        *   `Lock AC2R`: Maintains a fixed difference between AC2R and AC1R.
        *   `Lock Seg Formula`: Forces segment diameters to follow the formulas.
    *   **Dual Display Modes**: Toggle between Radius (mm) and Curvature (Diopters).
    *   **Advanced Visualization**:
        *   **Fluorescein Plot**: Simulates the fluo pattern based on tear film thickness.
        *   **Tear Film Plot**: Shows the tear film profile.
        *   **Sag Plot**: Displays the lens and cornea sag profiles.
    *   **Import/Export**: Save and load lens designs via CSV.

### 2. `OK5_design.html` & `OK5_design_DK.html`
These are specialized variations focused on specific design paradigms. `OK5_design_DK.html` likely includes specific tweaks or features related to "DK" (Defocus/Dual curve?) parameters or specific design logic variations.

*   **Common Features**:
    *   Input fields for standard lens parameters.
    *   Radio buttons for selecting calculation methods (e.g., Numerical vs. Simple for RCR).
    *   Visualization canvases for Fluorescein, Tear, and Combined plots.

### 3. `OK5_tutorial.html`
A simplified version aimed at educational purposes or basic parameter calculation without the complex visualization overhead of the integrated tool.

## Technical Details (OK5_intergrated.html)

### Libraries
*   **Math.js**: Used for safe and flexible parsing of user-defined formulas for curvatures and diameters.

### Key Logic
1.  **Input Collection**: Reads all numerical inputs from the DOM.
2.  **Formula Evaluation**:
    *   Parses strings from formula inputs.
    *   Evaluates them against the current input parameters (FlatK, ecc, etc.).
    *   Updates internal data attributes (`dataset.backend`) to store precise values.
3.  **Sag Calculation**:
    *   Uses the standard aspheric sag equation:
        $$Z(x) = \frac{x^2}{R(1+\sqrt{1-(1+k)\frac{x^2}{R^2}})}$$
    *   Calculates sag for the cornea and the multi-zone lens.
    *   Computes tear film thickness as the difference between cornea and lens sag.
4.  **Rendering**:
    *   Canvas API is used to draw the profiles and the simulated fluorescein pattern.
    *   The fluorescein pattern uses a Beer-Lambert-based color mapping model to simulate intensity based on tear thickness.

## Usage Guide (Integrated Tool)
1.  **Open the HTML file** in a modern web browser.
2.  **Set Base Parameters**: Enter values for `FlatK`, `ecc`, `TP`, etc.
3.  **Edit Formulas** (Optional): Modify the math expressions for curves or diameters if custom logic is needed.
4.  **Review Results**: Check the calculated radii and diameters in the results grid.
5.  **Analyze Plots**: Use the three plots on the right to verify the fit (Sag, Tear Layer, Fluorescein).
6.  **Export**: Use the "Export Config" button to save your work.
