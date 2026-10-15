# Model card: hae-n-ir-ext-kdf v1.0.0

[Українська](MODEL_CARD.uk.md) · [README](README.md)

This card follows the structure of *Model Cards for Model Reporting* (Mitchell et al., 2019). hae-n-ir-ext-kdf is the real-time member of the [hae](https://github.com/sashapiscivca-svg/hae) family of thermal person detectors for search-and-rescue drones; the general model is [hae-s-ir](https://github.com/sashapiscivca-svg/hae/blob/main/MODEL_CARD.md). Both are compared on the same splits below.

## 1. Model details

Machine-readable numbers: [`models/hae-n-ir-ext-kdf/metrics.json`](models/hae-n-ir-ext-kdf/metrics.json). Recipe: [`models/hae-n-ir-ext-kdf/config.json`](models/hae-n-ir-ext-kdf/config.json), [`configs/hae-n-ir-ext-kdf.yaml`](configs/hae-n-ir-ext-kdf.yaml).

| | |
|---|---|
| Release | v1.0.0 of this model repository, 2026-10-15; runs with the hae package ≥ 1.0.0 |
| Model type | as hae-s-ir: single-stage, anchor-free, dense detector, one class (`person`), output stride 4; size `n` with a finer stem |
| Input | Thermal (LWIR) 8-bit grayscale frame, per-frame z-score, **default scale ×1.0**. ×1.0 is the setting tested in real time on the Pi (2.25× fewer pixels than ×1.5); ×1.5, the training-time evaluation scale, is more accurate on HIT-UAV, AIResQ, WiSARD-IR and RGB-LWIR Air (section 3), so use it when compute allows or people are small |
| Size | 53,613 parameters; 0.052 GMAC per 256×320 tile (×1.0), 5.2× less than hae-s-ir; 123 KB int8 ONNX, 219 KB fp32 ONNX |
| Initialisation | Random. No pretrained or third-party weights. |
| Presets | balanced 0.55, sensitive 0.45 (chosen at ×1.5 on HIT-UAV test and AIResQ val, as for hae-s-ir) |
| Training compute | One NVIDIA T4, 90 epochs (about 38 min of training steps) |
| Licence | MIT |

**Training.** Same loss, optimiser, crop size, schedule and augmentation as hae-s-ir ([hae model card, section 1](https://github.com/sashapiscivca-svg/hae/blob/main/MODEL_CARD.md#1-model-details)), 90 epochs from scratch. Crops come from five datasets: HIT-UAV trainval 32 %, AIResQ train 16 %, WiSARD thermal train sites (Baker, Carnation, FHL) 40 %, AOS thermal integral images train 8 %, RGB-LWIR Air train 4 % (data details: [hae DATA_CARD.md](https://github.com/sashapiscivca-svg/hae/blob/main/DATA_CARD.md) and [NOTICE.md](NOTICE.md)). The weights are not tuned; they were set before the run.

**Knowledge distillation.** A frozen teacher of size `s` (313 k parameters, the hae-s-ir architecture), trained by us from scratch for 90 epochs on the same five-dataset mix without distillation, sees each crop upscaled ×1.333. The student's classification target is the maximum of the ground-truth IoU target and the teacher's score (weight 0.5 against the plain loss); box regression is also pulled towards the teacher's boxes where the teacher is confident (weight 0.3); cells near small teacher detections get double weight; and the student's stride-4 features imitate the teacher's (foreground and background weighted separately). The teacher (internally hae-s-ir-ext) is not released, because it is worse than hae-s-ir on HIT-UAV and AIResQ and worse than this student on WiSARD-IR; the recipe file names a placeholder path for it.

**Quantisation.** As for hae-s-ir, with the final head in fp32. Calibration used 256 AIResQ train tiles at ×1.5; calibrating on HIT-UAV + AIResQ instead lost up to 0.054 AP50 and was rejected (the choice was made on HIT-UAV test and AIResQ val). AP50 changes by −0.008 to +0.003 relative to fp32.

## 2. Intended use

The same as hae-s-ir ([hae model card, section 2](https://github.com/sashapiscivca-svg/hae/blob/main/MODEL_CARD.md#2-intended-use)): decision support for civilian search and rescue; out of scope are weapons, targeting, surveillance or tracking of people without consent, identifying individuals and sole-source life-critical decisions (see [RESPONSIBLE_USE.md](RESPONSIBLE_USE.md)). With this emphasis: live detection on a Raspberry Pi Zero 2 W class computer, and footage of forest, meadows and trails where people appear around 25–30 px tall (as in WiSARD). For small, distant people (AIResQ-like, about 8 px) use hae-s-ir, or at least ×1.5.

## 3. Evaluation

Matching is greedy and class-agnostic at IoU ≥ 0.5, detections inside ignore regions are not counted as false alarms, and AP50 is COCO-style AP at IoU 0.5, as in the [hae model card](https://github.com/sashapiscivca-svg/hae/blob/main/MODEL_CARD.md#4-metrics). **WiSARD-IR val is not a transfer test for this model**: its sites (Karen, MtErie, Airfield) are held out, but other WiSARD sites are in its training data, so this is in-dataset generalisation to new sites with the same kind of cameras. `aos_val` and `lwir_air_val` are the held-out splits of the two smaller new datasets (218 and 20 frames).

AP50, int8, on the same splits for both models (WiSARD, AOS and RGB-LWIR Air numbers of hae-s-ir and all ×1.0 numbers were computed for this release with hae's `scripts/evaluate.py`; the others come from the evaluation made when the model was exported, and the same script reproduces them exactly):

| Set | hae-n-ir-ext-kdf ×1.0 (default) | hae-n-ir-ext-kdf ×1.5 | hae-s-ir ×1.5 (default) | hae-s-ir ×1.0 |
|---|---:|---:|---:|---:|
| HIT-UAV test | 0.503 | 0.580 | **0.757** | 0.722 |
| AIResQ val | 0.042 | 0.188 | **0.230** | 0.074 |
| WiSARD-IR val | 0.170 | 0.202 | 0.087 | 0.107 |
| AOS thermal val | 0.780 | 0.765 | 0.427 | 0.479 |
| RGB-LWIR Air val (20 frames) | 0.559 | 0.621 | 0.644 | 0.683 |

Operator metrics of hae-n-ir-ext-kdf (int8):

| Set | Scale | AP50 | Preset | Recall | Precision | F1 | FP per frame |
|---|---|---:|---|---:|---:|---:|---:|
| HIT-UAV test | ×1.0 | 0.503 | balanced 0.55 | 0.427 | 0.698 | 0.530 | 0.83 |
|  |  |  | sensitive 0.45 | 0.552 | 0.573 | 0.562 | 1.86 |
|  | ×1.5 | 0.580 | balanced 0.55 | 0.525 | 0.690 | 0.596 | 1.06 |
|  |  |  | sensitive 0.45 | 0.634 | 0.551 | 0.590 | 2.32 |
| AIResQ val | ×1.0 | 0.042 | balanced 0.55 | 0.106 | 0.161 | 0.128 | 1.03 |
|  |  |  | sensitive 0.45 | 0.170 | 0.105 | 0.130 | 2.71 |
|  | ×1.5 | 0.188 | balanced 0.55 | 0.289 | 0.247 | 0.267 | 1.64 |
|  |  |  | sensitive 0.45 | 0.427 | 0.160 | 0.233 | 4.16 |
| WiSARD-IR val | ×1.0 | 0.170 | balanced 0.55 | 0.217 | 0.315 | 0.257 | 0.71 |
|  |  |  | sensitive 0.45 | 0.311 | 0.257 | 0.281 | 1.34 |
|  | ×1.5 | 0.202 | balanced 0.55 | 0.225 | 0.353 | 0.275 | 0.61 |
|  |  |  | sensitive 0.45 | 0.295 | 0.201 | 0.239 | 1.75 |
| AOS thermal val | ×1.0 | 0.780 | balanced 0.55 | 0.471 | 0.934 | 0.626 | 0.19 |
|  |  |  | sensitive 0.45 | 0.620 | 0.882 | 0.728 | 0.47 |
|  | ×1.5 | 0.765 | balanced 0.55 | 0.503 | 0.895 | 0.644 | 0.33 |
|  |  |  | sensitive 0.45 | 0.668 | 0.827 | 0.739 | 0.79 |
| RGB-LWIR Air val (20 frames) | ×1.0 | 0.559 | balanced 0.55 | 0.443 | 0.628 | 0.519 | 1.60 |
|  |  |  | sensitive 0.45 | 0.672 | 0.491 | 0.567 | 4.25 |
|  | ×1.5 | 0.621 | balanced 0.55 | 0.639 | 0.557 | 0.595 | 3.10 |
|  |  |  | sensitive 0.45 | 0.795 | 0.369 | 0.504 | 8.30 |

**The trade-off.** Against hae-s-ir at their default scales, hae-n-ir-ext-kdf gains 0.083 AP50 on WiSARD-IR val and loses 0.254 on HIT-UAV test and 0.188 on AIResQ val; at ×1.5 the losses shrink to 0.177 and 0.042. At ×1.5 it gains 0.115 on WiSARD-IR val; at ×1.0 for both models, 0.063. Part of the WiSARD gain comes from training on other WiSARD sites; hae-s-ir never saw WiSARD. It is also much better on AOS val (0.780 vs 0.427), whose training split it saw. On RGB-LWIR Air val it is **worse** than hae-s-ir (0.559 vs 0.644) although it saw that dataset in training; with 20 frames this set is only an indicator.

**Variation between runs.** One training run (seed 0). A second run of the same recipe (seed 1, fp32, ×1.5) scored 0.588 on HIT-UAV test, 0.146 on AIResQ val, 0.151 on WiSARD-IR val, 0.729 on AOS val and 0.682 on RGB-LWIR Air val, against 0.581, 0.196, 0.199, 0.753 and 0.619 for the released run. The released run is the better one on AIResQ and WiSARD-IR by about 0.05, so expect retraining to land lower there. The same recipe without distillation (two seeds) scored 0.556–0.567 / 0.096–0.136 / 0.124–0.160 on HIT-UAV / AIResQ / WiSARD-IR.

## 4. Real-time evaluation on a Raspberry Pi Zero 2 W

This test measures a **system**, not hae alone. A separate real-time pipeline (not part of hae or of this repository) ran on the device: the detector in a background thread (int8, 3 threads, ×1.0), a tracker on every frame, a candidate verification stage and a zoom re-check. Frames were fed at a live camera pace of 10 fps, so frames that arrive while the detector is busy are skipped. Data: 17 WiSARD thermal sequences from the val sites (Karen 6, Airfield 8, MtErie 3; 10,293 frames, 74 episodes in which a person is visible). An episode counts as found if the system raises an alarm on that person; the alarm threshold allows at most 2 false alarms per minute.

| Detector in the pipeline | Found (recall) | False alarms per minute | Detector latency median / p90 | Frames behind the camera, median / p90 |
|---|---:|---:|---:|---:|
| **hae-n-ir-ext-kdf** | **0.743** | 0.93 | 232 / 341 ms | 3 / 5 |
| hae-s-ir-ext (`s`, same data as hae-n-ir-ext-kdf, not released) | 0.527 | 0.47 | 358 / 472 ms | 5 / 6 |
| hae-n-ir-ext (`n`, same data, no distillation, not released) | 0.541 | 0.82 | 168 / 310 ms | 2 / 4 |

Paired bootstrap over sequences (5,000 resamples): hae-n-ir-ext-kdf minus hae-s-ir-ext +0.216 (95 % CI +0.04 to +0.42); minus hae-n-ir-ext +0.203 (0.00 to +0.37). Board temperature stayed at or below 68.8 °C with no throttling. Detector latency here includes the pipeline's per-candidate verification, so it is longer than a bare hae call.

Caveats: the released hae-s-ir was **not** in this test, so this is not a hae-s-ir comparison. The model was picked from six variants (three detectors, with and without the zoom re-check) on these same sequences, and each variant ran once, so 0.743 is mildly optimistic; about ±0.05 is noise with 74 episodes. Without the zoom re-check the same model scored 0.649 at 0.87 false alarms per minute. The pipeline's thresholds were tuned for the `s` model, not for this one. Not tested: a real camera in flight, flights longer than two minutes per sequence, daylight-heavy footage beyond WiSARD.

**Bare latency.** A 256×320 int8 tile takes 55 ms on 1 thread and 25 ms on 4 threads of a Pi Zero 2 W, and a full 640×512 frame at ×1.5 takes 585 ms / 281 ms. These were measured for hae-n-ir, which has the same architecture and the same int8 graph (213 nodes, 53,613 parameters); this model's weights were not benchmarked separately. At ×1.0 a frame has 2.25× fewer pixels than at ×1.5.

## 5. Limitations specific to this model

- **Very small people.** At its default ×1.0 it almost fails on AIResQ (AP50 0.042, people about 8 px). Use ×1.5 or hae-s-ir for high-altitude search.
- **Worse than hae-s-ir on open ground.** On HIT-UAV test it loses 0.18–0.25 AP50.
- **WiSARD is still hard.** Its AP50 on WiSARD-IR val is 0.170 at ×1.0 (0.202 at ×1.5): most single frames miss people under trees. Its advantage shows most when detections are combined over time.
- **AOS training images are synthetic-aperture integrals**, not single frames, and the RGB-LWIR Air frames were converted from a colour palette. Their val splits are small (218 and 20 frames).
- **Reproduction is partial.** The teacher is not released, the AOS and RGB-LWIR Air converters are not in this repository, and the annotations of the AOS, RGB-LWIR Air and WiSARD train splits are not published (hae's `scripts/prepare_data.py wisard-ir` builds a WiSARD train split with its own converter, not aligned to a published file).

## 6. Ethical considerations

- **Missed people cost lives; false alarms cost time.** Neither error rate is low enough for autonomous decisions. Always keep a human in the loop and never treat "no detection" as "no person".
- **Dual use.** A person detector for aerial imagery could be misused for surveillance or targeting. We release it because the life-saving value for under-resourced rescue teams is high and the capability is already widely available. [RESPONSIBLE_USE.md](RESPONSIBLE_USE.md) states the uses we ask people to refrain from. The MIT licence itself does not restrict use.
- **Privacy.** The model outputs boxes, not identities. Drone footage of people is still personal data in many jurisdictions. Follow local law and SAR protocols on recording and retention.

## 7. Caveats and recommendations

1. Validate on footage from **your** camera, altitude and terrain before an operation. The hae package's `scripts/evaluate.py` works on any COCO-annotated set.
2. Fine-tune from `hae-n-ir-ext-kdf.safetensors` (with the hae training code) if you have a few hundred labelled frames from your sensor.
3. Pick the threshold for your tolerance of false alarms; `sensitive` (0.45) finds more people and raises more false alarms.
4. Confirm detections over time, with a tracker or by requiring persistence across frames or passes, before alerting.
5. Keep ×1.0 for live video on a Pi; use ×1.5 when compute allows or people are small; use hae-s-ir for high-altitude search.
6. On a Pi Zero 2 W, fit a heatsink, use the int8 model with 3 threads, and run the detector asynchronously or every K frames with tracking in between.
