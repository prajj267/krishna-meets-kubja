from pathlib import Path
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def _font(styles):
    candidates=[Path("C:/Windows/Fonts/arial.ttf"),Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),Path("/Library/Fonts/Arial.ttf")]
    for candidate in candidates:
        if candidate.exists():
            pdfmetrics.registerFont(TTFont("Unicode",str(candidate)))
            for style in styles.byName.values(): style.fontName="Unicode"
            return "Unicode"
    return "Helvetica"

def generate(root,cfg,story,manifest):
    root=Path(root); out=root/"output"; out.mkdir(exist_ok=True); styles=getSampleStyleSheet(); font=_font(styles); doc=SimpleDocTemplate(str(out/"technical_report.pdf"),pagesize=letter)
    flow=[Spacer(1,70),Paragraph(cfg["project_title"],styles["Title"]),Paragraph(cfg["episode_title"],styles["Heading1"]),Paragraph(f"Student Name: {cfg['student_name']}<br/>Roll Number: {cfg['roll_number']}<br/>Course: {cfg['course']}<br/>Source: Śrīmad Bhāgavatam, Canto 10, Chapter 42, verses 1–12",styles["Normal"]),PageBreak()]
    sections=[("Abstract","This project specifies a reproducible multimodal storytelling pipeline. Media results depend on user-supplied narration and illustrations; absent media are reported as incomplete."),("Introduction","The episode is retold in twelve child-friendly panels while distinguishing the chapter's narrative from creative staging and dialogue."),("Objectives","Create comic layouts, demonstrate speech filtering and analysis, generate synchronized video, measure real outputs, and document limitations."),("Source narrative and references",f"Primary source: {manifest['source_url']} (Canto 10, Chapter 42, verses 1–12). Status: {manifest['verification_status']}."),("System architecture","JSON story and source manifest feed Pillow comic layout, SciPy audio processing, OpenCV motion, FFmpeg encoding, evaluation, and ReportLab."),("Speech methodology","Input WAV is converted to mono 44.1 kHz by polyphase resampling. A second-order high-pass filter is demonstrated. No noise-reduction/SNR benefit is presumed."),("Video and synchronization","Panels receive deterministic zoom/pan motion. SRT durations are estimated from word count over measured audio duration. This is an estimate, not forced alignment; manual verification is required."),("Quantitative evaluation","Only metrics derived from supplied audio/video are written. Missing assets result in unavailable metrics, never fabricated values."),("Source vs Adaptation","Source: Trivakrā offers ointment; Kṛṣṇa straightens her; she invites Him; He promises to visit after His purpose. Adaptation: simplified dialogue, scenic backgrounds, camera motion, transitions, reflection, and restrained child-friendly framing."),("Children's reflection",story["reflection"]),("Limitations","No recording or finished illustration assets are bundled. FFmpeg is an external prerequisite. This environment may lack Python/media dependencies. Timing estimates need human review."),("Conclusion","The code separates source claims from creative presentation and supports measured processing when actual media is supplied.")]
    sections.extend([("Problem statement","An accurate illustrated retelling requires coordinated speech analysis, video assembly, timing, and source attribution."),("Comic design and panel mapping","Twelve child-friendly panels map to chapter verses 1-12 in the source manifest. User-supplied artwork is required for finished illustrations."),("Waveform and spectrogram analysis","Waveforms show amplitude over time. Spectrograms use STFT, NFFT 1024, hop 256, Hann window, dB scale, and frequency display to 10 kHz."),("Noise reduction and filtering","A second-order high-pass filter is demonstrated. It can alter voice fundamentals; no SNR benefit is claimed without a noise-only sample."),("Video processing and frame extraction","Deterministic zoom/pan is rendered, then frames are sampled from the encoded MP4 at configured intervals."),("References","Bhaktivedanta Book Trust International, Srimad Bhagavatam 10.42: https://vedabase.io/en/library/sb/10/42/ ."),("Appendix: project structure and execution","See README.md for the project structure, setup, commands, required WAV and panel assets, and troubleshooting.")])
    for title,body in sections: flow += [Paragraph(title,styles["Heading1"]),Paragraph(body,styles["BodyText"]),Spacer(1,10)]
    flow += [Paragraph("Measured results",styles["Heading1"])]
    for name in ["audio_metrics.json","video_metrics.json","evaluation.json"]:
        f=out/name
        if f.exists():
            data=json.loads(f.read_text(encoding="utf-8"))
            flow += [Paragraph(name,styles["Heading2"]),Paragraph(f"<font name='Courier'>{str(data)[:1800]}</font>",styles["BodyText"])]
    plotdir=root/"analysis"/"plots"
    for f in [plotdir/"waveform_original.png",plotdir/"waveform_processed.png",plotdir/"spectrogram_original.png",plotdir/"spectrogram_processed.png"]:
        if f.exists(): flow += [Image(str(f),width=430,height=150),Paragraph(f.name,styles["Normal"])]
    cover=root/"output"/"cover.png"
    if cover.exists(): flow += [Image(str(cover),width=430,height=242)]
    comparison=Table([["Bhagavatam says","Our visual adaptation adds"],["Verses 1-5: Trivakra meets the brothers and offers ointments.","Mathura street scenery, simplified dialogue and decorative framing."],["Verses 6-8: Krishna straightens Trivakra.","Gentle camera movement and respectful, non-sensational framing."],["Verses 9-12: She invites Krishna; He says He will visit after His purpose.","Simplified retelling, transitions and a children's reflection."]],colWidths=[225,225],repeatRows=1,style=TableStyle([("GRID",(0,0),(-1,-1),0.35,colors.grey),("VALIGN",(0,0),(-1,-1),"TOP"),("BACKGROUND",(0,0),(-1,0),colors.whitesmoke)]))
    comparison.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),font)]))
    mapping=Table([["Verse","Narrative fact","Panel","Adaptation"]]+[[str(e["verse"]),e["fact"],e["panel"],e["adaptation"]] for e in manifest["entries"]],colWidths=[35,150,50,215],repeatRows=1,style=TableStyle([("GRID",(0,0),(-1,-1),0.35,colors.grey),("VALIGN",(0,0),(-1,-1),"TOP"),("BACKGROUND",(0,0),(-1,0),colors.whitesmoke),("FONTNAME",(0,0),(-1,-1),font)]))
    flow += [Paragraph("Bhagavatam says / Our visual adaptation adds",styles["Heading1"]),comparison,Paragraph("Panel-to-source map",styles["Heading1"]),mapping,Spacer(1,20),Paragraph("Execution",styles["Heading1"]),Paragraph("Run python -m src.pipeline --config config.yaml --stage all. Provide audio/original/narration.wav and assets/panels/panel_01.png through panel_12.png for media generation.",styles["BodyText"])]
    def page_number(canvas,document):
        canvas.saveState()
        canvas.setFont(font,9)
        canvas.drawRightString(letter[0]-42,24,str(document.page))
        canvas.restoreState()
    doc.build(flow,onFirstPage=page_number,onLaterPages=page_number)
    return out/"technical_report.pdf"
