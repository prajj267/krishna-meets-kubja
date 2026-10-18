import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas

def _font(size, bold=False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    try: return ImageFont.truetype(name, size)
    except OSError:
        try: return ImageFont.truetype("arial.ttf", size)
        except OSError: return ImageFont.load_default()

def make_panel(panel, out, cfg, root):
    w,h=cfg["video_width"],cfg["video_height"]
    image_path=Path(root)/"assets"/"panels"/f"{panel['id'].lower().replace('p','panel_')}.png"
    if image_path.exists():
        im=Image.open(image_path).convert("RGBA").resize((w,h))
        status="USER-SUPPLIED ART"
        overlay=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(overlay)

        # Top title pill
        title_str=f"{panel['id']} • {panel['title']}"
        font_title=_font(20,bold=True)
        bbox=d.textbbox((0,0),title_str,font=font_title)
        pill_w=max(260,(bbox[2]-bbox[0])+36)
        d.rounded_rectangle((30,20,30+pill_w,62),radius=10,fill=(15,18,28,210),outline=(218,165,32,230),width=2)
        d.text((45,29),title_str,font=font_title,fill=(255,220,130,255))

        # Bottom subtitle card with narration & dialogue matching the audio
        n_lines=textwrap.wrap(panel["narration"],width=84)
        d_lines=[]
        for dlg in panel.get("dialogue",[]):
            dlg_text=f'{dlg["speaker"]}: "{dlg["text"]}"'
            d_lines.extend(textwrap.wrap(dlg_text,width=84))

        box_h=36+len(n_lines)*26+(len(d_lines)*26+8 if d_lines else 0)+24
        box_y=h-box_h-16
        d.rounded_rectangle((30,box_y,w-30,h-16),radius=12,fill=(12,15,24,220),outline=(90,105,130,180),width=2)

        font_narr=_font(19)
        curr_y=box_y+14
        for line in n_lines:
            d.text((50,curr_y),line,font=font_narr,fill=(255,255,255,255))
            curr_y+=26

        if d_lines:
            curr_y+=6
            font_diag=_font(19,bold=True)
            for line in d_lines:
                d.text((50,curr_y),line,font=font_diag,fill=(255,225,90,255))
                curr_y+=26

        font_foot=_font(13)
        d.text((w-220,h-34),f"{panel['id']} • {status}",font=font_foot,fill=(170,180,200,220))
        im=Image.alpha_composite(im,overlay).convert("RGB")
    else:
        im=Image.new("RGB",(w,h),(236,218,177)); d=ImageDraw.Draw(im)
        d.rectangle((0,0,w,105),fill=(92,49,82))
        d.text((45,28),panel["title"],font=_font(44,bold=True),fill="white")
        d.rounded_rectangle((65,145,w-65,h-95),radius=28,fill=(255,246,218),outline=(122,72,47),width=4)
        d.text((100,180),"ILLUSTRATION NEEDED",font=_font(28,bold=True),fill=(135,53,47))
        y=235
        for line in textwrap.wrap(panel["narration"],width=65):
            d.text((100,y),line,font=_font(22),fill=(40,40,40)); y+=32
        for dlg in panel.get("dialogue",[]):
            d.text((100,y),f'{dlg["speaker"]}: "{dlg["text"]}"',font=_font(22,bold=True),fill=(160,80,0)); y+=32
        status="LAYOUT DRAFT — NO ILLUSTRATION"
        d.rectangle((0,h-78,w,h),fill=(28,25,38))
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
    for i,t in enumerate([f"Student Name: {cfg['student_name']}",f"Roll Number: {cfg['roll_number']}",f"Course: {cfg['course']}","Source: Śrīmad Bhāgavatam, Canto 10, Chapter 42, verses 1–12"]):
        d.text((60,300+i*40),t,font=_font(24),fill="white")
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
