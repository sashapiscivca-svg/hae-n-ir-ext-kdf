---
license: mit
library_name: onnx
pipeline_tag: object-detection
tags:
  - search-and-rescue
  - thermal
  - infrared
  - lwir
  - drone
  - uav
  - tiny-object-detection
  - person-detection
  - edge-ai
  - raspberry-pi
  - real-time
  - knowledge-distillation
  - onnx
  - int8
datasets:
  - alexshynkarenk0/hae-thermal-sar-annotations
language:
  - en
  - uk
model-index:
  - name: hae-n-ir-ext-kdf
    results:
      - task:
          type: object-detection
          name: Person detection (thermal, aerial)
        dataset:
          type: wisard
          name: WiSARD thermal (held-out sites Karen, MtErie, Airfield)
        metrics:
          - type: ap50
            name: AP50 (int8, IoU 0.5, input x1.5)
            value: 0.202
      - task:
          type: object-detection
          name: Person detection (thermal, aerial)
        dataset:
          type: hit-uav
          name: HIT-UAV (test split)
        metrics:
          - type: ap50
            name: AP50 (int8, IoU 0.5, input x1.5)
            value: 0.580
      - task:
          type: object-detection
          name: Person detection (thermal, aerial)
        dataset:
          type: airesq
          name: AIResQ Benchmark (held-out groups)
        metrics:
          - type: ap50
            name: AP50 (int8, IoU 0.5, input x1.5)
            value: 0.188
---

# hae-n-ir-ext-kdf: real-time thermal person detector for search-and-rescue drones

