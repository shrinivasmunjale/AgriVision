import os
import json
import argparse
from pathlib import Path

def train_and_export_model(dataset_dir: str, epochs: int = 5, batch_size: int = 16, lr: float = 0.001):
    """
    Train a PyTorch crop disease classification model on a custom dataset
    and automatically export 'model.pt' & 'labels.json' for AgriVision.
    
    Dataset structure expected:
    dataset_dir/
      ├── Early_Blight/
      │   ├── img1.jpg
      │   └── img2.jpg
      ├── Late_Blight/
      │   ├── img1.jpg
      │   └── img2.jpg
      └── Healthy/
          └── img1.jpg
    """
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
        from torch.utils.data import DataLoader
        from torchvision import datasets, models, transforms
    except ImportError:
        print("[ERROR] PyTorch and torchvision are required. Install with: pip install torch torchvision pillow")
        return

    dataset_path = Path(dataset_dir)
    if not dataset_path.exists():
        print(f"[ERROR] Dataset directory '{dataset_dir}' does not exist.")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[INFO] Using device: {device}")

    # Image transformations
    data_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    print(f"[INFO] Loading dataset from: {dataset_path}")
    dataset = datasets.ImageFolder(root=str(dataset_path), transform=data_transforms)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    class_names = dataset.classes
    num_classes = len(class_names)
    print(f"[INFO] Found {num_classes} classes: {class_names}")

    # Load pre-trained ResNet18 model
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    print(f"[TRAIN] Starting training for {epochs} epochs...")
    model.train()
    for epoch in range(epochs):
        running_loss = 0.0
        corrects = 0

        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            corrects += torch.sum(preds == labels.data)

        epoch_loss = running_loss / len(dataset)
        epoch_acc = corrects.double() / len(dataset)
        print(f"Epoch {epoch+1}/{epochs} - Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")

    # Export model to TorchScript format (.pt)
    output_dir = Path(__file__).parent
    model_output_path = output_dir / "model.pt"
    labels_output_path = output_dir / "labels.json"

    print("[EXPORT] Exporting model to TorchScript format...")
    model.eval()
    model_cpu = model.to("cpu")
    dummy_input = torch.rand(1, 3, 224, 224)
    traced_script_module = torch.jit.trace(model_cpu, dummy_input)
    traced_script_module.save(str(model_output_path))
    print(f"[SUCCESS] Model saved to: {model_output_path}")

    # Default mapping for AgriVision seed disease IDs
    disease_id_map = {
        "healthy": 1,
        "early blight": 2,
        "late blight": 3,
        "bacterial spot": 4,
        "mosaic virus": 5,
        "tomato mosaic virus": 5,
        "leaf mold": 6,
        "septoria leaf spot": 7,
        "spider mites": 8,
        "target spot": 9,
        "yellow leaf curl virus": 10,
    }

    labels_map = {}
    for idx, name in enumerate(class_names):
        clean_name = name.replace("_", " ").title()
        disease_id = disease_id_map.get(clean_name.lower(), idx + 1)
        labels_map[str(idx)] = {
            "disease_id": disease_id,
            "name": clean_name
        }

    with open(labels_output_path, "w", encoding="utf-8") as f:
        json.dump(labels_map, f, indent=2)
    print(f"[SUCCESS] Class labels saved to: {labels_output_path}")

    print("[SUCCESS] Training and export complete! AgriVision backend will now automatically use this model for predictions.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train custom PyTorch model for AgriVision")
    parser.add_argument("--dataset", type=str, required=True, help="Path to dataset directory with class subfolders")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    
    args = parser.parse_args()
    train_and_export_model(args.dataset, args.epochs, args.batch_size, args.lr)
