"""
HistoChemistry Image Mask Editor

A small Tkinter desktop application for threshold based image masking,
manual multi class annotation, and export of overlay, color mask, and
binary mask images.

Author: Intakhar Ahmad
License: MIT
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import numpy as np

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


class HistoChemistryImageMaskEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("HistoChemistry Image Mask Editor")
        self.root.geometry("1250x820")

        self.original_image = None
        self.overlay_image = None
        self.red_mask_image = None
        self.manual_masks = {}

        self.line_colors = {
            "type1": ("Type 1: Green",  [0, 255, 0]),
            "type2": ("Type 2: Yellow", [255, 255, 0]),
            "type3": ("Type 3: Pink",   [255, 0, 255]),
            "type4": ("Type 4: Blue",   [0, 0, 255]),
            "type5": ("Type 5: Brown",  [150, 75, 0]),
        }

        self.main_preview = None
        self.mask_preview = None

        self.main_scale = 1.0
        self.main_offset = (0, 0)

        self.mask_scale = 1.0
        self.mask_offset = (0, 0)

        self.last_main_point = None
        self.last_mask_point = None

        self.threshold_var = tk.IntVar(value=80)
        self.alpha_var = tk.DoubleVar(value=1.0)
        self.brush_size_var = tk.IntVar(value=25)
        self.manual_type_var = tk.StringVar(value="type1")

        self.create_main_widgets()
        self.create_mask_window()
        self.setup_drag_and_drop()

    def create_main_widgets(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)

        tk.Button(control_frame, text="Upload Image", command=self.upload_image, width=15).pack(side=tk.LEFT, padx=4)
        tk.Button(control_frame, text="Auto Threshold", command=self.auto_threshold, width=15).pack(side=tk.LEFT, padx=4)
        tk.Button(control_frame, text="Apply Threshold", command=self.apply_threshold, width=15).pack(side=tk.LEFT, padx=4)
        tk.Button(control_frame, text="Clear Selected", command=self.clear_selected_type, width=15).pack(side=tk.LEFT, padx=4)
        tk.Button(control_frame, text="Clear All Manual", command=self.clear_all_manual, width=16).pack(side=tk.LEFT, padx=4)
        tk.Button(control_frame, text="Save Overlay", command=self.save_overlay, width=14).pack(side=tk.LEFT, padx=4)
        tk.Button(control_frame, text="Save Color Mask", command=self.save_color_mask, width=15).pack(side=tk.LEFT, padx=4)
        tk.Button(control_frame, text="Save Binary Mask", command=self.save_combined_mask, width=15).pack(side=tk.LEFT, padx=4)

        settings_frame = tk.Frame(self.root)
        settings_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        tk.Label(settings_frame, text="Threshold").pack(side=tk.LEFT)

        tk.Scale(
            settings_frame,
            from_=0,
            to=255,
            orient=tk.HORIZONTAL,
            variable=self.threshold_var,
            length=190
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(settings_frame, text="Overlay intensity").pack(side=tk.LEFT, padx=(15, 0))

        tk.Scale(
            settings_frame,
            from_=0.1,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.alpha_var,
            command=lambda x: self.refresh_all(),
            length=140
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(settings_frame, text="Brush size").pack(side=tk.LEFT, padx=(15, 0))

        tk.Scale(
            settings_frame,
            from_=1,
            to=150,
            orient=tk.HORIZONTAL,
            variable=self.brush_size_var,
            length=160
        ).pack(side=tk.LEFT, padx=5)

        type_frame = tk.Frame(self.root)
        type_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        tk.Label(type_frame, text="Manual line type:").pack(side=tk.LEFT)

        for key, (label, color) in self.line_colors.items():
            tk.Radiobutton(
                type_frame,
                text=label,
                variable=self.manual_type_var,
                value=key,
                command=self.update_info_label
            ).pack(side=tk.LEFT, padx=8)

        self.info_label = tk.Label(
            self.root,
            text="Upload or drag-and-drop image. LEFT drag = draw selected type | RIGHT drag = erase | Mouse wheel = brush size",
            anchor="w"
        )
        self.info_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.main_canvas = tk.Canvas(self.root, bg="gray")
        self.main_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.bind_mouse_controls(self.main_canvas, panel="main")
        self.main_canvas.bind("<Configure>", lambda event: self.refresh_all())

    def create_mask_window(self):
        self.mask_window = tk.Toplevel(self.root)
        self.mask_window.title("Color Mask Window")
        self.mask_window.geometry("950x680")

        label = tk.Label(
            self.mask_window,
            text="Color mask: black background; red = auto dark pixels; green/yellow/pink/blue/brown = manual types.",
            anchor="w"
        )
        label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.mask_canvas = tk.Canvas(self.mask_window, bg="black")
        self.mask_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.bind_mouse_controls(self.mask_canvas, panel="mask")
        self.mask_canvas.bind("<Configure>", lambda event: self.refresh_all())

    def setup_drag_and_drop(self):
        if not DND_AVAILABLE:
            self.info_label.config(
                text="Drag-and-drop unavailable. Install with: pip install tkinterdnd2. Upload button still works."
            )
            return

        for widget in [self.root, self.main_canvas, self.mask_window, self.mask_canvas]:
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self.handle_drop)

    def handle_drop(self, event):
        try:
            dropped_files = self.root.tk.splitlist(event.data)

            if not dropped_files:
                return

            file_path = dropped_files[0]

            if os.path.isfile(file_path):
                self.load_image_from_path(file_path)
            else:
                messagebox.showwarning("Invalid file", "Please drop a valid image file.")

        except Exception as e:
            messagebox.showerror("Drag-and-drop error", str(e))

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="Select image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.tif *.tiff *.bmp"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.load_image_from_path(file_path)

    def load_image_from_path(self, file_path):
        try:
            self.original_image = Image.open(file_path).convert("RGB")
        except Exception as e:
            messagebox.showerror("Image error", f"Could not open image:\n{e}")
            return

        width, height = self.original_image.size

        self.manual_masks = {
            key: Image.new("L", (width, height), 0)
            for key in self.line_colors.keys()
        }

        self.apply_threshold()

    def bind_mouse_controls(self, canvas, panel):
        # Left mouse = draw selected manual line type
        canvas.bind("<ButtonPress-1>", lambda event: self.start_paint(event, panel, mode="draw"))
        canvas.bind("<B1-Motion>", lambda event: self.paint_drag(event, panel, mode="draw"))
        canvas.bind("<ButtonRelease-1>", lambda event: self.stop_paint(panel))

        # Right mouse = erase all masks under brush
        canvas.bind("<ButtonPress-3>", lambda event: self.start_paint(event, panel, mode="erase"))
        canvas.bind("<B3-Motion>", lambda event: self.paint_drag(event, panel, mode="erase"))
        canvas.bind("<ButtonRelease-3>", lambda event: self.stop_paint(panel))

        # Mac alternative: Ctrl + left mouse = erase
        canvas.bind("<Control-ButtonPress-1>", lambda event: self.start_paint(event, panel, mode="erase"))
        canvas.bind("<Control-B1-Motion>", lambda event: self.paint_drag(event, panel, mode="erase"))
        canvas.bind("<Control-ButtonRelease-1>", lambda event: self.stop_paint(panel))

        # Mouse wheel = brush size
        canvas.bind("<MouseWheel>", self.change_brush_size)
        canvas.bind("<Button-4>", self.change_brush_size)
        canvas.bind("<Button-5>", self.change_brush_size)

    def change_brush_size(self, event):
        current_size = self.brush_size_var.get()

        event_num = getattr(event, "num", None)
        event_delta = getattr(event, "delta", 0)

        if event_num == 4 or event_delta > 0:
            new_size = current_size + 2
        else:
            new_size = current_size - 2

        self.brush_size_var.set(max(1, min(150, new_size)))
        self.update_info_label()

    def apply_threshold(self):
        if self.original_image is None:
            messagebox.showwarning("No image", "Please upload or drop an image first.")
            return

        gray = np.array(self.original_image.convert("L"))
        threshold = self.threshold_var.get()

        red_mask_array = np.zeros_like(gray, dtype=np.uint8)
        red_mask_array[gray <= threshold] = 255

        self.red_mask_image = Image.fromarray(red_mask_array, mode="L")

        width, height = self.original_image.size

        for key in self.line_colors.keys():
            if key not in self.manual_masks:
                self.manual_masks[key] = Image.new("L", (width, height), 0)

        self.refresh_all()

    def auto_threshold(self):
        if self.original_image is None:
            messagebox.showwarning("No image", "Please upload or drop an image first.")
            return

        gray = np.array(self.original_image.convert("L"))
        hist, _ = np.histogram(gray.flatten(), bins=256, range=(0, 256))

        total = gray.size
        sum_total = np.dot(np.arange(256), hist)

        sum_background = 0
        weight_background = 0
        max_variance = 0
        threshold = 0

        for i in range(256):
            weight_background += hist[i]

            if weight_background == 0:
                continue

            weight_foreground = total - weight_background

            if weight_foreground == 0:
                break

            sum_background += i * hist[i]

            mean_background = sum_background / weight_background
            mean_foreground = (sum_total - sum_background) / weight_foreground

            variance = weight_background * weight_foreground * (mean_background - mean_foreground) ** 2

            if variance > max_variance:
                max_variance = variance
                threshold = i

        self.threshold_var.set(threshold)
        self.apply_threshold()

    def make_overlay(self):
        if self.original_image is None or self.red_mask_image is None:
            return None

        rgb = np.array(self.original_image).astype(np.float32)
        result = rgb.copy()
        alpha = self.alpha_var.get()

        # Auto dark pixels = red
        red_mask = np.array(self.red_mask_image) > 0
        red = np.array([255, 0, 0], dtype=np.float32)
        result[red_mask] = (1 - alpha) * result[red_mask] + alpha * red

        # Manual line types
        for key, (_, color) in self.line_colors.items():
            mask = np.array(self.manual_masks[key]) > 0
            color_array = np.array(color, dtype=np.float32)
            result[mask] = (1 - alpha) * result[mask] + alpha * color_array

        result = np.clip(result, 0, 255).astype(np.uint8)
        self.overlay_image = Image.fromarray(result)

        self.update_info_label()
        return self.overlay_image

    def make_color_mask(self):
        if self.red_mask_image is None:
            return None

        red_mask = np.array(self.red_mask_image) > 0
        height, width = red_mask.shape

        # Black background
        color_mask = np.zeros((height, width, 3), dtype=np.uint8)

        # Auto dark pixels = red
        color_mask[red_mask] = [255, 0, 0]

        # Manual types overwrite red if overlapping
        for key, (_, color) in self.line_colors.items():
            mask = np.array(self.manual_masks[key]) > 0
            color_mask[mask] = color

        return Image.fromarray(color_mask)

    def make_combined_binary_mask(self):
        if self.red_mask_image is None:
            return None

        combined = np.array(self.red_mask_image) > 0

        for key in self.line_colors.keys():
            combined = np.logical_or(combined, np.array(self.manual_masks[key]) > 0)

        return Image.fromarray((combined * 255).astype(np.uint8), mode="L")

    def clear_selected_type(self):
        if self.original_image is None:
            return

        selected = self.manual_type_var.get()
        width, height = self.original_image.size

        self.manual_masks[selected] = Image.new("L", (width, height), 0)
        self.refresh_all()

    def clear_all_manual(self):
        if self.original_image is None:
            return

        width, height = self.original_image.size

        for key in self.line_colors.keys():
            self.manual_masks[key] = Image.new("L", (width, height), 0)

        self.refresh_all()

    def refresh_all(self):
        if self.original_image is None or self.red_mask_image is None:
            return

        self.make_overlay()
        self.show_main_preview()
        self.show_mask_preview()

    def fit_image_to_canvas(self, image, canvas):
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        if canvas_width < 20 or canvas_height < 20:
            canvas_width, canvas_height = 800, 500

        image_width, image_height = image.size

        scale = min(canvas_width / image_width, canvas_height / image_height)

        new_width = int(image_width * scale)
        new_height = int(image_height * scale)

        resized = image.resize((new_width, new_height), Image.LANCZOS)

        offset_x = (canvas_width - new_width) // 2
        offset_y = (canvas_height - new_height) // 2

        return resized, scale, (offset_x, offset_y)

    def show_main_preview(self):
        if self.overlay_image is None:
            return

        display_image, self.main_scale, self.main_offset = self.fit_image_to_canvas(
            self.overlay_image,
            self.main_canvas
        )

        self.main_preview = ImageTk.PhotoImage(display_image)

        self.main_canvas.delete("all")
        self.main_canvas.create_image(
            self.main_offset[0],
            self.main_offset[1],
            anchor=tk.NW,
            image=self.main_preview
        )

    def show_mask_preview(self):
        color_mask = self.make_color_mask()

        if color_mask is None:
            return

        display_image, self.mask_scale, self.mask_offset = self.fit_image_to_canvas(
            color_mask,
            self.mask_canvas
        )

        self.mask_preview = ImageTk.PhotoImage(display_image)

        self.mask_canvas.delete("all")
        self.mask_canvas.create_image(
            self.mask_offset[0],
            self.mask_offset[1],
            anchor=tk.NW,
            image=self.mask_preview
        )

    def canvas_to_image_coordinates(self, canvas_x, canvas_y, scale, offset):
        if self.original_image is None:
            return None

        offset_x, offset_y = offset

        image_x = int((canvas_x - offset_x) / scale)
        image_y = int((canvas_y - offset_y) / scale)

        width, height = self.original_image.size

        if image_x < 0 or image_y < 0 or image_x >= width or image_y >= height:
            return None

        return image_x, image_y

    def start_paint(self, event, panel, mode):
        point = self.get_point_from_panel(event, panel)

        if panel == "main":
            self.last_main_point = point
        else:
            self.last_mask_point = point

        self.paint_mask(point, mode=mode)

    def paint_drag(self, event, panel, mode):
        point = self.get_point_from_panel(event, panel)

        if panel == "main":
            last_point = self.last_main_point
            self.paint_mask(point, last_point=last_point, mode=mode)
            self.last_main_point = point
        else:
            last_point = self.last_mask_point
            self.paint_mask(point, last_point=last_point, mode=mode)
            self.last_mask_point = point

    def stop_paint(self, panel):
        if panel == "main":
            self.last_main_point = None
        else:
            self.last_mask_point = None

    def get_point_from_panel(self, event, panel):
        if panel == "main":
            return self.canvas_to_image_coordinates(
                event.x,
                event.y,
                self.main_scale,
                self.main_offset
            )

        return self.canvas_to_image_coordinates(
            event.x,
            event.y,
            self.mask_scale,
            self.mask_offset
        )

    def paint_mask(self, point, last_point=None, mode="draw"):
        if self.red_mask_image is None or point is None:
            return

        brush_size = self.brush_size_var.get()
        brush_radius = brush_size // 2

        x, y = point

        if mode == "draw":
            selected = self.manual_type_var.get()
            draw = ImageDraw.Draw(self.manual_masks[selected])

            if last_point is not None:
                x0, y0 = last_point
                draw.line(
                    [(x0, y0), (x, y)],
                    fill=255,
                    width=max(1, brush_size)
                )

            draw.ellipse(
                [
                    x - brush_radius,
                    y - brush_radius,
                    x + brush_radius,
                    y + brush_radius
                ],
                fill=255
            )

        elif mode == "erase":
            all_masks = [self.red_mask_image] + list(self.manual_masks.values())

            for mask_img in all_masks:
                draw = ImageDraw.Draw(mask_img)

                if last_point is not None:
                    x0, y0 = last_point
                    draw.line(
                        [(x0, y0), (x, y)],
                        fill=0,
                        width=max(1, brush_size)
                    )

                draw.ellipse(
                    [
                        x - brush_radius,
                        y - brush_radius,
                        x + brush_radius,
                        y + brush_radius
                    ],
                    fill=0
                )

        self.refresh_all()

    def update_info_label(self):
        selected_key = self.manual_type_var.get()
        selected_label = self.line_colors[selected_key][0]

        if self.red_mask_image is None:
            self.info_label.config(
                text=f"Selected = {selected_label} | Upload or drag-and-drop image | LEFT drag = draw | RIGHT drag = erase"
            )
            return

        red_mask = np.array(self.red_mask_image) > 0
        total_pixels = red_mask.size

        red_percent = 100 * np.sum(red_mask) / total_pixels

        manual_text = []

        for key, (label, _) in self.line_colors.items():
            mask = np.array(self.manual_masks[key]) > 0
            percent = 100 * np.sum(mask) / total_pixels
            manual_text.append(f"{label.split(':')[0]} = {percent:.2f}%")

        combined = red_mask.copy()

        for key in self.line_colors.keys():
            combined = np.logical_or(combined, np.array(self.manual_masks[key]) > 0)

        total_percent = 100 * np.sum(combined) / total_pixels

        self.info_label.config(
            text=f"Selected = {selected_label} | "
                 f"LEFT drag = draw | RIGHT drag = erase | Mouse wheel = brush size | "
                 f"Threshold = {self.threshold_var.get()} | Brush = {self.brush_size_var.get()} px | "
                 f"Red auto = {red_percent:.2f}% | "
                 f"{' | '.join(manual_text)} | Total = {total_percent:.2f}%"
        )

    def save_overlay(self):
        if self.overlay_image is None:
            messagebox.showwarning("No image", "Please process an image first.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save overlay image",
            defaultextension=".png",
            filetypes=[
                ("PNG image", "*.png"),
                ("TIFF image", "*.tif"),
                ("JPEG image", "*.jpg")
            ]
        )

        if save_path:
            self.overlay_image.save(save_path)
            messagebox.showinfo("Saved", f"Overlay saved:\n{save_path}")

    def save_color_mask(self):
        color_mask = self.make_color_mask()

        if color_mask is None:
            messagebox.showwarning("No mask", "Please create a mask first.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save color mask",
            defaultextension=".png",
            filetypes=[
                ("PNG image", "*.png"),
                ("TIFF image", "*.tif")
            ]
        )

        if save_path:
            color_mask.save(save_path)
            messagebox.showinfo("Saved", f"Color mask saved:\n{save_path}")

    def save_combined_mask(self):
        combined_mask = self.make_combined_binary_mask()

        if combined_mask is None:
            messagebox.showwarning("No mask", "Please create a mask first.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save combined binary mask",
            defaultextension=".png",
            filetypes=[
                ("PNG image", "*.png"),
                ("TIFF image", "*.tif")
            ]
        )

        if save_path:
            combined_mask.save(save_path)
            messagebox.showinfo("Saved", f"Binary mask saved:\n{save_path}")


if __name__ == "__main__":
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    app = HistoChemistryImageMaskEditor(root)
    root.mainloop()