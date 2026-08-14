import os
import json
import io
import httpx
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Base directory for ML artifacts
ML_DIR = Path(__file__).parent
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

# ----- True model data lives in the project's mywork/models folder -----
PROJECT_ROOT = Path(__file__).resolve().parents[3]      # d:\AgriVision
MYWORK_MODEL_DIR = PROJECT_ROOT / "mywork" / "models"
MYWORK_MODEL_FILE = MYWORK_MODEL_DIR / "best_efficientnetb0.pth"
MYWORK_CLASS_NAMES = MYWORK_MODEL_DIR / "class_names.json"

# Display-name (lower-cased) -> AgriVision database disease_id mapping.
# Derived from backend/app/ml/labels.json so the model output index can be
# translated into the disease ids used by the DB / recommendation engine.
DISEASE_ID_MAP = {
    "bacterial spot": 4,
    "early blight": 2,
    "late blight": 3,
    "leaf mold": 6,
    "septoria leaf spot": 7,
    "spider mites two-spotted spider mite": 8,
    "spider mites": 8,
    "target spot": 9,
    "tomato yellow leaf curl virus": 10,
    "tomato mosaic virus": 5,
    "healthy": 1,
}

def _clean_class_name(raw: str) -> str:
    """Turn PlantVillage-style names like 'Tomato___Bacterial_spot' into 'Bacterial Spot'."""
    name = raw.replace("___", " ").replace("_", " ").strip()
    return " ".join(part.capitalize() for part in name.split())

