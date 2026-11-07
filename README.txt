# 🧊 CubeVision X

**An Accessible Computer Vision-Based Rubik's Cube Recognition and Solving Assistant for Individuals with Color Vision Deficiency**

CubeVision X is a desktop app that scans a Rubik's Cube through a webcam, identifies each sticker's color, and shows it as a **symbol, pattern, or color name** so users don't have to rely on hue alone. It then validates the scanned cube and guides the user to the solution step by step, with optional **voice assistance**.

This is the improved version of my final project in **CPE 018: Emerging Technologies in CpE 1**, Bachelor of Science in Computer Engineering, Technological Institute of the Philippines, Quezon City.

---

## 📸 Screenshots /

| Scanner | Accessibility modes | 
| ![Scanner](screenshots/scanner.png) | ![Accessibility](screenshots/accessibility.png) |

| GhostCube | CubeCoach |
|---|---|
| ![GhostCube](screenshots/ghostcube.png) | ![CubeCoach](screenshots/cubecoach.png) |

> Add your screenshots to a `screenshots/` folder using the file names above. A short demo video link can go here too.

---

## 🎯 Why This Project?

Color vision deficiency (CVD) is common. Red, orange, and green are easy to confuse, which makes a Rubik's Cube hard to read and hard to solve. Optical aids are not a dependable answer, so CubeVision X takes a software approach: it identifies the colors for the user and presents them in other forms, following the accessibility principle that color should not be the only way information is conveyed (WCAG 2.2).

**Goal:** make cube colors easier to identify and follow without relying on color perception.

**Who it's for:**
- People with color vision deficiency
- Beginners learning to solve the cube
- Educators and organizers running inclusive puzzle activities

## ✨ Features

- **Webcam scanner:** recognizes the six cube colors (white, yellow, red, orange, blue, green) with HSV color analysis, or imports a photo of a face.
- **Auto-filled 3×3 grid:** detected colors fill an editable grid automatically.
- **Manual correction and locking:** fix a wrong sticker and lock it so the live camera won't overwrite it.
- **Color-independent display modes:** Symbols, Patterns, Color Names, or Original Colors.
- **GhostCube:** a six-face digital net to review all 54 stickers before solving.
- **Cube validation:** checks for all six faces, 54 known stickers, nine of each color, distinct centers, and correct opposite centers before solving.
- **CubeCoach:** step-by-step solution moves in plain language (for example, "Turn right face clockwise 90 degrees"), with Previous, Next, and Speak Move controls. Solving runs in a background thread so the window stays responsive.
- **Voice assistance:** reads colors and moves aloud (optional, can be switched off).
- **Keyboard shortcuts:** single-key shortcuts for the main actions.
- **Progress tab and JSON export:** tracks scanned faces and exports the saved cube, solution moves, and display mode.

### Color labels

| Color | Symbol | Pattern |
|---|---|---|
| White | X | XXX |
| Yellow | * | *** |
| Red | A | === |
| Orange | + | +++ |
| Blue | # | \|\|\| |
| Green | O | /// |

### Keyboard shortcuts

| Key | Where | Action |
|---|---|---|
| `C` | Scanner | Capture / freeze the face |
| `S` | Scanner | Save the face |
| `V` | Scanner | Read the face aloud |
| `P` | CubeCoach | Previous move |
| `N` | CubeCoach | Next move |
| `M` | CubeCoach | Speak the current move |

## 🛠️ Tech Stack

| Purpose | Technology |
|---|---|
| Language | Python |
| GUI | PySide6 |
| Vision | OpenCV, NumPy |
| Color classification | HSV rule-based thresholds |
| Cube solving | rubik-solver-py |
| Voice | pyttsx3 |
| Evaluation | pandas, Matplotlib, scikit-learn, Google Colab |

## 🏗️ How It Works

```
Webcam / imported image
        ↓
Sample the center of each 3×3 cell → median BGR → HSV → color rules
        ↓
Editable grid (manual correction + lock) → save face (U R F D L B)
        ↓
GhostCube review → cube validation → 54-letter facelet string
        ↓
Solver (background thread) → step-by-step moves → voice / JSON export
```

Faces are scanned in the order **U, R, F, D, L, B**. The app shows an on-screen orientation guide for each face so the grid matches the cube net used by the solver.

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or newer
- A webcam (or use the image import)

## 📁 Project Structure

```
├── main.py               # Main window; combines all modules
├── shared.py             # Theme, constants, icons
├── widgets.py            # Custom UI widgets
├── ui_scanner.py         # Scanner tab
├── ui_accessibility.py   # Accessibility tab
├── ui_ghostcube.py       # GhostCube tab
├── ui_coach.py           # CubeCoach tab
├── ui_progress.py        # Progress tab
├── camera.py             # Webcam capture
├── face_manager.py       # Face saving and corrections
├── accessibility.py      # Names, symbols, patterns, voice
├── display.py            # Display modes
├── solver.py             # Validation and solving
├── solver_worker.py      # Background solving thread
├── project_data.py       # JSON export and reset
├── shortcuts.py          # Keyboard shortcuts
├── color_recognition.py  # HSV classifier and sticker sampling
├── face_analysis.py      # Imported-photo analysis
└── evaluation.py         # Accuracy, metrics, and graphs (Colab)
```

## ⚠️ Limitations

- The scanner uses a fixed center 3×3 grid, so the cube face must be positioned inside it.
- Recognition is affected by poor lighting, reflections, shadows, and camera quality. Red/orange and white/yellow are common confusions for HSV rules.
- Recognition is rule-based HSV classification, not a trained machine-learning model, and thresholds may need adjusting for a particular cube and camera.
- Perspective distortion is not corrected.
- GhostCube shows a flat six-face net, not an interactive 3D model.
- The app does not check whether the user physically performed each move.
- Recognition accuracy has not yet been established from a completed labeled evaluation, and the accessibility benefit has not yet been tested with users who have CVD.

## 🗺️ Roadmap

- [ ] Finish the labeled-image evaluation and report accuracy, precision, recall, and F1
- [ ] Perspective correction and automatic cube-face detection
- [ ] Per-session color calibration, or a trained classifier compared with the HSV rules
- [ ] Interactive 3D GhostCube
- [ ] Check that each physical move was performed correctly
- [ ] Usability study with participants who have color vision deficiency

## 🔒 Privacy

The exported JSON file contains only sticker colors, solution moves, and the display mode. It does not contain camera frames.

## 👤 Author

**George Albin M. Seda**
Computer Engineering student, Technological Institute of the Philippines, Quezon City
GitHub: [@geoseda](https://github.com/geoseda)

## 📚 References

- World Wide Web Consortium. (2023). *Web Content Accessibility Guidelines (WCAG) 2.2.* https://www.w3.org/TR/WCAG22/
- Dávalos-Carpio, J.-P., et al. (2025). *Rubik's cube solver robot with previous scanning using the HSV model.* LACCEI.
- Harris, C. R., et al. (2020). Array programming with NumPy. *Nature, 585*, 357–362.

## 📄 License

Developed for academic purposes. Add a license (for example MIT) if you want others to reuse the code.
