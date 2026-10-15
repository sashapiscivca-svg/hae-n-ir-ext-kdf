# Changelog

All notable changes to this model repository are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This repository is versioned on its own, starting at 1.0.0; the [hae](https://github.com/sashapiscivca-svg/hae) package has its own versions. Released weights are never changed in place: new weights get a new version.

## [1.0.0] — 2026-10-15

First public release.

- `hae-n-ir-ext-kdf`: real-time thermal person detector, 53,613 parameters, 0.052 GMAC per 256×320 tile, 123 KB int8 ONNX. Trained from scratch for 90 epochs on HIT-UAV, AIResQ, WiSARD thermal (train sites), AOS thermal integral images and RGB-LWIR Air, with knowledge distillation from our own unreleased `s`-size teacher. Default scale ×1.0, presets 0.55 (balanced) / 0.45 (sensitive).
- ONNX fp32 and int8 (fp32 head), PyTorch safetensors, `config.json`, `metrics.json`, `SHA256SUMS`; recipe `configs/hae-n-ir-ext-kdf.yaml`.
- Works with the published hae package v1.0.0 by file path or by name with `root=` / `$HAE_MODELS`; CI checks box counts on two HIT-UAV test frames with that package.
- Model card (EN, UK), README (EN, UK), NOTICE with attribution for all five datasets, responsible-use statement.