**hae-n-ir-ext-kdf** finds people in thermal (LWIR) drone imagery. It is the real-time member of the [hae](https://github.com/sashapiscivca-svg/hae) family: 53,613 parameters, 0.052 GMAC per 256×320 tile (about 5× less than [hae-s-ir](https://huggingface.co/alexshynkarenk0/hae-s-ir)), a 123 KB int8 ONNX file. It was trained from scratch on five openly licensed civilian thermal datasets, with knowledge distillation from a larger hae teacher that we trained ourselves. Code and weights are MIT-licensed.

- **Live demo (runs in your browser, both models):** https://huggingface.co/spaces/alexshynkarenk0/hae-demo
- **Code:** model repository https://github.com/sashapiscivca-svg/hae-n-ir-ext-kdf (model card, recipe, examples, tests) · runtime and training package https://github.com/sashapiscivca-svg/hae
- Full model card (EN): https://github.com/sashapiscivca-svg/hae-n-ir-ext-kdf/blob/main/MODEL_CARD.md · (UK): https://github.com/sashapiscivca-svg/hae-n-ir-ext-kdf/blob/main/MODEL_CARD.uk.md
- Responsible use: https://github.com/sashapiscivca-svg/hae-n-ir-ext-kdf/blob/main/RESPONSIBLE_USE.md

> **Decision support only.** The model misses people and raises false alarms. Never use it as the only means of search, and never call off a search because it found nothing.

## When to use it

- **Use it** for live video on a Raspberry Pi Zero 2 W class computer, and for forest, meadow and trail footage similar to WiSARD (people around 25–30 px tall in 640×512 frames).
- **Prefer [hae-s-ir](https://huggingface.co/alexshynkarenk0/hae-s-ir)** for small, distant people (about 8–20 px) and for footage like HIT-UAV or AIResQ, and whenever you are unsure: it is the general model.

## Files

| File | Purpose |
|---|---|
| `hae-n-ir-ext-kdf_lwir_int8.onnx` | deployment (int8, fp32 head), 123 KB |
| `hae-n-ir-ext-kdf_lwir.onnx` | fp32 reference, 219 KB |
| `hae-n-ir-ext-kdf.safetensors` | PyTorch weights for fine-tuning with the `hae` package |
| `config.json` | architecture and full training recipe |
| `metrics.json` | all evaluation numbers, including threshold sweeps and both input scales |
| `SHA256SUMS` | checksums of the files above |

## Usage

```bash
pip install "hae[hub] @ git+https://github.com/sashapiscivca-svg/hae@v1.0.0"
```

```python
from huggingface_hub import hf_hub_download
from hae.detector import Detector
path = hf_hub_download("alexshynkarenk0/hae-n-ir-ext-kdf", "hae-n-ir-ext-kdf_lwir_int8.onnx", revision="v1.0.0")
det = Detector(path, threads=3)                # x1.0 scale and 0.55 threshold from the ONNX metadata
res = det.predict("thermal_frame.png")         # 8-bit grayscale, white-hot
det_small = Detector(path, scale=1.5)          # for small, distant people (slower: 2.25x the pixels)
```

hae v1.0.0 does not list this model by name, so pass the file path (or `root=` / `$HAE_MODELS` pointing at a folder `<root>/hae-n-ir-ext-kdf/`).

**Without the hae package:** the input `t` is float32 `(B,1,H,W)` with H and W multiples of 32. Normalise each frame as `(t − mean) / max(std, 1)` on the 0..255 scale (and resize if you use a scale other than ×1.0). The outputs are `cls` `(B,1,H/4,W/4)` logits and `box` `(B,4,H/4,W/4)`. Decode by taking 3×3 local maxima of `sigmoid(cls)`; each box is `softplus(box) × 4` around the cell centre `((j+0.5)·4, (i+0.5)·4)`. Then divide by the scale.

## Results (int8, IoU ≥ 0.5)

| Set | AP50 at ×1.0 (default) | AP50 at ×1.5 | hae-s-ir AP50 (×1.5 / ×1.0) |
|---|---:|---:|---:|
| WiSARD-IR val (held-out sites; 1,633 frames, 2,439 people) | 0.170 | **0.202** | 0.087 / 0.107 |
| HIT-UAV test (579 frames, 2,611 people) | 0.503 | 0.580 | **0.757** / 0.722 |
| AIResQ val (502 frames, 933 people, ~8 px tall) | 0.042 | 0.188 | **0.230** / 0.074 |
| AOS thermal val (218 frames, forest integral images) | **0.780** | 0.765 | 0.427 / 0.479 |
| RGB-LWIR Air val (20 frames) | 0.559 | 0.621 | 0.644 / **0.683** |

The default ×1.0 is the setting validated in real time on the Pi (2.25× fewer pixels than ×1.5); offline, ×1.5 is more accurate on four of these five sets, so use it when compute allows. WiSARD-IR val is **not** a transfer test for this model: other WiSARD sites (Baker, Carnation, FHL) are in its training data; the val sites (Karen, MtErie, Airfield) are not. For hae-s-ir it is a pure transfer test. One training run (a second seed of the same recipe scored 0.151 on WiSARD-IR val, 0.588 on HIT-UAV test and 0.146 on AIResQ val, fp32 at ×1.5), so treat differences below about 0.05 as noise.

**Real-time system test on a Raspberry Pi Zero 2 W.** Inside a separate real-time pipeline (tracker on every frame, detector in a background thread, candidate verification; these parts are not in hae), run on the device at a 10 fps camera pace on 17 unseen WiSARD thermal sequences (74 people episodes), this model found 0.743 of the people at 0.93 false alarms per minute, against 0.527 at 0.47 for an `s`-size model trained on the same data (its unreleased teacher), which was slower on the Pi. The model was chosen from six variants on the same sequences, so the absolute number is mildly optimistic.

**Speed.** A 256×320 int8 tile takes 55 ms on 1 thread and 25 ms on 4 threads of a Pi Zero 2 W (measured for hae-n-ir, which has the same architecture and int8 graph).

## Training data and licence

Trained on HIT-UAV trainval (CC0 1.0; 32 % of crops), AIResQ Benchmark train (CC BY 4.0; 16 %), WiSARD thermal, sites Baker/Carnation/FHL (MIT; 40 %), AOS thermal integral images (CC BY 4.0; 8 %) and the RGB-LWIR Labeled Dataset for Air-based platforms (CC BY 4.0; 4 %). Attribution: Suo et al., *Scientific Data* 10, 227 (2023); Büttner, *AIResQ Benchmark*, Zenodo doi:10.5281/zenodo.17405074 (CC BY 4.0); Broyles, Hayner, Leung, *IROS 2022*, WiSARD, MIT License, © 2022 Daniel Broyles, Christopher Hayner, Karen Leung; Kurmi & Bimber, Zenodo doi:10.5281/zenodo.6382373, from Schedl, Kurmi & Bimber, *Nature Machine Intelligence* 2, 783–790 (2020) (CC BY 4.0); Gallagher & Oughton, Zenodo doi:10.5281/zenodo.7465521, *Scientific Reports* 13, 8491 (2023) (CC BY 4.0). Changes made to each dataset are listed in [NOTICE.md](NOTICE.md). The distillation teacher is our own model, trained from scratch on the same data; no third-party weights were used. The model weights are released under the MIT License, © 2026 The hae authors.

## Citation

```bibtex
@software{hae_n_ir_ext_kdf_2026,
  title   = {hae-n-ir-ext-kdf: a real-time thermal person detector for search-and-rescue drones},
  author  = {{The hae authors}},
  year    = {2026},
  version = {1.0.0},
  license = {MIT},
  url     = {https://github.com/sashapiscivca-svg/hae-n-ir-ext-kdf}
}
```
