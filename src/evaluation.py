import json,subprocess,shutil
from pathlib import Path
from .audio_processor import load_mono,metrics

def evaluate(root,cfg):
    root=Path(root); result={"audio":None,"video":None,"qualitative_checklist":{k:"manual review required" for k in ["story accuracy","visual consistency","speech intelligibility","subtitle readability","synchronization","cultural appropriateness","child accessibility"]}}
    wav=root/"audio"/"original"/"narration.wav"
    if wav.exists():
        rate,x,_=load_mono(wav,cfg["sample_rate"]); result["audio"]=metrics(x,rate)
    mp4=root/"output"/"final_comic.mp4"
    if mp4.exists() and shutil.which("ffprobe"):
        raw=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_name,width,height,r_frame_rate","-of","json",str(mp4)],text=True)
        result["video"]=json.loads(raw)
    (root/"output").mkdir(exist_ok=True); (root/"output"/"evaluation.json").write_text(json.dumps(result,indent=2))
    return result
