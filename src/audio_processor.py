from pathlib import Path
import csv,shutil
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfiltfilt,resample_poly
from math import gcd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load_mono(path,target_rate):
    rate,x=wavfile.read(path)
    original_dtype=str(x.dtype)
    if np.issubdtype(x.dtype,np.integer):
        x=x.astype(np.float64)/max(abs(np.iinfo(x.dtype).min),np.iinfo(x.dtype).max)
    else:
        x=x.astype(np.float64)
    if x.ndim==2: x=x.mean(axis=1)
    if rate!=target_rate:
        g=gcd(int(rate),int(target_rate)); x=resample_poly(x,target_rate//g,rate//g); rate=target_rate
    return rate,np.clip(x,-1,1),original_dtype

def metrics(x,rate):
    return {"duration_seconds":len(x)/rate,"sample_rate":rate,"peak_amplitude":float(np.max(np.abs(x))) if len(x) else 0.0,"rms_amplitude":float(np.sqrt(np.mean(x*x))) if len(x) else 0.0,"clipping_percent":float(np.mean(np.abs(x)>=0.999)*100) if len(x) else 0.0}

def _save_wav(path,rate,x):
    pcm=np.int16(np.clip(x,-1,1)*32767); wavfile.write(path,rate,pcm)

def _plots(x,rate,dest,stem):
    Path(dest).mkdir(parents=True,exist_ok=True); t=np.arange(len(x))/rate
    fig,ax=plt.subplots(figsize=(10,3)); ax.plot(t,x,lw=.4); ax.set(xlabel="Time (s)",ylabel="Amplitude",title=f"{stem}: waveform, {rate} Hz"); fig.tight_layout(); fig.savefig(Path(dest)/f"waveform_{stem}.png",dpi=120); plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4)); ax.specgram(x,Fs=rate,NFFT=1024,noverlap=768,cmap="magma",scale="dB"); ax.set(xlabel="Time (s)",ylabel="Frequency (Hz)",ylim=(0,10000),title=f"{stem}: STFT magnitude (1024 Hann, hop 256)"); fig.tight_layout(); fig.savefig(Path(dest)/f"spectrogram_{stem}.png",dpi=120); plt.close(fig)

def process_audio(source,root,cfg):
    rate,x,dtype=load_mono(source,int(cfg["sample_rate"])); processed=sosfiltfilt(butter(2,cfg["noise_filter_cutoff_hz"],btype="highpass",fs=rate,output="sos"),x)
    dest=Path(root)/"audio"; (dest/"processed").mkdir(parents=True,exist_ok=True); (Path(root)/"analysis"/"plots").mkdir(parents=True,exist_ok=True)
    _save_wav(dest/"processed"/"processed.wav",rate,processed)
    _plots(x,rate,Path(root)/"analysis"/"plots","original"); _plots(processed,rate,Path(root)/"analysis"/"plots","processed")
    for folder,names in [("waveforms",["waveform_original.png","waveform_processed.png"]),("spectrograms",["spectrogram_original.png","spectrogram_processed.png"])]:
        target=Path(root)/"analysis"/folder; target.mkdir(parents=True,exist_ok=True)
        for name in names: shutil.copy2(Path(root)/"analysis"/"plots"/name,target/name)
    mix=processed.copy(); dialogue_path=Path(root)/"audio"/"original"/"dialogue.wav"; dialogue_metrics=None
    if dialogue_path.exists():
        dr,dialogue,_=load_mono(dialogue_path,int(cfg["sample_rate"]))
        if abs(len(dialogue)-len(processed))>int(rate*0.1):
            raise ValueError("Separate dialogue.wav must be manually time-aligned and within 100 ms of narration duration.")
        n=max(len(dialogue),len(processed)); a=np.pad(processed,(0,n-len(processed))); b=np.pad(dialogue,(0,n-len(dialogue)))
        mix=0.7*a+0.3*b; peak=np.max(np.abs(mix))
        if peak>0.98: mix*=0.98/peak
        dialogue_metrics=metrics(dialogue,dr)
        _save_wav(dest/"processed"/"dialogue_processed.wav",rate,b)
    result={"original":metrics(x,rate),"processed":metrics(processed,rate),"dialogue":dialogue_metrics,"final_mix":metrics(mix,rate),"filter":{"type":"Butterworth high-pass","order":2,"cutoff_hz":cfg["noise_filter_cutoff_hz"],"snr_claimed":False},"input_dtype":dtype,"snr_db":None}
    import json
    out=Path(root)/"output"; out.mkdir(exist_ok=True); (out/"audio_metrics.json").write_text(json.dumps(result,indent=2))
    flat={f"{track}_{key}":value for track in ["original","processed"] for key,value in result[track].items()}
    flat.update({"filter":result["filter"]["type"],"cutoff_hz":result["filter"]["cutoff_hz"],"snr_db":""})
    with (out/"audio_metrics.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(flat)); writer.writeheader(); writer.writerow(flat)
    original=dest/"original"/"original.wav"; original.parent.mkdir(parents=True,exist_ok=True)
    if Path(source).resolve()!=original.resolve(): shutil.copy2(source,original)
    _save_wav(dest/"final_mix.wav",rate,mix)
    return result,mix
