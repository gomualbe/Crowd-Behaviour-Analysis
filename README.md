# Crowd-Behaviour-Analysis

Real-time crowd counting and zone-level density analysis on live camera streams.

The application connects to one or more video sources (RTSP/HTTP), runs each frame
through a **CLIP-EBC (ViT-B/16)** crowd-counting model, and displays the selected
camera together with its real-time crowd estimate inside a PyQt6 desktop GUI. Beyond
a single total count, every frame is split into a **4×4 grid** so the people density
can be inspected zone by zone.

---

## How it works

```
camera_links.txt ─► live stream (OpenCV) ─► frame (resized to 224×224)
                                                  │
                                                  ▼
                                  CLIP-EBC ViT-B/16 (NWPU weights)
                                                  │
                                                  ▼
                                       density map (bilinear up-sampled)
                                          │                     │
                                          ▼                     ▼
                                   total head count       4×4 grid count
                                          │                     │
                                          └──────► PyQt6 GUI ◄───┘
```

- **`main.py`** — entry point. Builds the PyQt6 `MainWindow`, which shows a scrollable
  sidebar of cameras (loaded from `camera_links.txt`) on the left and the live,
  analyzed feed of the selected camera on the right.
- **`init_model.py`** — builds the CLIP-EBC model from the bundled config and loads the
  checkpoint. Backbone `clip_vit_b_16`, input size `224`, reduction `8`, prompt type
  `word`, deep VPT with 32 visual-prompt tokens. Config read from
  `models/clip_ebc/configs/reduction_8.json` → entry `["4"]["nwpu"]` (NWPU, truncation 4).
- **`test_crowd.py`** — standalone sanity check: runs the model on a sample image from
  `images/` and prints the total count plus the per-cell counts of the 4×4 grid.
- **`models/clip_ebc/`** — git **submodule** pointing to
  [`Yiming-M/CLIP-EBC`](https://github.com/Yiming-M/CLIP-EBC). It is **not** vendored
  in this repo and must be initialized explicitly (see below).
- **`ui/`** — PyQt6 interface code.

---

## Requirements

- Python **3.12.4**
- A working OpenCV video backend and the camera stream URLs you want to analyze.
- GPU optional: the code uses CUDA if available, otherwise it falls back to CPU.

---

## Installation

### 1. Clone the repository **with submodules**

The crowd-counting model lives in a submodule. A plain `git clone` leaves
`models/clip_ebc/` empty and the import in `init_model.py` will fail.

```bash
git clone --recurse-submodules https://github.com/gomualbe/Crowd-Behaviour-Analysis.git
cd Crowd-Behaviour-Analysis
```

If you already cloned without `--recurse-submodules`:

```bash
git submodule update --init --recursive
```

### 2. Create the environment

```bash
conda create -n Crowd-Behaviour-Analysis python=3.12.4
conda activate Crowd-Behaviour-Analysis
pip install -r requirements.txt
```

---

## Model weights (required — not included in the repo)

The model architecture is defined in code, but the **trained weights are not stored in
this repository**. `init_model.py` expects the file here:

```
models/checkpoints/best_mae.pth
```

This folder does **not** exist after cloning, so you must create it and drop the
checkpoint in.

### Where to get the weights

The weights are published, free and publicly, on the official CLIP-EBC release page:

➡️ **https://github.com/Yiming-M/CLIP-EBC/releases/tag/v1.0.0**

Download the asset corresponding to the **CLIP-EBC ViT-B/16 model trained on NWPU-Crowd**
(checkpoint folder `clip_vit_b_16_word_224_8_4_fine_1.0_dmcount`). This is the
configuration this project loads (`clip_vit_b_16`, prompt `word`, input `224`, reduction
`8`, truncation `4`, fine bins).

### Where to put them

```bash
mkdir -p models/checkpoints
# move/rename the downloaded checkpoint to:
#   models/checkpoints/best_mae.pth
```

> **Note on the filename.** `init_model.py` loads `best_mae.pth`. The official CLIP-EBC
> release ships two metrics for the NWPU ViT-B/16 model (`best_mae.pth` and
> `best_rmse.pth`). If your download only contains one of them, either rename it to
> `best_mae.pth` or change the `pth_file` line in `init_model.py` accordingly.

---

## Configuring the cameras

Edit `camera_links.txt` in the project root and add one camera stream URL per line.

- If a link does not produce video, try appending `/video` to the URL.

---

## Running

Once weights and `camera_links.txt` are in place:

```bash
python main.py
```

In the GUI:

- The left sidebar lists every camera from `camera_links.txt`. Scroll and click to
  switch the active camera.
- The right panel shows the selected feed (the first camera by default), which is also
  the feed analyzed in real time by the crowd-analysis system.

### Quick model check (no cameras needed)

```bash
python test_crowd.py
```

This runs the model on a sample image in `images/` and prints the total count and the
4×4 grid breakdown — useful to confirm the weights loaded correctly before wiring up
live streams.

---

## Project structure

```
Crowd-Behaviour-Analysis/
├── images/                  # sample frames (used by test_crowd.py)
├── models/
│   ├── clip_ebc/            # git submodule → Yiming-M/CLIP-EBC
│   └── checkpoints/         # YOU create this; put best_mae.pth here
├── ui/                      # PyQt6 interface
├── camera_links.txt         # one camera stream URL per line
├── init_model.py            # builds + loads the CLIP-EBC model
├── main.py                  # application entry point
├── test_crowd.py            # standalone model sanity check
└── requirements.txt
```

---

## Credits

This project builds on **CLIP-EBC** by Yiming Ma, Victor Sanchez and Tanaya Guha.

- Code & weights: <https://github.com/Yiming-M/CLIP-EBC>
- Paper: *CLIP-EBC: CLIP Can Count Accurately through Enhanced Blockwise Classification*,
  arXiv:2403.09281

```bibtex
@article{ma2024clip,
  title={CLIP-EBC: CLIP Can Count Accurately through Enhanced Blockwise Classification},
  author={Ma, Yiming and Sanchez, Victor and Guha, Tanaya},
  journal={arXiv preprint arXiv:2403.09281},
  year={2024}
}
```
