from pathlib import Path
import json
import subprocess
import sys
import yaml
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]
st.set_page_config(page_title="Chitra-Katha",layout="wide")
st.title("Śrīmad Bhāgavatam Chitra-Katha")
st.subheader("Kṛṣṇa Meets Kubjā")
tabs=st.tabs(["Overview","Story & Source","Comic","Speech","Video & Evaluation","Deliverables"])
with tabs[0]:
    cfg=yaml.safe_load((ROOT/"config.yaml").read_text(encoding="utf-8"))
    st.write(f"Student Name: {cfg['student_name']} · Roll Number: {cfg['roll_number']} · Course: {cfg['course']}")
    cover=ROOT/"output/cover.png"
    if cover.exists(): st.image(str(cover))
    else: st.info("Run the comic stage to create a cover layout.")
with tabs[1]:
    m=json.loads((ROOT/"data/source_manifest.json").read_text(encoding="utf-8"))
    st.write(m["verification_status"],m["source_url"]); st.dataframe(m["entries"],use_container_width=True)
with tabs[2]:
    for f in sorted((ROOT/"output/panels").glob("*.png")): st.image(str(f),caption=f.stem,width=640)
with tabs[3]:
    for p in [ROOT/"audio/original/narration.wav",ROOT/"audio/processed/processed.wav",ROOT/"audio/final_mix.wav"]:
        if p.exists(): st.write(p.name); st.audio(str(p))
    for p in sorted((ROOT/"analysis/plots").glob("*.png")): st.image(str(p),caption=p.name)
with tabs[4]:
    video=ROOT/"output/final_comic.mp4"
    if video.exists(): st.video(str(video))
    met=ROOT/"output/evaluation.json"
    if met.exists(): st.json(json.loads(met.read_text(encoding="utf-8")))
with tabs[5]:
    for p in sorted((ROOT/"output").glob("*")):
        if p.is_file(): st.write(f"{p.name}: {p}")
    if st.button("Run pipeline"):
        result=subprocess.run([sys.executable,"-m","src.pipeline","--config","config.yaml","--stage","all"],cwd=ROOT,capture_output=True,text=True)
        if result.returncode==0: st.success(result.stdout)
        else: st.error(result.stderr or result.stdout)
