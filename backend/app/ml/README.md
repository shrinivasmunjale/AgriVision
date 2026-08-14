# How to Attach Your Custom PyTorch Model to AgriVision

This folder (`backend/app/ml/`) handles loading and running inference with your trained PyTorch model.

---

## Quick Setup Steps

### 1. Copy Your Trained Model Weights File
Place your trained model file into this directory (`backend/app/ml/`). Supported file names:
- `model.pt` or `model.pth`
- `best.pt` or `best.pth`
- `crop_disease_model.pt`

> **TorchScript (`.pt`) Recommended**:
> If possible, export/save your PyTorch model using TorchScript:
> ```python
> # In your training script:
> script_model = torch.jit.trace(model, sample_input)
> torch.jit.save(script_model, "backend/app/ml/model.pt")
> ```

---

### 2. Configure Class Labels (`labels.json`)
Edit `backend/app/ml/labels.json` to map your model's output index to the corresponding AgriVision disease ID and disease name:

```json
{
  "0": {
    "disease_id": 2,
    "name": "Early Blight"
  },
  "1": {
    "disease_id": 3,
    "name": "Late Blight"
  },
  "2": {
    "disease_id": 4,
    "name": "Bacterial Spot"
  },
  "3": {
    "disease_id": 5,
    "name": "Tomato Mosaic Virus"
  }
}
```

*Note: `disease_id` corresponds to the ID in the database `Disease` table so that automatic treatment recommendations (pesticides & fertilizers) are fetched for the farmer.*

---

### 3. Install PyTorch Dependencies
Make sure PyTorch and torchvision are installed in your backend environment:

```bash
pip install torch torchvision pillow
```

---

## How It Works at Runtime

1. When an image is uploaded and analyzed via `/api/v1/predictions/analyze`:
2. `MLInferenceService` detects your PyTorch model in `backend/app/ml/`.
3. The image is preprocessed (Resized to 224x224, converted to Tensor, normalized with ImageNet mean/std).
4. Model performs forward pass and outputs confidence score & disease class.
5. If no model file is present in `backend/app/ml/`, AgriVision safely defaults to Modal API or dev mock predictions.
