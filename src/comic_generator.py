from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas

def _font(size):
    try: return ImageFont.truetype("arial.ttf",size)
    except OSError: return ImageFont.load_default()

def make_panel(panel, out, cfg, root):
    w,h=cfg["video_width"],cfg["video_height"]
    image_path=Path(root)/"assets"/"panels"/f"{panel['id'].lower().replace('p','panel_')}.png"
    if image_path.exists():
        im=Image.open(image_path).convert("RGB").resize((w,h))
        status="USER-SUPPLIED ART"
    else:
        im=Image.new("RGB",(w,h),(236,218,177)); d=ImageDraw.Draw(im)
        d.rectangle((0,0,w,105),fill=(92,49,82))
        d.text((45,28),panel["title"],font=_font(44),fill="white")
        d.rounded_rectangle((65,145,w-65,h-95),radius=28,fill=(255,246,218),outline=(122,72,47),width=4)
        d.text((100,180),"ILLUSTRATION NEEDED",font=_font(28),fill=(135,53,47))
        y=235
        for line in [panel["visual"][i:i+62] for i in range(0,len(panel["visual"]),62)]:
            d.text((100,y),line,font=_font(25),fill=(40,40,40)); y+=40
        status="LAYOUT DRAFT — NO ILLUSTRATION"
    d=ImageDraw.Draw(im); d.rectangle((0,h-78,w,h),fill=(28,25,38))
    d.text((35,h-58),f"{panel['id']}  •  {status}",font=_font(22),fill="white")
    out=Path(out); out.parent.mkdir(parents=True,exist_ok=True); im.save(out)
    return out

def build_comic(story,cfg,root):
    out=Path(root)/"output"; panels=[]
    for i,p in enumerate(story["panels"],1):
        panels.append(make_panel(p,out/"panels"/f"panel_{i:02}.png",cfg,root))
    cover=Image.new("RGB",(cfg["video_width"],cfg["video_height"]),(31,44,73)); d=ImageDraw.Draw(cover)
    d.text((60,90),cfg["project_title"],font=_font(46),fill=(255,220,135))
    d.text((60,180),cfg["episode_title"],font=_font(42),fill="white")
    for y,t in enumerate([f"Student Name: {cfg['student_name']}",f"Roll Number: {cfg['roll_number']}",f"Course: {cfg['course']}","Source: Śrīmad Bhāgavatam, Canto 10, Chapter 42, verses 1–12"],300):
        d.text((60,y),t,font=_font(24),fill="white")
    cover.save(out/"cover.png")
    import json
    (Path(root)/"data"/"panel_metadata.json").write_text(json.dumps(story["panels"],ensure_ascii=False,indent=2),encoding="utf-8")
    thumbs=[]
    for f in panels:
        im=Image.open(f).convert("RGB"); im.thumbnail((320,180)); thumbs.append(im.copy())
    sheet=Image.new("RGB",(960,((len(thumbs)+2)//3)*210),"white")
    for i,im in enumerate(thumbs): sheet.paste(im,((i%3)*320,(i//3)*210))
    sheet.save(out/"comic_contact_sheet.png")
    pdf=canvas.Canvas(str(out/"comic.pdf"),pagesize=(cfg["video_width"],cfg["video_height"]))
    for image in [out/"cover.png",*panels]:
        pdf.drawImage(str(image),0,0,width=cfg["video_width"],height=cfg["video_height"]); pdf.showPage()
    pdf.save()
    return {"cover":out/"cover.png","comic":out/"comic.pdf","panels":panels}
