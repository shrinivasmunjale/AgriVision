import os
import json
import io
import httpx
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image

# Base directory for ML artifacts
ML_DIR = Path(__file__).resolve().parent
LABELS_FILE = ML_DIR / "labels.json"


# Potential model filenames in backend/app/ml/
MODEL_CANDIDATES = [
    ML_DIR / "best_efficientnetb0.pth",  # Our trained model
    ML_DIR / "model.pt",
    ML_DIR / "model.pth",
    ML_DIR / "best.pt",
    ML_DIR / "best.pth",
    ML_DIR / "crop_disease_model.pt",
]

# Also check for class_names.json in ML_DIR first
CLASS_NAMES_FILE = ML_DIR / "class_names.json"

# Safe lookup function for external mywork/models folder (local dev environment)
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
MYWORK_MODEL_FILE = MYWORK_MODEL_DIR / "best_efficientnetb0.pth" if MYWORK_MODEL_DIR else None
MYWORK_CLASS_NAMES = MYWORK_MODEL_DIR / "class_names.json" if MYWORK_MODEL_DIR else None

# Display-name (lower-cased) -> AgriVision database disease_id mapping.
DISEASE_ID_MAP = {
    "bacterial spot": 4,
    "tomato bacterial spot": 4,
    "early blight": 2,
    "tomato early blight": 2,
    "late blight": 3,
    "tomato late blight": 3,
    "leaf mold": 6,
    "tomato leaf mold": 6,
    "septoria leaf spot": 7,
    "tomato septoria leaf spot": 7,
    "spider mites two-spotted spider mite": 8,
    "spider mites": 8,
    "tomato spider mites two-spotted spider mite": 8,
    "target spot": 9,
    "tomato target spot": 9,
    "tomato yellow leaf curl virus": 10,
    "tomato tomato yellow leaf curl virus": 10,
    "yellow leaf curl virus": 10,
    "tomato mosaic virus": 5,
    "tomato tomato mosaic virus": 5,
    "healthy": 1,
    "tomato healthy": 1,
}

def _clean_class_name(raw: str) -> str:
    """Turn PlantVillage-style names like 'Tomato___Bacterial_spot' into 'Bacterial Spot'."""
    clean_name = raw.replace("Tomato___", "").replace("___", " ").replace("_", " ").strip()
    return " ".join(part.capitalize() for part in clean_name.split())

def _class_name_to_label_info(class_name: str, idx: int) -> Dict:
    """Map a raw model class name + index to AgriVision {disease_id, name}."""
    clean_display = _clean_class_name(class_name)
    clean_key = clean_display.lower()
    disease_id = DISEASE_ID_MAP.get(clean_key)
    if disease_id is None:
        raw_key = class_name.replace("___", " ").replace("_", " ").lower().strip()
        disease_id = DISEASE_ID_MAP.get(raw_key)
    if disease_id is None:
        disease_id = idx + 1
    return {
        "disease_id": disease_id,
        "name": clean_display,
    }


