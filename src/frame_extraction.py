from pathlib import Path
import cv2
from PIL import Image,ImageDraw

def extract(video,out,interval=10):
    cap=cv2.VideoCapture(str(video))
    if not cap.isOpened(): raise RuntimeError(f"Cannot open video {video}")
    fps=cap.get(cv2.CAP_PROP_FPS); frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration=frames/fps if fps else 0
    dest=Path(out); dest.mkdir(parents=True,exist_ok=True); paths=[]
    for sec in range(0,int(duration)+1,interval):
        cap.set(cv2.CAP_PROP_POS_MSEC,sec*1000); ok,frame=cap.read()
        if ok:
            p=dest/f"frame_{sec:04}.png"; cv2.imwrite(str(p),frame); paths.append((p,sec))
    cap.release()
    if paths:
        thumb=[]
        for p,sec in paths:
            im=Image.open(p).convert("RGB"); im.thumbnail((320,180)); thumb.append((im.copy(),sec))
        sheet=Image.new("RGB",(640,((len(thumb)+1)//2)*210),"white"); d=ImageDraw.Draw(sheet)
        for i,(im,sec) in enumerate(thumb):
            x=(i%2)*320; y=(i//2)*210; sheet.paste(im,(x,y)); d.text((x+5,y+182),f"{sec}s",fill="black")
        sheet.save(dest/"contact_sheet.png")
    return {"frame_count":len(paths),"duration_seconds":duration,"contact_sheet":str(dest/"contact_sheet.png") if paths else None}
