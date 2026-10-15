<div align="center">

# hae-n-ir-ext-kdf — a real-time thermal person detector for search-and-rescue drones

**A 54 k-parameter model that finds people in drone thermal video, fast enough for a $15 Raspberry Pi Zero 2 W.**

[Українська](README.uk.md) · [Model card](MODEL_CARD.md) · [Hugging Face](https://huggingface.co/alexshynkarenk0/hae-n-ir-ext-kdf) · [Live demo](https://huggingface.co/spaces/alexshynkarenk0/hae-demo) · [hae package](https://github.com/sashapiscivca-svg/hae) · [Responsible use](RESPONSIBLE_USE.md)

`weights: MIT` · `v1.0.0` · `runs with hae ≥ 1.0.0 or any ONNX runtime` · `int8 ONNX: 123 KB`

</div>

---

hae-n-ir-ext-kdf is the real-time member of the [hae](https://github.com/sashapiscivca-svg/hae) family of open thermal person detectors. It was trained from scratch on five openly licensed civilian thermal datasets, with knowledge distillation from a larger hae model that we trained ourselves. It needs about a fifth of the compute of the general model [hae-s-ir](https://github.com/sashapiscivca-svg/hae), and it is better than hae-s-ir on forest, meadow and trail footage like WiSARD, but worse on small, distant people.

> [!IMPORTANT]
> This is a **research release** and a **decision-support** tool. It misses people and raises false alarms (see [Limitations](#limitations)). Never use it as the only means of search, and never call off a search because it found nothing. Read [RESPONSIBLE_USE.md](RESPONSIBLE_USE.md) before deploying.

## Which model to use

| | **hae-s-ir** (in [hae](https://github.com/sashapiscivca-svg/hae)) — general | **hae-n-ir-ext-kdf** (this repository) — real-time |
|---|---|---|
| Best for | small, distant people; footage like HIT-UAV and AIResQ (open ground, roads, coast) | forest and wilderness footage like WiSARD; live video on a Raspberry Pi Zero 2 W |
| Parameters | 313,169 | 53,613 |
| Compute per 256×320 tile (×1.0) | 0.269 GMAC | 0.052 GMAC (5.2× less) |
| Default input scale | ×1.5 | ×1.0 |
| int8 ONNX | 383 KB | 123 KB |
| Training data | HIT-UAV, AIResQ | HIT-UAV, AIResQ, WiSARD (other sites), AOS thermal, RGB-LWIR Air; distilled from a larger hae teacher |

**Start with hae-s-ir** when you do not know your footage: it is more accurate on HIT-UAV, AIResQ and RGB-LWIR Air. **Pick hae-n-ir-ext-kdf** when you need live detection on a Pi Zero 2 W, or when your footage looks like WiSARD (people around 25–30 px tall in forest, meadows and trails): there, at each model's default scale, its AP50 is about twice that of hae-s-ir (0.170 vs 0.087; 0.170 vs 0.107 if both run at ×1.0). At its default ×1.0 it nearly fails on very small people (AIResQ, about 8 px); use `scale=1.5` or hae-s-ir for high-altitude search.

## Results

AP50, int8, IoU ≥ 0.5, the same splits for both models. Numbers come from the hae evaluation script (`scripts/evaluate.py`); per-threshold recall, precision and false alarms per frame are in [MODEL_CARD.md](MODEL_CARD.md#3-evaluation) and [`metrics.json`](models/hae-n-ir-ext-kdf/metrics.json).

| Evaluation set | hae-n-ir-ext-kdf ×1.0 (default) | hae-n-ir-ext-kdf ×1.5 | hae-s-ir ×1.5 (its default) | hae-s-ir ×1.0 |
|---|---:|---:|---:|---:|
| HIT-UAV test (579 frames, 2,611 people) | 0.503 | 0.580 | **0.757** | 0.722 |
| AIResQ val (502 frames, 933 people, ~8 px tall) | 0.042 | 0.188 | **0.230** | 0.074 |
| WiSARD-IR val (1,633 frames, 2,439 people) | 0.170 | **0.202** | 0.087 | 0.107 |
| AOS thermal val (218 frames, forest integral images) | **0.780** | 0.765 | 0.427 | 0.479 |
| RGB-LWIR Air val (20 frames) | 0.559 | 0.621 | 0.644 | **0.683** |

How to read this:

- **WiSARD-IR val is not a transfer test for this model.** Its sites (Karen, MtErie, Airfield) are held out, but other WiSARD sites are in its training data. For hae-s-ir, which never saw WiSARD, it is a pure transfer test. Part of the gain comes from that.
- AOS and RGB-LWIR Air val are the held-out splits of two datasets that only this model was trained on. On RGB-LWIR Air it is nevertheless worse than hae-s-ir; with 20 frames that set is only an indicator.
- ×1.0 is the default because it is the setting validated in real time on the Pi (below). Offline, ×1.5 is more accurate on four of the five sets, at 2.25× the compute.
- One training run. A second run of the same recipe scored about 0.05 lower on WiSARD-IR and AIResQ (fp32, ×1.5: 0.151 and 0.146 against 0.199 and 0.196), so these numbers are at the lucky end. The presets (0.55 / 0.45) and the int8 calibration were chosen on HIT-UAV test and AIResQ val.

## Real-time test on a Raspberry Pi Zero 2 W

The model was evaluated **inside a separate real-time system** that is not part of hae or of this repository: the detector in a background thread (int8, 3 threads, ×1.0), a tracker on every frame, candidate verification and a zoom re-check, fed at a live camera pace of 10 fps on the device. Data: 17 unseen WiSARD thermal sequences from the val sites (10,293 frames, 74 episodes in which a person is visible); the alarm threshold allows at most 2 false alarms per minute.

| Detector in that system | Found (recall) | False alarms per minute | Detector latency, median / p90 | Frames behind the camera, median / p90 |
|---|---:|---:|---:|---:|
| **hae-n-ir-ext-kdf** | **0.743** | 0.93 | 232 / 341 ms | 3 / 5 |
| hae-s-ir-ext (`s`, same data, its distillation teacher, not released) | 0.527 | 0.47 | 358 / 472 ms | 5 / 6 |
| hae-n-ir-ext (`n`, same data, no distillation, not released) | 0.541 | 0.82 | 168 / 310 ms | 2 / 4 |

Paired bootstrap over sequences: +0.216 against hae-s-ir-ext (95 % CI +0.04 to +0.42), +0.203 against hae-n-ir-ext (0.00 to +0.37). The `s` model lost mainly because it was slower on the Pi and fell further behind the camera.

Caveats: this measures a system, and the tracker, verification and zoom are **not part of hae**. The released hae-s-ir was **not** in this test. The model was picked from six variants on these same sequences, each run once, so 0.743 is mildly optimistic (about ±0.05 is noise with 74 episodes). Without the zoom re-check it scored 0.649 at 0.87 false alarms per minute. The system's thresholds were tuned for the `s` model. Not tested: a real camera in flight, long flights, daylight-heavy footage beyond WiSARD.

**Bare latency** of the same architecture and int8 graph (measured for hae-n-ir on a Pi Zero 2 W; these weights were not benchmarked separately): 55 ms per 256×320 tile on 1 thread, 25 ms on 4 threads; a full 640×512 frame at ×1.5 takes 585 / 281 ms, and ×1.0 has 2.25× fewer pixels.

## Quick start

The model runs with the published [hae](https://github.com/sashapiscivca-svg/hae) package v1.0.0 (runtime only: numpy, onnxruntime, opencv, onnx, pillow; no PyTorch). hae v1.0.0 does not list this model among its released names, so give it the file path or the folder:

```bash
pip install "hae @ git+https://github.com/sashapiscivca-svg/hae@v1.0.0"
git clone https://github.com/sashapiscivca-svg/hae-n-ir-ext-kdf && cd hae-n-ir-ext-kdf
python examples/detect.py examples/frames/1-hituav-night-60m.png          # 16 people at the balanced preset
hae predict models/hae-n-ir-ext-kdf/hae-n-ir-ext-kdf_lwir_int8.onnx path/to/frames/ --json
HAE_MODELS=models hae predict hae-n-ir-ext-kdf frame.png --preset sensitive   # by name, via the models folder
```

```python
from hae.detector import Detector

det = Detector("models/hae-n-ir-ext-kdf/hae-n-ir-ext-kdf_lwir_int8.onnx", threads=3)   # x1.0 and threshold 0.55 from the ONNX metadata
det = Detector("hae-n-ir-ext-kdf", root="models", preset="sensitive")                  # the same by name; threshold 0.45
det = Detector("models/hae-n-ir-ext-kdf/hae-n-ir-ext-kdf_lwir_int8.onnx", scale=1.5)   # small, distant people (2.25x compute)
res = det.predict("frame.png")       # 8-bit grayscale, white-hot; also a numpy array, a folder or a list
print(res.summary(), res.boxes, res.conf)
```

hae v1.0.0 reads everything it needs from this model's ONNX metadata (mode, normalisation, stride, scale ×1.0, presets 0.55 / 0.45); this was checked in a clean environment installed from the v1.0.0 tag. Without cloning, fetch the file from the Hugging Face Hub (needs `pip install huggingface_hub`):

```python
from huggingface_hub import hf_hub_download
from hae.detector import Detector
path = hf_hub_download("alexshynkarenk0/hae-n-ir-ext-kdf", "hae-n-ir-ext-kdf_lwir_int8.onnx", revision="v1.0.0")
det = Detector(path)
```

`hae download hae-n-ir-ext-kdf` (with `pip install "hae[hub] @ git+https://github.com/sashapiscivca-svg/hae@v1.0.0"`) also downloads it and prints the path, but in v1.0.0 `Detector("hae-n-ir-ext-kdf")` without a path, `root` or `$HAE_MODELS` does not look it up on the Hub. Any other ONNX runtime works too; the input/output contract is in the [hae inference guide](https://github.com/sashapiscivca-svg/hae/blob/main/docs/en/inference.md#the-onnx-contract-for-c-rust-java-mobile-) (use ×1.0 instead of ×1.5).

## Files

| File | Purpose |
|---|---|
| `models/hae-n-ir-ext-kdf/hae-n-ir-ext-kdf_lwir_int8.onnx` | deployment model (int8, fp32 head), 123 KB |
| `models/hae-n-ir-ext-kdf/hae-n-ir-ext-kdf_lwir.onnx` | fp32 reference, 219 KB |
| `models/hae-n-ir-ext-kdf/hae-n-ir-ext-kdf.safetensors` | PyTorch weights for fine-tuning with the hae training code |
| `models/hae-n-ir-ext-kdf/config.json` | architecture and full training recipe |
| `models/hae-n-ir-ext-kdf/metrics.json` | all evaluation numbers: both scales, threshold sweeps, comparison, Pi test |
| `models/hae-n-ir-ext-kdf/SHA256SUMS` | checksums (`cd models/hae-n-ir-ext-kdf && sha256sum -c SHA256SUMS`) |
| `configs/hae-n-ir-ext-kdf.yaml` | training recipe in the format of hae's `scripts/train.py` |
| `examples/detect.py`, `examples/frames/` | a minimal example and two HIT-UAV test frames (CC0 1.0) |

## Training and reproduction

[`configs/hae-n-ir-ext-kdf.yaml`](configs/hae-n-ir-ext-kdf.yaml) records the exact recipe (90 epochs from scratch, five datasets, distillation settings) and works with hae's `scripts/train.py`. Reproduction is partial for now: hae's `prepare_data.py` builds the HIT-UAV, AIResQ and WiSARD sets but not AOS and RGB-LWIR Air, and the teacher is not released. The recipe file explains how to train your own teacher. Training took about 38 minutes of steps on one NVIDIA T4.

## Limitations
- **int8 on x86 CPUs without VNNI.** On an AMD EPYC 7763 (AVX2 only) the int8 model found 13 people instead of 16 on a test frame with the balanced preset (sensitive: identical); on CPUs with AVX512-VNNI and in fp32 the counts are identical. This is how ONNX Runtime's int8 kernels behave without VNNI (u8×s8 products can saturate). On such PCs use the fp32 file `hae-n-ir-ext-kdf_lwir.onnx` (224 KB, fast enough on a PC). The Raspberry Pi (ARM) numbers above were measured with the int8 model on the Pi itself.

- **Very small people.** At ×1.0, AP50 is 0.042 on AIResQ (people about 8 px). Use ×1.5 or hae-s-ir for high-altitude search.
- **Open ground.** On HIT-UAV test it is 0.18–0.25 AP50 below hae-s-ir.
- **Forest is still hard.** On WiSARD-IR val, AP50 is 0.170 at ×1.0; most single frames miss people under trees. Combine detections over time.
- **Domain shift.** Thermal detectors do not transfer reliably between cameras, altitudes and seasons. Validate on your own footage and fine-tune if you can.
- **Daylight, false alarms, one class**, untested conditions (dense rubble, crowds, heavy rain or fog, radiometric 14/16-bit input, colour palettes): as for hae-s-ir, see the [hae limitations](https://github.com/sashapiscivca-svg/hae#limitations).

## License

- **Model weights and the files in this repository:** [MIT](LICENSE).
- **Training data:** five civilian datasets under CC0 1.0, CC BY 4.0 and MIT; attribution in [NOTICE.md](NOTICE.md). The two example frames are HIT-UAV test frames (CC0 1.0; Suo et al., Scientific Data 2023).
- We ask, without any legal force, that the model be used for saving lives. See [RESPONSIBLE_USE.md](RESPONSIBLE_USE.md).

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

Please also cite hae and the datasets ([NOTICE.md](NOTICE.md) lists the references).
