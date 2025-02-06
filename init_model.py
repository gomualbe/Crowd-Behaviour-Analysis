import os
import json
import torch
# import torch.onnx
from models.clip_ebc.models import get_model

main_dir = os.path.abspath(os.path.dirname(__file__))
models_dir = os.path.join(main_dir, "models")
clip_dir = os.path.join(models_dir, "clip_ebc")
checkpoints_dir = os.path.join(models_dir, "checkpoints")
# onnx_model_path = os.path.join(main_dir, "onnx", "model.onnx")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model():
    with open(os.path.join(clip_dir, "configs", "reduction_8.json"), "r") as f:
        config = json.load(f)["4"]["nwpu"]
    bins = config["bins"]["fine"]
    anchor_points = config["anchor_points"]["fine"]["average"]
    bins = [(float(b[0]), float(b[1])) for b in bins]
    anchor_points = [float(p) for p in anchor_points]

    model = get_model(
        backbone="clip_vit_b_16",
        input_size=224,
        reduction=8,
        bins=bins,
        anchor_points=anchor_points,
        prompt_type="word",
        num_vpt=32,
        vpt_drop=0.0,
        deep_vpt=True
    )

    pth_file = "best_mae.pth" # NWPU dataset checkpoint
    checkpoint = torch.load(os.path.join(checkpoints_dir, pth_file), map_location=device)

    # If 'model_state_dict' is not present, just use the state_dict as is
    if "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)

    model = model.to(device)

    return model

# def init_onnx_model():
#     # Load model
#     model = load_model()
#     model.eval()
#
#     # Create a dummy input with the same device as the model
#     dummy_input = torch.randn(1, 3, 224, 224, dtype=torch.float32, device=device)
#
#     # Export the model
#     torch.onnx.export(
#         model,
#         dummy_input,
#         onnx_model_path,
#         verbose=True,
#         opset_version=14,
#         input_names=["input"],  # Name of input layer
#         output_names=["output"],  # Name of output layer
#         dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}  # Dynamic batch size
#     )
#     print("Model exported to ONNX format")

# if __name__ == "__main__":
#     init_onnx_model()
