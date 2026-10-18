from pathlib import Path
import shutil,subprocess,json
import cv2
import numpy as np

def _probe(path):
    cmd=["ffprobe","-v","error","-show_entries","format=duration:stream=codec_name,width,height,r_frame_rate","-of","json",str(path)]
    return json.loads(subprocess.check_output(cmd,text=True))

def motion_frame(image,j,n,scene_index,width,height):
    im=cv2.resize(image,(width,height)); center=(width//2,height//2)
    scale=1+0.055*j/max(1,n-1)
    M=cv2.getRotationMatrix2D(center,0,scale)
    frame=cv2.warpAffine(im,M,(width,height),borderMode=cv2.BORDER_REFLECT)
    shift=int((j/max(1,n-1))*width*.018)*(1 if scene_index%2 else -1)
    return cv2.warpAffine(frame,np.float32([[1,0,shift],[0,1,0]]),(width,height),borderMode=cv2.BORDER_REFLECT)

def build_video(story,panels,audio_path,root,cfg):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"): raise RuntimeError("FFmpeg/ffprobe unavailable; MP4 stage skipped.")
    if not Path(audio_path).exists(): raise FileNotFoundError(f"Narration missing: {audio_path}")
    # Allocate panel times by word count so subtitle timing follows available narration length.
    import wave
    with wave.open(str(audio_path),"rb") as w: audio_len=w.getnframes()/w.getframerate()
    if not 175<=audio_len<=295: raise ValueError(f"Narration is {audio_len:.1f}s; with a 5-second cover, target is 180–300s. Record at natural pace; audio will not be artificially stretched.")
    weights=np.array([max(1,len((p["narration"]+" "+" ".join(d["text"] for d in p["dialogue"])).split())) for p in story["panels"]],float)
    durations=weights/weights.sum()*audio_len; out=Path(root)/"output"; out.mkdir(parents=True,exist_ok=True); temp=out/"silent.mp4"
    if len(panels)!=len(story["panels"]): raise ValueError("Comic panel image count does not match story panel count.")
    width,height,fps=cfg["video_width"],cfg["video_height"],cfg["fps"]
    writer=cv2.VideoWriter(str(temp),cv2.VideoWriter_fourcc(*"mp4v"),fps,(width,height))
    if not writer.isOpened(): raise RuntimeError("OpenCV could not initialize the intermediate video writer.")
    cover=Path(root)/"output"/"cover.png"
    if cover.exists():
        card=cv2.imread(str(cover)); card=cv2.resize(card,(width,height))
        for _ in range(5*fps): writer.write(card)
    srt=[]; cues=[]; cursor=5.0; scene_errors=[]; rendered_frames=5*fps
    for idx,(p,imgpath,dur) in enumerate(zip(story["panels"],panels,durations)):
        im=cv2.imread(str(imgpath))
        n=max(1,round(dur*fps))
        actual_start=rendered_frames/fps
        scene_errors.append(abs(actual_start-cursor)*1000)
        for j in range(n):
            frame=motion_frame(im,j,n,idx,width,height)
            writer.write(frame)
        text=p["narration"]+" "+" ".join(f'{d["speaker"]}: {d["text"]}' for d in p["dialogue"])
        srt.append(f"{idx+1}\n{_ts(cursor)} --> {_ts(cursor+dur)}\n{_wrap(text)}\n")
        cues.append({"panel_id":p["id"],"start":float(cursor),"end":float(cursor+dur),"subtitle":text,"timing":"word-count estimate"})
        cursor+=dur
        rendered_frames+=n
    writer.release()
    srtfile=out/"subtitles.srt"; srtfile.write_text("\n".join(srt),encoding="utf-8")
    from .synchronization import validate_subtitles
    validate_subtitles(cues,audio_len+5)
    (out/"subtitle_timeline.json").write_text(json.dumps(cues,indent=2,ensure_ascii=False),encoding="utf-8")
    cmd=["ffmpeg","-y","-i",str(temp),"-i",str(audio_path),"-af","adelay=5000|5000","-c:v","libx264","-pix_fmt","yuv420p","-r",str(fps),"-c:a","aac","-shortest",str(out/"final_comic.mp4")]
    subprocess.run(cmd,check=True,capture_output=True)
    probe=_probe(out/"final_comic.mp4")
    metrics={"probe":probe,"duration_seconds":audio_len+5,"panel_count":len(panels),"fps":fps,"resolution":[width,height],"timing_method":"word-count proportional estimate; manual speech alignment review required","scene_boundary_render_error_ms_max":max(scene_errors,default=0.0),"scene_boundary_error_definition":"Difference between intended word-count boundary and frame-quantized rendered scene start; does not measure speech phoneme alignment."}
    from .frame_extraction import extract
    metrics["frame_extraction"]=extract(out/"final_comic.mp4",Path(root)/"analysis"/"frame_extractions",cfg["frame_extract_interval_seconds"])
    contact=Path(root)/"analysis"/"frame_extractions"/"contact_sheet.png"
    if contact.exists():
        import shutil
        shutil.copy2(contact,out/"contact_sheet.png")
    (out/"video_metrics.json").write_text(json.dumps(metrics,indent=2))
    import csv
    row={"duration_seconds":metrics["duration_seconds"],"fps":fps,"width":width,"height":height,"panel_count":len(panels),"extracted_frames":metrics["frame_extraction"]["frame_count"],"file_bytes":(out/"final_comic.mp4").stat().st_size}
    with (out/"video_metrics.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(row)); w.writeheader(); w.writerow(row)
    return out/"final_comic.mp4"

def _ts(t):
    ms=round(t*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000); return f"{h:02}:{m:02}:{s:02},{ms:03}"
def _wrap(text,n=45):
    words=text.split(); lines=[]; line=""
    for w in words:
        if len(line)+len(w)+1>n: lines.append(line); line=w
        else: line=(line+" "+w).strip()
    if line: lines.append(line)
    return "\n".join(lines)
