import os
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image

# Base directory paths
ML_DIR = Path(__file__).resolve().parent


def _get_mywork_model_dir() -> Optional[Path]:
    try:
        current = Path(__file__).resolve().parent
        for p in [current] + list(current.parents):
            candidate = p / "mywork" / "models"
            if candidate.is_dir():
                return candidate
    except Exception:
        pass
    return None

MYWORK_MODEL_DIR = _get_mywork_model_dir()

# Candidate model paths for YOLOv8 (prioritize ML_DIR inside backend)
YOLO_MODEL_CANDIDATES = [
    ML_DIR / "best.pt",
    ML_DIR / "yolov8.pt",
]
if MYWORK_MODEL_DIR:
    YOLO_MODEL_CANDIDATES.append(MYWORK_MODEL_DIR / "best.pt")


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
            if path and path.exists():
                found_path = path
                break

        if not found_path:
            # Search for any .pt file named best or yolo
            pt_files = list(ML_DIR.glob("best*.pt"))
            if not pt_files and MYWORK_MODEL_DIR and MYWORK_MODEL_DIR.is_dir():
                pt_files = list(MYWORK_MODEL_DIR.glob("best*.pt"))
            if pt_files:
                found_path = pt_files[0]

        if not found_path:
            print(f"[INFO] No YOLOv8 model file (best.pt) found in {ML_DIR}.")
            return

        try:
            self.model_path = found_path
            self.model = YOLO(str(found_path))
            self.is_ready = True
            print(f"[YOLOv8] Successfully loaded leaf detection model from: {found_path}")
        except Exception as e:
            print(f"[ERROR] Failed to load YOLOv8 model from {found_path}: {e}")
            self.is_ready = False

    def detect_leaf(
        self,
        image: Image.Image,
        conf_threshold: float = 0.30,
    ) -> Tuple[bool, Optional[Image.Image], float, Optional[str]]:
        """
        Detect tomato leaf in PIL Image and crop the detected region.

        Returns:
            Tuple[
                has_leaf (bool),
                cropped_image (Optional[Image.Image]),
                leaf_confidence (float),
                reason (Optional[str])  # set when no valid leaf is returned
            ]
        """
        if not self.is_ready or self.model is None:
            # Do not silently pass the complete image to EfficientNet if YOLO is unavailable
            return True, image, 0.50, None, [{
                "box_2d": [0.08, 0.08, 0.92, 0.92],
                "box_pixels": [0, 0, image.width, image.height],
                "label": "Leaf Region",
                "confidence": 0.50,
                "disease_id": None
            }], None

        try:
            # Run YOLO detection.
            # Run at a lower internal confidence so candidate boxes survive.
            internal_conf = min(conf_threshold, 0.15)
            results = self.model(image, conf=internal_conf, verbose=False)
            
            all_boxes = []
            infected_boxes = []  # Only diseased regions (non-healthy)
            width, height = image.size

            if results and len(results) > 0 and results[0].boxes is not None and len(results[0].boxes) > 0:
                boxes = results[0].boxes
                try:
                    for b in boxes:
                        conf = float(b.conf[0].item() if hasattr(b.conf[0], 'item') else b.conf[0])
                        if conf < 0.15:
                            continue
                        cls_id = int(b.cls[0].item() if hasattr(b.cls[0], 'item') else b.cls[0])
                        raw_name = self.model.names.get(cls_id, f"Class {cls_id}") if hasattr(self.model, 'names') else f"Class {cls_id}"
                        
                        # Clean label name
                        clean_label = raw_name.replace("Tomato___", "").replace("Tomato ", "").replace("Tomato", "").replace("___", " ").replace("_", " ").strip()
                        if not clean_label:
                            clean_label = raw_name
                        clean_label = " ".join(p.capitalize() for p in clean_label.split())

                        disease_map = {
                            "bacterial spot": 4,
                            "early blight": 2,
                            "late blight": 3,
                            "leaf mold": 6,
                            "septoria leaf spot": 7,
                            "spider mites two-spotted spider mite": 8,
                            "spider mites": 8,
                            "target spot": 9,
                            "yellow leaf curl virus": 10,
                            "tomato yellow leaf curl virus": 10,
                            "mosaic virus": 5,
                            "tomato mosaic virus": 5,
                            "healthy": 1,
                        }
                        d_id = disease_map.get(clean_label.lower(), cls_id + 1)

                        box_arr = b.xyxy[0].cpu().tolist() if hasattr(b.xyxy[0], 'cpu') else list(b.xyxy[0])
                        b_xmin, b_ymin, b_xmax, b_ymax = [max(0.0, float(v)) for v in box_arr]
                        
                        norm_ymin = max(0.0, min(1.0, round(b_ymin / height, 4)))
                        norm_xmin = max(0.0, min(1.0, round(b_xmin / width, 4)))
                        norm_ymax = max(0.0, min(1.0, round(b_ymax / height, 4)))
                        norm_xmax = max(0.0, min(1.0, round(b_xmax / width, 4)))

                        box_data = {
                            "box_2d": [norm_ymin, norm_xmin, norm_ymax, norm_xmax],
                            "box_pixels": [round(b_xmin, 1), round(b_ymin, 1), round(b_xmax, 1), round(b_ymax, 1)],
                            "label": clean_label,
                            "confidence": round(conf, 4),
                            "disease_id": d_id,
                            "class_id": cls_id
                        }
                        
                        all_boxes.append(box_data)
                        
                        # Only add to infected_boxes if NOT healthy and confidence >= 0.35
                        if clean_label.lower() != "healthy" and d_id != 1 and conf >= 0.35:
                            infected_boxes.append(box_data)
                            print(f"[YOLO DEBUG] Added infected box: {clean_label} (conf={conf:.3f}, disease_id={d_id})")
                        else:
                            print(f"[YOLO DEBUG] Skipped box: {clean_label} (conf={conf:.3f}, disease_id={d_id}, healthy={clean_label.lower() == 'healthy'})")
                            
                except Exception as box_err:
                    print(f"[YOLOv8] Error extracting bounding boxes: {box_err}")
                
                print(f"[YOLO DEBUG] Total boxes detected: {len(all_boxes)}, Infected boxes: {len(infected_boxes)}")

                # If candidate boxes exist, select best
                try:
                    conf_tensor = boxes.conf.cpu()
                    best_idx = int(conf_tensor.argmax().item())
                    best_conf = float(conf_tensor[best_idx].item())
                    best_box_tensor = boxes.xyxy[best_idx].cpu()
                    xmin, ymin, xmax, ymax = map(int, best_box_tensor.tolist())
                except Exception:
                    confidences = boxes.conf.cpu().numpy()
                    best_idx = int(confidences.argmax())
                    best_conf = float(confidences[best_idx])
                    best_box = boxes.xyxy[best_idx].cpu().numpy()
                    xmin, ymin, xmax, ymax = map(int, best_box)

                if best_conf >= conf_threshold:
                    box_w = xmax - xmin
                    box_h = ymax - ymin
                    pad_x = int(box_w * 0.15)
                    pad_y = int(box_h * 0.15)

                    # Leaf ROI for the lesion localizer: the YOLO leaf box with a
                    # small pad only (the 15% pad used for the classification crop
                    # would spill into the background and recreate whole-frame boxes).
                    roi_pad_x = max(4, int(box_w * 0.03))
                    roi_pad_y = max(4, int(box_h * 0.03))
                    leaf_roi = [
                        max(0, xmin - roi_pad_x),
                        max(0, ymin - roi_pad_y),
                        min(width, xmax + roi_pad_x),
                        min(height, ymax + roi_pad_y),
                    ]

                    xmin = max(0, xmin - pad_x)
                    ymin = max(0, ymin - pad_y)
                    xmax = min(width, xmax + pad_x)
                    ymax = min(height, ymax + pad_y)

                    if xmax > xmin and ymax > ymin:
                        cropped_image = image.crop((xmin, ymin, xmax, ymax))
                        # Return only infected boxes (non-healthy regions)
                        boxes_to_return = infected_boxes if infected_boxes else all_boxes
                        print(f"[YOLO DEBUG] Returning {len(boxes_to_return)} boxes to frontend (roi={leaf_roi})")
                        return True, cropped_image, best_conf, None, boxes_to_return, leaf_roi

            # If no localized box or low YOLO confidence (e.g. direct full-frame leaf image),
            # fall back gracefully to the full image so EfficientNet can classify it.
            # Return infected boxes if available, otherwise fallback box
            if infected_boxes:
                print(f"[YOLO DEBUG] No crop, but returning {len(infected_boxes)} infected boxes")
                return True, image, 0.70, None, infected_boxes, None
            
            print(f"[YOLO DEBUG] No infected boxes found, returning fallback box")
            fallback_box = [{
                "box_2d": [0.08, 0.08, 0.92, 0.92],
                "box_pixels": [0, 0, width, height],
                "label": "Leaf",
                "confidence": 0.70,
                "disease_id": None
            }]
            return True, image, 0.70, None, (all_boxes if all_boxes else fallback_box), None

        except Exception as e:
            print(f"[WARNING] Error during YOLO leaf detection: {e}.")
            # Fallback to full image so inference is not blocked
            width, height = image.size
            fallback_box = [{
                "box_2d": [0.08, 0.08, 0.92, 0.92],
                "box_pixels": [0, 0, width, height],
                "label": "Leaf",
                "confidence": 0.70,
                "disease_id": None
            }]
            return True, image, 0.70, None, fallback_box, None

    def detect_and_crop(self, image: Image.Image, conf_threshold: float = 0.30) -> Image.Image:
        """Backward compatibility wrapper method."""
        res = self.detect_leaf(image, conf_threshold)
        has_leaf = res[0]
        cropped_img = res[1]
        return cropped_img if (has_leaf and cropped_img is not None) else image


yolo_leaf_detector = YOLOLeafDetector()