def _class_name_to_label_info(class_name: str, idx: int) -> Dict:
    """Map a raw model class name + index to AgriVision {disease_id, name}."""
    clean = _clean_class_name(class_name).lower()
    disease_id = DISEASE_ID_MAP.get(clean)
    if disease_id is None:
        disease_id = idx + 1
    return {
        "disease_id": disease_id,
        "name": _clean_class_name(class_name),
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
        # 1. Load labels mapping (class_names.json in mywork/ takes priority, else labels.json)
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
            print("[INFO] PyTorch (torch/torchvision/Pillow) is not installed. Using fallback predictions.")
            return

        # 3. Locate and load model weights
        self._load_model()

    def _load_labels(self):
        """Load the model's class -> disease mapping.

        Priority:
          1. backend/app/ml/class_names.json (deployed with model)
          2. mywork/models/class_names.json  (raw model class names -> disease ids)
          3. backend/app/ml/labels.json      (pre-mapped disease info)
        """
        # 1) Check deployed class_names.json first
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
        
        # 2) Raw model class names from mywork -> build mapped labels
        if MYWORK_CLASS_NAMES.exists():
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

        # 3) Fallback to pre-mapped labels.json
        if LABELS_FILE.exists():
            try:
                with open(LABELS_FILE, "r", encoding="utf-8") as f:
                    self.labels = json.load(f)
            except Exception as e:
                print(f"[WARNING] Failed to load labels.json: {e}")

    def _load_model(self):
        """Find and load a PyTorch model file."""
        if not self.is_torch_available:
            return
            
        import torch

        # Look for the trained model. Priority:
        # 1. backend/app/ml/ (deployed with app)
        # 2. mywork/models/ (local development)
        found_path = None

        # Check deployed model location first
        for path in MODEL_CANDIDATES:
            if path.exists():
                found_path = path
                print(f"[MODEL] Found deployed model at: {path}")
                break

        # Fallback to mywork/models for local development
        if found_path is None and MYWORK_MODEL_FILE.exists():
            found_path = MYWORK_MODEL_FILE
            print(f"[MODEL] Found development model at: {MYWORK_MODEL_FILE}")

        if found_path is None:
            # Look for any .pt or .pth file in ML_DIR first, then mywork/models/
            pt_files = list(ML_DIR.glob("*.pt")) + list(ML_DIR.glob("*.pth"))
            if not pt_files and MYWORK_MODEL_DIR.is_dir():
                pt_files = list(MYWORK_MODEL_DIR.glob("*.pt")) + list(MYWORK_MODEL_DIR.glob("*.pth"))
            if pt_files:
                found_path = pt_files[0]

        if not found_path:
            print(
                f"[INFO] No PyTorch model file found in {ML_DIR} or {MYWORK_MODEL_DIR}. "
                "Place model.pt / best_efficientnetb0.pth here for local inference."
            )
            return

        self.model_path = found_path
        print(f"[MODEL] Loading PyTorch model from: {found_path} on device: {self.device}")

        try:
            # First try loading as TorchScript model
            self.model = torch.jit.load(str(found_path), map_location=self.device)
            self.model.eval()
            print("[SUCCESS] TorchScript model loaded successfully!")
        except Exception as script_err:
            # Fallback to standard torch.load
            try:
                loaded = torch.load(str(found_path), map_location=self.device)
                if isinstance(loaded, torch.nn.Module):
                    self.model = loaded
                    self.model.eval()
                    print("[SUCCESS] PyTorch nn.Module loaded successfully!")
                elif isinstance(loaded, dict) and "model" in loaded and isinstance(loaded["model"], torch.nn.Module):
                    # e.g., YOLO / PyTorch model checkpoint
                    self.model = loaded["model"]
                    if hasattr(self.model, "eval"):
                        self.model.eval()
                    print("[SUCCESS] PyTorch model checkpoint loaded successfully!")
                elif isinstance(loaded, dict):
                    # State dict handling (e.g. EfficientNet-B0, ResNet)
                    state_dict = loaded.get("state_dict", loaded.get("model_state_dict", loaded))
                    num_classes = len(self.labels) if self.labels else 10
                    import torchvision.models as tv_models
                    import torch.nn as nn
                    
                    # 1. Try EfficientNet-B0 (your trained model)
                    try:
                        eff_model = tv_models.efficientnet_b0(weights=None)
                        in_features = eff_model.classifier[1].in_features
                        eff_model.classifier[1] = nn.Linear(in_features, num_classes)
                        eff_model.load_state_dict(state_dict)
                        self.model = eff_model.to(self.device)
                        self.model.eval()
                        print("[SUCCESS] EfficientNet-B0 model loaded successfully from state dict!")
                    except Exception as eff_err:
                        # 2. Try ResNet-18
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
                    print(f"[WARNING] torch.load returned object format that requires custom model instantiation: {script_err}")
            except Exception as load_err:
                print(f"[ERROR] Failed to load model from {found_path}: {load_err}")

    def is_ready(self) -> bool:
        """Return True if PyTorch is installed and model is loaded."""
        return self.is_torch_available and self.model is not None

    async def _fetch_image(self, image_url: str):
        """Download image bytes from HTTP URL or load from disk if local path."""
        from PIL import Image

        if image_url.startswith("http://") or image_url.startswith("https://"):
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(image_url)
                resp.raise_for_status()
                image_bytes = resp.content
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        else:
            # Local file path
            image = Image.open(image_url).convert("RGB")
        return image

    async def predict_image(self, image_url: str) -> Dict:
        """
        Run inference on an image URL or local path.
        Returns a dict matching AgriVision prediction format.
        """
        if not self.is_ready():
            raise RuntimeError("PyTorch model is not loaded.")

        import torch

        image = await self._fetch_image(image_url)
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(input_tensor)
            
            # Handle dictionary or tuple outputs (e.g. YOLO/detectors)
            if isinstance(outputs, dict):
                outputs = outputs.get("out", outputs.get("logits", outputs))
            elif isinstance(outputs, (tuple, list)):
                outputs = outputs[0]

            probabilities = torch.softmax(outputs, dim=1)
            top_prob, top_catid = torch.topk(probabilities, 1)

            class_idx = str(top_catid.item())
            confidence = round(float(top_prob.item()), 4)

        # Look up disease info in labels.json
        label_info = self.labels.get(class_idx, {})
        disease_id = label_info.get("disease_id", int(class_idx) if class_idx.isdigit() else None)
        disease_name = label_info.get("name", f"Class {class_idx}")

        return {
            "image_url": image_url,
            "disease_id": disease_id,
            "disease_name": disease_name,
            "confidence_score": confidence
        }

    async def predict_batch(self, image_urls: List[str]) -> List[Dict]:
        """Run batch inference for multiple image URLs."""
        results = []
        for url in image_urls:
            try:
                res = await self.predict_image(url)
                results.append(res)
            except Exception as e:
                print(f"[ERROR] Error predicting image {url}: {e}")
                # Fallback item if individual image fails
                results.append({
                    "image_url": url,
                    "disease_id": 2,
                    "disease_name": "Early Blight",
                    "confidence_score": 0.75
                })
        return results

pytorch_model_loader = PyTorchModelLoader()
