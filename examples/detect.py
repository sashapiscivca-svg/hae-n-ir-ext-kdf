"""Detect people in thermal frames with hae-n-ir-ext-kdf (needs the hae package >= 1.0.0; no PyTorch).

    python examples/detect.py examples/frames/1-hituav-night-60m.png
    python examples/detect.py path/to/frames/ --preset sensitive --scale 1.5 --save out/
"""
from __future__ import annotations

import argparse
from pathlib import Path

from hae.detector import Detector

MODEL = Path(__file__).resolve().parents[1] / "models" / "hae-n-ir-ext-kdf" / "hae-n-ir-ext-kdf_lwir_int8.onnx"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", help="an 8-bit grayscale (white-hot) thermal image or a folder of them")
    ap.add_argument("--preset", choices=["balanced", "sensitive"], default="balanced", help="balanced 0.55 or sensitive 0.45")
    ap.add_argument("--scale", type=float, default=None, help="input scale (default from the model: x1.0; x1.5 for small people)")
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--save", default=None, help="folder for annotated images")
    a = ap.parse_args()
    det = Detector(MODEL, preset=a.preset, scale=a.scale, threads=a.threads)   # presets and scale come from the ONNX metadata
    res = det.predict(a.source)
    for r in res if isinstance(res, list) else [res]:
        print(r.summary())
        for (x1, y1, x2, y2), s in zip(r.boxes, r.conf):
            print(f"  person {s:.2f} at ({x1:.0f},{y1:.0f})-({x2:.0f},{y2:.0f})")
        if a.save:
            Path(a.save).mkdir(parents=True, exist_ok=True)
            r.save(Path(a.save) / Path(r.path).name, thr=det.conf)


if __name__ == "__main__":
    main()
