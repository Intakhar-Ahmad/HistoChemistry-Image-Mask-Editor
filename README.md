# HistoChemistry Image Mask Editor

HistoChemistry Image Mask Editor is a Python desktop tool for image masking, dark pixel detection, manual annotation, and mask export. It is designed for histology, histochemistry, microscopy, and other image analysis workflows where users need a simple graphical interface to identify dark image regions and manually add multiple annotation classes.

The tool uses a Tkinter interface and supports image upload, optional drag and drop loading, threshold based dark pixel detection, manual brush editing, and export of overlay, color mask, and binary mask images.

## Features

* Load images using an upload button
* Load images by drag and drop when tkinterdnd2 is installed
* Detect dark pixels using an adjustable threshold
* Display automatically detected dark pixels in red
* Edit annotations manually with mouse based drawing and erasing
* Use five manual annotation types with different colors
* Adjust brush size using a slider or mouse wheel
* View the original overlay and color mask in separate windows
* Export the edited overlay image
* Export a color mask image with black background
* Export a combined binary mask

## Annotation colors

Automatic dark pixel mask: red

Manual Type 1: green

Manual Type 2: yellow

Manual Type 3: pink

Manual Type 4: blue

Manual Type 5: brown

## Mouse controls

Draw selected annotation type: left mouse drag

Erase annotation: right mouse drag

Alternative erase on Mac: Ctrl plus left mouse drag

Change brush size: mouse wheel

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/HistoChemistry-Image-Mask-Editor.git
cd HistoChemistry-Image-Mask-Editor
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Required Python packages:

```text
pillow
numpy
tkinterdnd2
```

Tkinter is included with most standard Python installations. If Tkinter is missing, install it using your operating system package manager.

## Running the tool

Run the main Python file:

```bash
python histochemistry_image_mask_editor.py
```

## Basic workflow

1. Open the program.
2. Click Upload Image or drag and drop an image into the window.
3. Adjust the threshold slider to detect dark pixels.
4. Click Apply Threshold or Auto Threshold.
5. Select one of the manual line types.
6. Draw using the left mouse button.
7. Erase unwanted areas using the right mouse button.
8. Save the overlay, color mask, or binary mask.

## Output files

### Overlay image

The overlay image shows the original image with colored annotations applied on top.

### Color mask

The color mask uses a black background. The automatic dark pixel mask is red, and manual annotation types are shown in green, yellow, pink, blue, and brown.

### Binary mask

The binary mask combines all detected and manually drawn regions into a single white mask on a black background.

## Supported image formats

* JPG
* JPEG
* PNG
* TIF
* TIFF
* BMP

## Suggested use cases

* Histochemistry image annotation
* Histology image masking
* Microscopy image preprocessing
* Manual correction of threshold based segmentation
* Creating color coded annotation masks
* Preparing masks for downstream image analysis

## Notes

Drag and drop requires the tkinterdnd2 package. If this package is not installed, the upload button will still work.

Threshold based detection is intended as a simple first pass masking method. Manual correction should be used when image background, staining intensity, or tissue artifacts affect automatic detection.

## Citation

If you use this tool in academic work, please cite the GitHub repository.

Suggested citation:

```text
Ahmad, I. HistoChemistry Image Mask Editor: A Python Tkinter tool for threshold based image masking and manual multi class annotation. GitHub repository.
```

## License

This project is released under the MIT License.