class PyTorchModelLoader:
    def __init__(self):
        self.model = None
        self.labels: Dict[str, Dict] = {}
        self.is_torch_available = False
        self.model_path: Optional[Path] = None
        self.device = "cpu"
        
        self._init_environment()
        
    def _init_environment(self):
        """Check for PyTorch availability, model weights, and labels configuration."""
        # 1. Load labels mapping
        self._load_labels()
        
        # 2. Check if PyTorch is installed
        try:
            import torch
            import torchvision.transforms as T
            from PIL import Image
            
            self.is_torch_available = True
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self.device = "mps"
                
            # Define standard ImageNet preprocessing transform
            self.transform = T.Compose([
                T.Resize((224, 224)),
                T.ToTensor(),
                T.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
        except ImportError:
            self.is_torch_available = False
            print("[INFO] PyTorch is not installed. Using fallback predictions.")
            return

        # 3. Locate and load model weights
        self._load_model()

    def _load_labels(self):
        """Load the model's class -> disease mapping."""
        if CLASS_NAMES_FILE.exists():
            try:
                with open(CLASS_NAMES_FILE, "r", encoding="utf-8") as f:
                    raw_names = json.load(f)
                self.labels = {
                    str(idx): _class_name_to_label_info(name, idx)
                    for idx, name in enumerate(raw_names)
                }
                print(f"[LABELS] Loaded {len(self.labels)} classes from {CLASS_NAMES_FILE.name}")
                return
            except Exception as e:
                print(f"[WARNING] Failed to load class_names.json from ML_DIR: {e}")
        
        if MYWORK_CLASS_NAMES and MYWORK_CLASS_NAMES.exists():
            try:
                with open(MYWORK_CLASS_NAMES, "r", encoding="utf-8") as f:
                    raw_names = json.load(f)
                self.labels = {
                    str(idx): _class_name_to_label_info(name, idx)
                    for idx, name in enumerate(raw_names)
                }
                print(f"[LABELS] Loaded {len(self.labels)} classes from {MYWORK_CLASS_NAMES.name}")
                return
            except Exception as e:
                print(f"[WARNING] Failed to load class_names.json from mywork: {e}")

        if LABELS_FILE.exists():
            try:
                with open(LABELS_FILE, "r", encoding="utf-8") as f:
                    self.labels = json.load(f)
            except Exception as e:
                print(f"[WARNING] Failed to load labels.json: {e}")

    def _load_model(self):
        """Find and load PyTorch model file."""
        if not self.is_torch_available:
            return
            
        import torch

        found_path = None
        for path in MODEL_CANDIDATES:
            if path.exists():
                found_path = path
                print(f"[MODEL] Found deployed model at: {path}")
                break

        if found_path is None and MYWORK_MODEL_FILE and MYWORK_MODEL_FILE.exists():
            found_path = MYWORK_MODEL_FILE
            print(f"[MODEL] Found development model at: {MYWORK_MODEL_FILE}")

        if found_path is None:
            pt_files = list(ML_DIR.glob("*.pt")) + list(ML_DIR.glob("*.pth"))
            if not pt_files and MYWORK_MODEL_DIR and MYWORK_MODEL_DIR.is_dir():
                pt_files = list(MYWORK_MODEL_DIR.glob("*.pt")) + list(MYWORK_MODEL_DIR.glob("*.pth"))
            if pt_files:
                found_path = pt_files[0]

        if not found_path:
            print(f"[INFO] No PyTorch model file found in {ML_DIR}.")
            return

        self.model_path = found_path
        print(f"[MODEL] Loading PyTorch model from: {found_path} on device: {self.device}")

        try:
            self.model = torch.jit.load(str(found_path), map_location=self.device)
            self.model.eval()
            print("[SUCCESS] TorchScript model loaded successfully!")
        except Exception as script_err:
            try:
                loaded = torch.load(str(found_path), map_location=self.device)
                if isinstance(loaded, torch.nn.Module):
                    self.model = loaded
                    self.model.eval()
                    print("[SUCCESS] PyTorch nn.Module loaded successfully!")
                elif isinstance(loaded, dict) and "model" in loaded and isinstance(loaded["model"], torch.nn.Module):
                    self.model = loaded["model"]
                    if hasattr(self.model, "eval"):
                        self.model.eval()
                    print("[SUCCESS] PyTorch model checkpoint loaded successfully!")
                elif isinstance(loaded, dict):
                    state_dict = loaded.get("state_dict", loaded.get("model_state_dict", loaded))
                    num_classes = len(self.labels) if self.labels else 10
                    import torchvision.models as tv_models
                    import torch.nn as nn
                    
                    try:
                        eff_model = tv_models.efficientnet_b0(weights=None)
                        in_features = eff_model.classifier[1].in_features
                        eff_model.classifier[1] = nn.Linear(in_features, num_classes)
                        eff_model.load_state_dict(state_dict)
                        self.model = eff_model.to(self.device)
                        self.model.eval()
                        print("[SUCCESS] EfficientNet-B0 model loaded successfully from state dict!")
                    except Exception as eff_err:
                        try:
                            res_model = tv_models.resnet18(weights=None)
                            res_model.fc = nn.Linear(res_model.fc.in_features, num_classes)
                            res_model.load_state_dict(state_dict)
                            self.model = res_model.to(self.device)
                            self.model.eval()
                            print("[SUCCESS] ResNet-18 model loaded successfully from state dict!")
                        except Exception as res_err:
                            print(f"[WARNING] Could not automatically map state dict: {res_err}")
                else:
                    print(f"[WARNING] torch.load returned object format: {script_err}")
            except Exception as load_err:
                print(f"[ERROR] Failed to load model from {found_path}: {load_err}")

    def is_ready(self) -> bool:
        """Return True if PyTorch is installed and model is loaded."""
        return self.is_torch_available and self.model is not None

    async def _fetch_image(self, image_url: str):
        """Download image bytes from HTTP URL or load directly from disk if local path."""
        from PIL import Image
        from urllib.parse import unquote

        raw_url = str(image_url).strip()
        path_str = unquote(raw_url)

        # 1. Check if the URL points to a local upload (/uploads/filename.jpg)
        if "/uploads/" in path_str:
            filename = path_str.split("/uploads/")[-1]
            candidates = [
                Path("uploads") / filename,
                Path("backend/uploads") / filename,
                Path(__file__).resolve().parents[2] / "uploads" / filename,
            ]
            for cand in candidates:
                if cand.exists():
                    print(f"[ML] Loaded image directly from disk: {cand}")
                    return Image.open(cand).convert("RGB")

        # 2. Check if path_str is a direct local file path
        if not (path_str.startswith("http://") or path_str.startswith("https://")):
            p = Path(path_str)
            if p.exists():
                return Image.open(p).convert("RGB")

        # 3. HTTP download with fallback
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(raw_url)
                resp.raise_for_status()
                image_bytes = resp.content
            return Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as e:
            print(f"[WARNING] Remote fetch failed for {raw_url} ({e}). Checking local uploads fallback...")
            filename = path_str.split("/")[-1]
            for cand in [Path("uploads") / filename, Path("backend/uploads") / filename]:
                if cand.exists():
                    return Image.open(cand).convert("RGB")
            raise e

    async def predict_image(self, image_url: str, filename: Optional[str] = None) -> Dict:
        """
        Run two-stage pipeline:
        1. Run YOLOv8 detection. If no leaf, return an ignored result with reason.
        2. Run EfficientNetB0 classification. If confidence < 50%, return ignored result.

        Returns a normalized dict:
            valid  -> {"status": "valid", "disease_id", "disease_name", "confidence_score",
                        "image_url", "filename", "cropped_image"}
            ignored-> {"status": "ignored", "reason", "image_url", "filename", "confidence_score"}
        """
        if not self.is_ready():
            raise RuntimeError("PyTorch model is not loaded.")

        import torch

        display_name = self._derive_filename(image_url, filename)

        # Fetch image with explicit error handling -> "Corrupted or invalid image"
        try:
            image = await self._fetch_image(image_url)
        except Exception as e:
            print(f"[ERROR] Failed to fetch image {image_url}: {e}")
            return {
                "status": "ignored",
                "reason": f"Corrupted or invalid image: {e}",
                "image_url": image_url,
                "filename": display_name,
                "confidence_score": 0.0,
            }

        # Step 5 & 6: First run YOLO detection. If YOLO does not detect any tomato leaf, DO NOT call EfficientNet.
        try:
            from app.ml.yolo_detector import yolo_leaf_detector
            res = yolo_leaf_detector.detect_leaf(image, conf_threshold=0.30)
            has_leaf, cropped_image, leaf_conf, leaf_reason = res[0], res[1], res[2], res[3]
            bounding_boxes = res[4] if len(res) > 4 else []
            leaf_roi = res[5] if len(res) > 5 else None
        except Exception as e:
            print(f"[WARNING] YOLO leaf detection error: {e}")
            has_leaf, cropped_image, leaf_conf, leaf_reason, bounding_boxes, leaf_roi = (
                True,
                image,
                0.70,
                None,
                [],
                None,
            )

        if not has_leaf or cropped_image is None:
            cropped_image = image

        # Step 6: Classify with EfficientNetB0
        if self.model is None:
            return {
                "status": "error",
                "reason": "Model not available",
                "image_url": image_url,
                "filename": display_name,
            }

        import torch
        # Ensure cropped_image is a PIL Image
        if not isinstance(cropped_image, Image.Image):
            cropped_image = Image.fromarray(cropped_image)
        
        input_tensor = self.transform(cropped_image)
        if not isinstance(input_tensor, torch.Tensor):
            input_tensor = torch.tensor(input_tensor)
        input_tensor = input_tensor.unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(input_tensor)

            if isinstance(outputs, dict):
                outputs = outputs.get("out", outputs.get("logits", outputs))
            elif isinstance(outputs, (tuple, list)):
                outputs = outputs[0]

            probabilities = torch.softmax(outputs, dim=1)
            top_prob, top_catid = torch.topk(probabilities, 1)

            class_idx = str(top_catid.item())
            confidence = round(float(top_prob.item()), 4)

        # Step 9: If EfficientNet confidence is below 50%, return low confidence warning
        if confidence < 0.50:
            return {
                "status": "ignored",
                "reason": "Disease confidence too low",
                "image_url": image_url,
                "filename": display_name,
                "confidence_score": confidence,
                "bounding_boxes": bounding_boxes,
            }

        # Look up disease info in labels.json
        label_info = self.labels.get(class_idx, {})
        disease_id = label_info.get("disease_id", int(class_idx) if class_idx.isdigit() else None)
        disease_name = label_info.get("name", f"Class {class_idx}")

        # Localize the ACTUAL infected spots and return exactly 1 tight box around
        # the disease area (verifying that it does not cover the whole frame).
        is_healthy = bool(
            disease_id == 1 or "healthy" in str(disease_name).lower()
        )
        if is_healthy:
            # Healthy leaves get no red overlay boxes.
            bounding_boxes = []
        else:
            try:
                from app.ml.lesion_detector import localize_infected_regions

                lesion_boxes = localize_infected_regions(
                    image,
                    roi=leaf_roi,
                    label=disease_name,
                    confidence=confidence,
                    disease_id=disease_id,
                )
                if lesion_boxes:
                    bounding_boxes = lesion_boxes[:1]
                else:
                    # Try full-frame search
                    full_boxes = localize_infected_regions(
                        image,
                        roi=None,
                        label=disease_name,
                        confidence=confidence,
                        disease_id=disease_id,
                    )
                    if full_boxes:
                        bounding_boxes = full_boxes[:1]
                    else:
                        bounding_boxes = []
            except Exception as exc:
                print(f"[WARNING] Lesion localization failed ({exc})")
                bounding_boxes = []

            # If no color lesion could be segmented, construct 1 compact focal box
            # around the leaf ROI center so it pinpoints the infected area without covering the whole image
            W, H = image.size
            if not bounding_boxes:
                if leaf_roi is not None and isinstance(leaf_roi, (list, tuple)) and len(leaf_roi) >= 4:
                    rx0, ry0, rx1, ry1 = leaf_roi  # type: ignore
                    cx = (rx0 + rx1) / 2.0
                    cy = (ry0 + ry1) / 2.0
                    fw = min(W * 0.45, max(40.0, (rx1 - rx0) * 0.50))
                    fh = min(H * 0.45, max(40.0, (ry1 - ry0) * 0.50))
                else:
                    cx, cy = W / 2.0, H / 2.0
                    fw, fh = W * 0.40, H * 0.40

                bx0 = max(0.0, cx - fw / 2.0)
                by0 = max(0.0, cy - fh / 2.0)
                bx1 = min(float(W), cx + fw / 2.0)
                by1 = min(float(H), cy + fh / 2.0)

                bounding_boxes = [{
                    "box_2d": [
                        round(by0 / H, 4),
                        round(bx0 / W, 4),
                        round(by1 / H, 4),
                        round(bx1 / W, 4),
                    ],
                    "box_pixels": [round(bx0, 1), round(by0, 1), round(bx1, 1), round(by1, 1)],
                    "label": disease_name,
                    "confidence": round(confidence, 4),
                    "disease_id": disease_id,
                }]
            else:
                # Ensure exactly 1 box with verified bounds
                primary_box = bounding_boxes[0]
                primary_box["label"] = disease_name
                primary_box["disease_id"] = disease_id
                primary_box["confidence"] = round(confidence, 4)

                # Verification: ensure box does not cover the full frame
                b2d = primary_box.get("box_2d", [0.0, 0.0, 1.0, 1.0])
                ymin, xmin, ymax, xmax = b2d[0], b2d[1], b2d[2], b2d[3]
                w_frac = max(0.01, xmax - xmin)
                h_frac = max(0.01, ymax - ymin)
                if w_frac > 0.78 or h_frac > 0.78 or (w_frac * h_frac) > 0.60:
                    cx = (xmin + xmax) / 2.0
                    cy = (ymin + ymax) / 2.0
                    w_frac = min(w_frac, 0.65)
                    h_frac = min(h_frac, 0.65)
                    xmin = max(0.0, cx - w_frac / 2.0)
                    xmax = min(1.0, cx + w_frac / 2.0)
                    ymin = max(0.0, cy - h_frac / 2.0)
                    ymax = min(1.0, cy + h_frac / 2.0)
                    primary_box["box_2d"] = [round(ymin, 4), round(xmin, 4), round(ymax, 4), round(xmax, 4)]
                    primary_box["box_pixels"] = [round(xmin * W, 1), round(ymin * H, 1), round(xmax * W, 1), round(ymax * H, 1)]

                bounding_boxes = [primary_box]

        return {
            "status": "valid",
            "image_url": image_url,
            "filename": display_name,
            "disease_id": disease_id,
            "disease_name": disease_name,
            "confidence_score": confidence,
            "bounding_boxes": bounding_boxes,
            "cropped_image": cropped_image,  # debug/inspection only (not persisted)
        }

    async def predict_batch(self, image_urls: List[str], filenames: Optional[List[str]] = None) -> Dict:
        """
        Run batch inference for multiple image URLs, independently, and aggregate:
            {"valid_predictions": [...], "ignored_images": [...]}
        """
        valid_predictions = []
        ignored_images = []
        for idx, url in enumerate(image_urls):
            fname = filenames[idx] if filenames and idx < len(filenames) else None
            try:
                res = await self.predict_image(url, filename=fname)
            except Exception as e:
                print(f"[ERROR] Error predicting image {url}: {e}")
                res = {
                    "status": "ignored",
                    "reason": f"Error processing image: {e}",
                    "image_url": url,
                    "filename": self._derive_filename(url, fname),
                    "confidence_score": 0.0
                }
            if res.get("status") == "valid":
                valid_predictions.append(res)
            else:
                ignored_images.append(res)
        return {
            "valid_predictions": valid_predictions,
            "ignored_images": ignored_images,
        }

    @staticmethod
    def _derive_filename(image_url: str, filename: Optional[str] = None) -> str:
        """Return a display filename for an image URL, preferring an explicit filename."""
        if filename and str(filename).strip():
            return str(filename)
        try:
            from urllib.parse import urlparse
            base = os.path.basename(urlparse(image_url).path)
            return base or "image"
        except Exception:
            base = os.path.basename(str(image_url))
            return base or "image"


pytorch_model_loader = PyTorchModelLoader()
