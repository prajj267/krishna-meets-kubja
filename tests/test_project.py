import json
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from src.script_manager import load_story,validate_manifest
from src.audio_processor import metrics,load_mono,process_audio
from src.synchronization import validate_subtitles,estimated_scene_error
from src.source_verification import check_manifest

ROOT=Path(__file__).resolve().parents[1]

def test_story_and_source_map():
    s=load_story(ROOT/"data/story_script.json")
    m=validate_manifest(s,ROOT/"data/source_manifest.json")
    assert len(s["panels"])==12 and len(m["entries"])==12
    assert all(p["verses"] for p in s["panels"])
    assert check_manifest(ROOT/"data/source_manifest.json")["chapter"]==42

def test_audio_metrics_and_real_resampling(tmp_path):
    rate=22050; x=np.sin(np.arange(rate)/10).astype(np.float32)*.25
    f=tmp_path/"fixture.wav"; wavfile.write(f,rate,x)
    out_rate,y,dtype=load_mono(f,44100)
    assert out_rate==44100 and len(y)==2*len(x)
    assert 0<metrics(y,out_rate)["peak_amplitude"]<1

def test_filter_outputs_plots_and_real_metrics(tmp_path):
    rate=44100; t=np.arange(rate*2)/rate
    signal=(.2*np.sin(2*np.pi*220*t)+.1*np.sin(2*np.pi*20*t)).astype(np.float32)
    source=tmp_path/"audio"/"original"/"narration.wav"; source.parent.mkdir(parents=True)
    wavfile.write(source,rate,signal)
    cfg={"sample_rate":44100,"noise_filter_cutoff_hz":80}
    result,_=process_audio(source,tmp_path,cfg)
    assert result["snr_db"] is None
    assert (tmp_path/"audio/processed/processed.wav").exists()
    assert (tmp_path/"analysis/plots/waveform_original.png").exists()
    assert (tmp_path/"analysis/plots/spectrogram_processed.png").exists()

def test_story_has_respectful_reflection():
    data=json.loads((ROOT/"data/story_script.json").read_text(encoding="utf-8"))
    assert "dignity" in data["reflection"]

def test_subtitle_timing_validation():
    assert validate_subtitles([{"start":0,"end":1},{"start":1.1,"end":2}],3)
    assert estimated_scene_error([0,2],[0,2.01])==10
