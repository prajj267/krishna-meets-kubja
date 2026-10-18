# Śrīmad Bhāgavatam Chitra-Katha — Kṛṣṇa Meets Kubjā

An offline-first Python academic project for speech and video processing. Student identity is configurable in `config.yaml`.

## Source status

Chapter 42 of Canto 10 was checked against [Vedabase](https://vedabase.io/en/library/sb/10/42/). Verses 1–12 cover the encounter with Trivakrā (also called Kubjā), her ointment offering, Kṛṣṇa straightening her body, her invitation, and His reply. Facts are mapped in `data/source_manifest.json`. Narration and dialogue are adaptations, not quotations. This episode stops at verse 12.

## Setup

Python 3.10+ recommended. FFmpeg is needed for MP4 rendering. In PowerShell:

```powershell
cd krishna-meets-kubja
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.pipeline --config config.yaml --stage all
```

Linux/macOS: `python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt`.

Provide 16:9 art as `assets/panels/panel_01.png` through `panel_12.png` for finished illustrations. Without artwork, layouts are generated with clearly identified text scene cards; they are not claimed as illustrations. Put a narration recording at `audio/original/narration.wav`. An optional separately recorded dialogue track may be placed at `audio/original/dialogue.wav`; it must be manually aligned and within 100 ms of the narration length. Audio is not supplied or synthesized. Missing prerequisites are reported honestly.

```powershell
python -m src.pipeline --config config.yaml --stage comic
python -m src.pipeline --config config.yaml --stage audio
python -m src.pipeline --config config.yaml --stage video
python -m src.pipeline --config config.yaml --stage evaluation
python -m src.pipeline --config config.yaml --stage report
python -m src.app
python -m pytest
```

Audio is truly resampled to 44.1 kHz mono; input is retained. A conservative Butterworth high-pass filter demonstrates filtering, not claimed noise reduction. No SNR is reported without a valid noise reference. Video uses deterministic Ken Burns motion, cross-fades, FFmpeg encoding, SRT and periodic frame extraction. Subtitle timing is estimated from narration word counts and requires manual review. Tests use synthetic fixtures and are not real-media evaluation. Outputs live under `output/` and `analysis/`.
