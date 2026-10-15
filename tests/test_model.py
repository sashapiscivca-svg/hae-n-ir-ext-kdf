"""The committed int8 model runs with the published hae package and gives the reference box counts on two HIT-UAV test frames (CC0)."""
import hashlib
from pathlib import Path

import pytest
from hae.detector import Detector
from hae.infer import read_metadata

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "models" / "hae-n-ir-ext-kdf"
INT8 = D / "hae-n-ir-ext-kdf_lwir_int8.onnx"
FRAMES = ROOT / "examples" / "frames"
# reference counts from the Python package (also matched by the in-browser demo)
EXPECTED = {"balanced": {"1-hituav-night-60m.png": 16, "3-hituav-night-100m-nadir.png": 12},
            "sensitive": {"1-hituav-night-60m.png": 20, "3-hituav-night-100m-nadir.png": 12}}


def test_checksums():
    for line in (D / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split()
        assert hashlib.sha256((D / name).read_bytes()).hexdigest() == digest, name


def test_metadata_is_read_by_hae():
    meta = read_metadata(INT8)
    assert meta["name"] == "hae-n-ir-ext-kdf" and meta["mode"] == "lwir" and meta["license"] == "MIT"
    assert (meta["recommended_scale"], meta["recommended_conf"], meta["sensitive_conf"]) == (1.0, 0.55, 0.45)
    for preset, conf in (("balanced", 0.55), ("sensitive", 0.45)):
        det = Detector(INT8, preset=preset)
        assert (det.mode, det.scale, det.conf, det.stride, det.tnorm) == ("lwir", 1.0, conf, 4, True)
    assert Detector("hae-n-ir-ext-kdf", root=ROOT / "models").path == INT8


@pytest.mark.parametrize("preset", ["balanced", "sensitive"])
def test_box_counts_on_hituav_frames(preset):
    det = Detector(INT8, preset=preset, threads=2)
    got = {name: len(det.predict(FRAMES / name)) for name in EXPECTED[preset]}
    assert got == EXPECTED[preset]
