# Project Master Context: Autosim Master Suite

## 1. Domain & Purpose
* **Industry:** Automotive Powertrain NVH Engineering (Jaguar Land Rover).
* **Core Application:** A multi-module PyQt6 desktop suite (`Autosim Master Suite`) for heavy simulation post-processing, automated plotting, and analytics.
* **Impact:** Minimizes manual engineering data handling, handles PCH parsing, CSV/Excel loading, dynamic charting, and RMS analytics.

## 2. Tech Stack & Architecture
* **Language:** Python 3
* **GUI Framework:** PyQt6 (`QMainWindow`, `QStackedWidget`, custom widgets, context menus).
* **Data & Math Libraries:** Pandas, NumPy, Matplotlib, OpenPyXL, mplcursors.
* **Main Script File:** `Autosim_PostProcessing_2026.10.04.py` (Single-file multi-studio architecture).

## 3. Core Modules inside the Script
1. **Global Exception Handler & Stylesheet:** Custom Dark/Light styling (`GLOBAL_STYLE`) and robust traceback catching.
2. **Module 1: Plotting Studio (`PlottingStudio`)**
   * Handles multi-file curve mapping, smart matching (`difflib`), interactive subplot rubberband zooming (`SubplotZoomManager`), hover tooltips (`mplcursors`), and RMS analytics.
3. **Module 2: Mobility Studio (`MobilityStudio`)**
   * Parses binary/text Nastran `.pch` files (Displacements & Velocities), extracts node IDs and translation/rotation components (X, Y, Z, Rx, Ry, Rz), and plots Mobility or Dynamic Stiffness curves with target overlays.
4. **Module 3: Gear & Bearings Studio (`GearBearingsStudio`)**
   * Tabbed interface for Forces & Moments, Transmission Error (Linear & Tilt TE), and Bearing Stiffness bar charts with custom color overrides and visibility toggling.
5. **Session Management:** Full JSON state saving and restoring across all 3 modules.

## 4. Coding & Collaboration Rules for AI
* **Always provide full, copy-pasteable code blocks** when updating or fixing scripts. Avoid code omissions or `# rest of code here` placeholders.
* Maintain clean PyQt6 layout structures, thread safety, and exception handling.
