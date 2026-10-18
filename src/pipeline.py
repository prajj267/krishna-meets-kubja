import argparse,json,shutil,sys
from pathlib import Path
import yaml
from .script_manager import load_story,validate_manifest
from .source_verification import check_manifest
from .comic_generator import build_comic
from .audio_processor import process_audio
from .evaluation import evaluate
from .report_generator import generate

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--config",default="config.yaml"); ap.add_argument("--stage",choices=["all","comic","audio","video","evaluation","report"],default="all"); args=ap.parse_args()
    cfg=yaml.safe_load(Path(args.config).read_text(encoding="utf-8")); root=Path(args.config).resolve().parent
    story=load_story(root/"data/story_script.json"); manifest=validate_manifest(story,root/"data/source_manifest.json")
    check_manifest(root/"data/source_manifest.json")
    done=[]; issues=[]; panels=[]
    stages=["comic","audio","video","evaluation","report"] if args.stage=="all" else [args.stage]
    for stage in stages:
        try:
            if stage=="comic":
                r=build_comic(story,cfg,root); panels=r["panels"]; done += [str(r["cover"]),str(r["comic"])]
            elif stage=="audio":
                src=root/"audio/original/narration.wav"
                if not src.exists(): raise FileNotFoundError(f"Supply narration WAV at {src}")
                result,_=process_audio(src,root,cfg); done.append(str(root/"output/audio_metrics.json"))
            elif stage=="video":
                from .video_generator import build_video
                if not panels: panels=sorted((root/"output/panels").glob("panel_*.png"))
                result=build_video(story,panels,root/"audio/original/narration.wav",root,cfg); done.append(str(result))
            elif stage=="evaluation": evaluate(root,cfg); done.append(str(root/"output/evaluation.json"))
            elif stage=="report": result=generate(root,cfg,story,manifest); done.append(str(result))
        except Exception as e: issues.append(f"{stage}: {e}")
    print(json.dumps({"generated":done,"incomplete_or_failed":issues},indent=2,ensure_ascii=False))
    if args.stage!="all" and issues: sys.exit(1)
if __name__=="__main__": main()
