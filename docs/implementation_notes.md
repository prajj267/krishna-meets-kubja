# Implementation notes

## Source review

Primary source is Vedabase's English chapter page, Canto 10 Chapter 42. Chapter overview and translations for verses 1–12 were checked on 2026-10-16. The overview calls Kubjā Trivakrā and describes the ointment encounter, straightening, invitation and promise to visit. Verse mapping is in data/source_manifest.json. Scenic content and simplified dialogue are marked as adaptation.

## Media pipeline

The audio processor uses SciPy WAV I/O, polyphase resampling and a 2nd-order 80 Hz high-pass by default. This removes low frequencies but may also remove voice fundamentals; it is a filtering example, not an assured denoiser. Plots use STFT with NFFT=1024, overlap=768 (hop=256), Hann window, dB scale, frequency display to 10 kHz. No SNR estimate is made without noise-only material.

Video motion scales deterministically from 1.0 to 1.055 with a small alternating horizontal pan. Timeline boundaries are proportional to text word counts over supplied audio duration. This is not forced alignment; subtitle accuracy needs listening review. Audio outside 180–300 seconds is not stretched.

## Manual work / environment

No narration or finished illustrations are included. Student identity is placeholder text. Install dependencies and FFmpeg, record narration and supply twelve panel illustrations before expecting a finished illustrated movie. The environment check found Python unavailable (Windows could not access python.exe) and FFmpeg absent from PATH; therefore tests and deliverables could not be generated here. Rerun pytest and the pipeline after setup.

## Qualitative review checklist

Review story accuracy against the manifest; character design consistency; speech intelligibility; subtitle readability/timing; audio/video sync; respectful depiction; and child suitability. No review scores or listener feedback are prefilled.
