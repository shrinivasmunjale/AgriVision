# Jupyter Notebooks Directory

You can save your Jupyter Notebook (`.ipynb`) files here!

### Exporting your trained model from Jupyter Notebook:

At the end of your Jupyter Notebook, export your model as TorchScript (`.pt`) or PyTorch weights (`.pth`):

```python
import torch

# Method A: Save as TorchScript .pt (RECOMMENDED)
model.eval()
dummy_input = torch.rand(1, 3, 224, 224)
traced_model = torch.jit.trace(model, dummy_input)
traced_model.save("../model.pt")

# Method B: Save model state dict
torch.save(model.state_dict(), "../model.pth")
```

Once saved to `backend/app/ml/model.pt`, AgriVision will automatically load and use your model for disease predictions!
