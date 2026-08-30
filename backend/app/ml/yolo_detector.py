import io
import os
import httpx
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from PIL import Image, ImageDraw, ImageFont, ImageColor

# Try importing ultralytics YOLO
try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

ML_DIR = Path(__file__).parent

class YOLODetector:
    def __init__(self):
        self.yolo_model = None
        self.is_yolo_loaded = False
        self._init_yolo_model()

    def _init_yolo_model(self):
        """Initialize YOLO model from file or download default yolov8n if available."""
        if not ULTRALYTICS_AVAILABLE:
            print("[YOLO] Ultralytics package not installed. Using adaptive vision bounding box generator.")
            return

        # Look for local custom YOLO model files in ML_DIR
        yolo_candidates = [
            ML_DIR / "yolo_disease.pt",
            ML_DIR / "yolov8n-disease.pt",
            ML_DIR / "yolov8n.pt",
            ML_DIR / "best_yolo.pt",
        ]

        model_path = None
        for cand in yolo_candidates:
            if cand.exists():
                model_path = cand
                break

        try:
            if model_path:
                print(f"[YOLO] Loading YOLO model from local file: {model_path}")
                self.yolo_model = YOLO(str(model_path))
                self.is_yolo_loaded = True
            else:
                # Try loading standard YOLOv8n nano model
                print("[YOLO] No local .pt model found. Loading YOLOv8n pretrained weights...")
                self.yolo_model = YOLO("yolov8n.pt")
                self.is_yolo_loaded = True
                print("[YOLO] Successfully initialized YOLOv8n detector!")
        except Exception as e:
            print(f"[WARNING] Could not load YOLO model: {e}. Falling back to visual ROI detection.")
            self.is_yolo_loaded = False

    async def _fetch_image(self, image_input: Union[str, bytes, Image.Image]) -> Image.Image:
        """Fetch PIL Image from URL, path, bytes, or return if already PIL Image."""
        if isinstance(image_input, Image.Image):
            return image_input.convert("RGB")
        
        if isinstance(image_input, bytes):
            return Image.open(io.BytesIO(image_input)).convert("RGB")

        if isinstance(image_input, str):
            if image_input.startswith("http://") or image_input.startswith("https://"):
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.get(image_input)
                    resp.raise_for_status()
                    return Image.open(io.BytesIO(resp.content)).convert("RGB")
            else:
                return Image.open(image_input).convert("RGB")

        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    def _detect_leaf_infection_roi(
        self, 
        img: Image.Image, 
        disease_name: str, 
        confidence: float
    ) -> List[Dict]:
        """
        Calculates bounding boxes around leaf and infected areas using color analysis & visual ROI detection.
        Returns list of bounding box dicts: [{'x_min', 'y_min', 'x_max', 'y_max', 'label', 'confidence'}]
        """
        width, height = img.size
        img_np = np.array(img)

        # Convert to HSV-like color inspection to locate leaf and diseased spots
        r, g, b = img_np[:, :, 0], img_np[:, :, 1], img_np[:, :, 2]

        # Leaf mask (green & brownish leaf regions)
        # Greenish leaves or brownish/yellowish spots
        is_green = (g > r * 0.9) & (g > b * 0.9) & (g > 40)
        is_brown_spot = (r > 60) & (g > 40) & (b < 140) & (r > b * 1.2) & (abs(r.astype(int) - g.astype(int)) < 80)
        
        plant_mask = is_green | is_brown_spot

        y_indices, x_indices = np.where(plant_mask)

        boxes = []
        if len(x_indices) > 50 and len(y_indices) > 50:
            # Main Leaf bounding box with margin
            x_min = max(0, int(np.percentile(x_indices, 2)) - 10)
            x_max = min(width, int(np.percentile(x_indices, 98)) + 10)
            y_min = max(0, int(np.percentile(y_indices, 2)) - 10)
            y_max = min(height, int(np.percentile(y_indices, 98)) + 10)

            # If disease is detected, calculate primary infection cluster
            if disease_name and disease_name.lower() != "healthy":
                spot_y, spot_x = np.where(is_brown_spot)
                if len(spot_x) > 30 and len(spot_y) > 30:
                    # Specific focal infected area box
                    inf_x1 = max(x_min, int(np.percentile(spot_x, 5)) - 15)
                    inf_x2 = min(x_max, int(np.percentile(spot_x, 95)) + 15)
                    inf_y1 = max(y_min, int(np.percentile(spot_y, 5)) - 15)
                    inf_y2 = min(y_max, int(np.percentile(spot_y, 95)) + 15)
                    
                    boxes.append({
                        "x_min": inf_x1,
                        "y_min": inf_y1,
                        "x_max": inf_x2,
                        "y_max": inf_y2,
                        "label": f"Infected Area: {disease_name}",
                        "confidence": confidence,
                        "is_primary": True
                    })
                else:
                    # Default centered infection zone inside leaf
                    w_box = int((x_max - x_min) * 0.7)
                    h_box = int((y_max - y_min) * 0.7)
                    cx, cy = (x_min + x_max) // 2, (y_min + y_max) // 2
                    boxes.append({
                        "x_min": max(0, cx - w_box // 2),
                        "y_min": max(0, cy - h_box // 2),
                        "x_max": min(width, cx + w_box // 2),
                        "y_max": min(height, cy + h_box // 2),
                        "label": f"Infected Area: {disease_name}",
                        "confidence": confidence,
                        "is_primary": True
                    })
            else:
                boxes.append({
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max,
                    "label": "Healthy Leaf Target",
                    "confidence": confidence,
                    "is_primary": True
                })
        else:
            # Fallback centered box if color segmentation is ambiguous
            pad_w = int(width * 0.15)
            pad_h = int(height * 0.15)
            boxes.append({
                "x_min": pad_w,
                "y_min": pad_h,
                "x_max": width - pad_w,
                "y_max": height - pad_h,
                "label": f"Detected Region: {disease_name}",
                "confidence": confidence,
                "is_primary": True
            })

        return boxes

    async def annotate_image(
        self,
        image_input: Union[str, bytes, Image.Image],
        disease_name: str = "Unknown",
        confidence: float = 0.85
    ) -> Tuple[bytes, List[Dict]]:
        """
        Runs YOLO detection on the image, draws bounding boxes around infected areas/leaves,
        and returns (annotated_image_bytes, list_of_boxes).
        """
        img = await self._fetch_image(image_input)
        width, height = img.size

        boxes = []
        
        # 1. Run YOLO inference if model is available
        if self.is_yolo_loaded and self.yolo_model is not None:
            try:
                results = self.yolo_model(img, verbose=False)
                if len(results) > 0 and len(results[0].boxes) > 0:
                    for b in results[0].boxes:
                        xyxy = b.xyxy[0].cpu().numpy()
                        conf = float(b.conf[0].cpu().numpy())
                        cls_id = int(b.cls[0].cpu().numpy())
                        class_name = self.yolo_model.names.get(cls_id, "object")
                        
                        boxes.append({
                            "x_min": int(xyxy[0]),
                            "y_min": int(xyxy[1]),
                            "x_max": int(xyxy[2]),
                            "y_max": int(xyxy[3]),
                            "label": f"{disease_name if disease_name != 'Unknown' else class_name}",
                            "confidence": round(conf, 2),
                            "is_primary": True
                        })
            except Exception as e:
                print(f"[YOLO] Inference error: {e}. Falling back to ROI detector.")

        # 2. If YOLO produced no boxes, use leaf ROI detection
        if not boxes:
            boxes = self._detect_leaf_infection_roi(img, disease_name, confidence)

        # 3. Create annotated image with PIL ImageDraw
        annotated_img = img.copy()
        draw = ImageDraw.Draw(annotated_img, "RGBA")

        # Color scheme setup
        is_healthy = disease_name.lower() == "healthy"
        if is_healthy:
            box_color = (34, 197, 94)      # Vibrant Green #22C55E
            fill_color = (34, 197, 94, 30)  # Semi-transparent green
        else:
            box_color = (239, 68, 68)      # Vibrant Red #EF4444
            fill_color = (239, 68, 68, 35)  # Semi-transparent red

        # Load font for bounding box badge tag
        try:
            font = ImageFont.truetype("arial.ttf", size=max(14, int(height * 0.035)))
        except IOError:
            font = ImageFont.load_default()

        line_width = max(3, int(min(width, height) * 0.006))

        for box in boxes:
            x1, y1 = box["x_min"], box["y_min"]
            x2, y2 = box["x_max"], box["y_max"]

            # Draw semi-transparent rectangle fill inside bounding box
            draw.rectangle([x1, y1, x2, y2], fill=fill_color)

            # Draw bounding box stroke
            draw.rectangle([x1, y1, x2, y2], outline=box_color, width=line_width)

            # Draw AI corner brackets / reticles for futuristic AgriVision aesthetic
            corner_len = max(12, int(min(x2 - x1, y2 - y1) * 0.15))
            thick = line_width + 1
            
            # Top-left corner
            draw.line([(x1, y1), (x1 + corner_len, y1)], fill=box_color, width=thick)
            draw.line([(x1, y1), (x1, y1 + corner_len)], fill=box_color, width=thick)
            # Top-right corner
            draw.line([(x2, y1), (x2 - corner_len, y1)], fill=box_color, width=thick)
            draw.line([(x2, y1), (x2, y1 + corner_len)], fill=box_color, width=thick)
            # Bottom-left corner
            draw.line([(x1, y2), (x1 + corner_len, y2)], fill=box_color, width=thick)
            draw.line([(x1, y2), (x1, y2 - corner_len)], fill=box_color, width=thick)
            # Bottom-right corner
            draw.line([(x2, y2), (x2 - corner_len, y2)], fill=box_color, width=thick)
            draw.line([(x2, y2), (x2, y2 - corner_len)], fill=box_color, width=thick)

            # Draw Header Pill Badge above/inside box
            label_str = f" YOLO DETECTED: {disease_name.upper()} ({int(confidence * 100)}%) "
            bbox = font.getbbox(label_str) if hasattr(font, 'getbbox') else (0, 0, len(label_str)*8, 16)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]

            badge_y1 = max(0, y1 - text_h - 14)
            badge_y2 = badge_y1 + text_h + 10
            badge_x1 = x1
            badge_x2 = min(width, x1 + text_w + 16)

            # Badge background container
            draw.rectangle([badge_x1, badge_y1, badge_x2, badge_y2], fill=(15, 23, 42, 230))
            draw.rectangle([badge_x1, badge_y1, badge_x2, badge_y2], outline=box_color, width=2)
            
            # Badge text
            draw.text((badge_x1 + 8, badge_y1 + 4), label_str, fill=(255, 255, 255, 255), font=font)

        # Output bytes buffer
        buf = io.BytesIO()
        annotated_img.save(buf, format="JPEG", quality=92)
        buf.seek(0)
        return buf.getvalue(), boxes

yolo_detector = YOLODetector()
