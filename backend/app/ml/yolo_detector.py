import os
from pathlib import Path
from typing import Optional
from PIL import Image

# Base directory paths
ML_DIR = Path(__file__).parent
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MYWORK_MODEL_DIR = PROJECT_ROOT / "mywork" / "models"

# Candidate model paths for YOLOv8
YOLO_MODEL_CANDIDATES = [
    MYWORK_MODEL_DIR / "best.pt",
    ML_DIR / "best.pt",
    ML_DIR / "yolov8.pt",
]

class YOLOLeafDetector:
    def __init__(self):
        self.model = None
        self.is_ready = False
        self.model_path: Optional[Path] = None
        self._load_model()

    def _load_model(self):
        """Locate and load the YOLOv8 model weights."""
        try:
            from ultralytics import YOLO
        except ImportError:
            print("[INFO] ultralytics package is not installed. YOLOv8 leaf detection disabled.")
            return

        found_path = None
        for path in YOLO_MODEL_CANDIDATES:
            if path.exists():
                found_path = path
                break

        if not found_path:
            # Search for any .pt file named best or yolo
            pt_files = list(MYWORK_MODEL_DIR.glob("best*.pt")) + list(ML_DIR.glob("best*.pt"))
            if pt_files:
                found_path = pt_files[0]

        if not found_path:
            print(f"[INFO] No YOLOv8 model file (best.pt) found in {MYWORK_MODEL_DIR} or {ML_DIR}.")
            return

        try:
            self.model_path = found_path
            self.model = YOLO(str(found_path))
            self.is_ready = True
            print(f"[YOLOv8] Successfully loaded leaf detection model from: {found_path}")
        except Exception as e:
            print(f"[ERROR] Failed to load YOLOv8 model from {found_path}: {e}")
            self.is_ready = False

    def detect_and_crop(self, image: Image.Image, conf_threshold: float = 0.15) -> Image.Image:
        """
        Detect tomato leaf in PIL Image and crop the detected region.
        If no leaf is detected or YOLO is unavailable, returns the original image.
        """
        if not self.is_ready or self.model is None:
            return image

        try:
            # Run YOLOv8 detection
            results = self.model(image, conf=conf_threshold, verbose=False)
            if not results or len(results) == 0:
                return image

            boxes = results[0].boxes
            if boxes is None or len(boxes) == 0:
                print("[YOLOv8] No leaf detected in image. Using full image for classification.")
                return image

            # Select the bounding box with the highest confidence score
            confidences = boxes.conf.cpu().numpy()
            best_idx = int(confidences.argmax())
            best_box = boxes.xyxy[best_idx].cpu().numpy()  # [xmin, ymin, xmax, ymax]
            xmin, ymin, xmax, ymax = map(int, best_box)

            # Add 15% margin padding around the leaf bounding box for expanded leaf context
            box_w = xmax - xmin
            box_h = ymax - ymin
            pad_x = int(box_w * 0.15)
            pad_y = int(box_h * 0.15)

            width, height = image.size
            xmin = max(0, xmin - pad_x)
            ymin = max(0, ymin - pad_y)
            xmax = min(width, xmax + pad_x)
            ymax = min(height, ymax + pad_y)


            print(f"[YOLOv8] Leaf detected with confidence {confidences[best_idx]:.2f}. Cropping bbox: [{xmin}, {ymin}, {xmax}, {ymax}]")
            cropped_image = image.crop((xmin, ymin, xmax, ymax))

            # Save latest cropped leaf to uploads folder so it can be visually inspected at http://localhost:8000/uploads/latest_cropped_leaf.jpg
            try:
                debug_dir = ML_DIR.parent.parent / "uploads"
                if debug_dir.exists():
                    cropped_image.save(debug_dir / "latest_cropped_leaf.jpg")
            except Exception:
                pass

            return cropped_image

        except Exception as e:
            print(f"[WARNING] Error during YOLO leaf detection/cropping: {e}. Falling back to full image.")
            return image


yolo_leaf_detector = YOLOLeafDetector()
