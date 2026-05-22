# HistoChemistry Image Mask Editor

A lightweight Python/Tkinter desktop tool for histochemistry and microscopy image annotation. The app detects dark pixels using thresholding, displays them as a red overlay, and allows manual multi-class line annotation using five user-selectable colors. It can export the edited overlay, a color-coded mask, and a combined binary mask.

This tool was originally designed for Black Gold and related histology/histochemistry images where dark staining needs to be highlighted, corrected, and separated from manually annotated structures.

## Features

- Load images using a file upload dialog or drag-and-drop.
- Detect dark pixels using an adjustable grayscale threshold.
- Apply an automatic threshold or use built-in Otsu-style auto-thresholding.
- Show the original image with a red overlay for automatically detected dark pixels.
- Open a second live mask window with a black background.
- Draw manual annotations using five line classes:
  - Type 1: Green
  - Type 2: Yellow
  - Type 3: Pink
  - Type 4: Blue
  - Type 5: Brown
- Edit annotations with mouse controls:
  - Left mouse drag: draw selected manual line type
  - Right mouse drag: erase automatic and manual masks
  - Ctrl + left mouse drag: erase alternative for some systems
  - Mouse wheel: change brush size
- Save outputs as PNG or TIFF.
- Export:
  - overlay image
  - color mask
  - combined binary mask

## Example Use Cases

- Black Gold staining image cleanup and mask preparation.
- Histochemistry image annotation.
- Manual correction of threshold-based segmentation.
- Multi-class line annotation for microscopy images.
- Preparing masks for downstream image analysis workflows.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/HistoChemistry-Image-Mask-Editor.git
cd HistoChemistry-Image-Mask-Editor
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If drag-and-drop does not work, make sure `tkinterdnd2` is installed:

```bash
pip install tkinterdnd2
```

The upload button will still work even if drag-and-drop is unavailable.

## Requirements

The core dependencies are:

```text
pillow
numpy
tkinterdnd2
```

Tkinter is included with most standard Python installations. On some Linux systems, it may need to be installed separately:

```bash
sudo apt-get install python3-tk
```

## Running the App

```bash
python blackgold_mask_editor.py
```

or, on some systems:

```bash
python3 blackgold_mask_editor.py
```

## How to Use

1. Start the program.
2. Load an image by clicking **Upload Image** or dragging an image into the main window.
3. Adjust the **Threshold** slider to select dark pixels.
4. Click **Apply Threshold** to update the automatic red mask.
5. Click **Auto Threshold** to estimate a threshold automatically.
6. Choose a manual line type from the radio buttons.
7. Draw on either the image panel or the mask panel:
   - Left mouse drag: draw the selected manual line type.
   - Right mouse drag: erase mask regions.
   - Mouse wheel: increase or decrease brush size.
8. Save outputs using:
   - **Save Overlay**
   - **Save Color Mask**
   - **Save Binary Mask**

## Output Files

### Overlay Image

The overlay image shows the original microscopy image with:

- automatic dark-pixel mask in red
- manual Type 1 line in green
- manual Type 2 line in yellow
- manual Type 3 line in pink
- manual Type 4 line in blue
- manual Type 5 line in brown

### Color Mask

The color mask uses a black background and the same class colors:

- red = automatically detected dark pixels
- green = manual Type 1
- yellow = manual Type 2
- pink = manual Type 3
- blue = manual Type 4
- brown = manual Type 5

Manual annotations overwrite automatic red pixels when they overlap.

### Combined Binary Mask

The binary mask combines the automatic red mask and all manual line classes into one black-and-white mask:

- white = selected/annotated region
- black = background

## Recommended Repository Structure

```text
HistoChemistry-Image-Mask-Editor/
├── blackgold_mask_editor.py
├── README.md
├── requirements.txt
├── LICENSE
└── .gitignore
```

## Suggested GitHub Description

```text
A Python/Tkinter tool for histochemistry image masking, dark-pixel thresholding, manual multi-class annotation, and color/binary mask export.
```

## Notes

- This is a research-support and annotation tool, not a clinical diagnostic tool.
- Thresholding results should be visually inspected and corrected manually when needed.
- For quantitative publication workflows, keep the same threshold and brush settings across comparable image groups whenever possible.
- Save original images separately and avoid overwriting raw microscopy data.

## License

This project is released under the MIT License. See the `LICENSE` file for details.

## Citation

If you use this tool in a research workflow, please cite the repository URL and version or commit hash used for analysis.

Example:

```text
HistoChemistry Image Mask Editor, version 1.0. GitHub repository: https://github.com/YOUR_USERNAME/HistoChemistry-Image-Mask-Editor
```

## Author

Developed by Intakhar Ahmad.

