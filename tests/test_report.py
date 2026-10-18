from pathlib import Path
import json
from src.report_generator import generate

ROOT=Path(__file__).resolve().parents[1]

def test_report_is_created(tmp_path):
    story=json.loads((ROOT/"data/story_script.json").read_text(encoding="utf-8"))
    manifest=json.loads((ROOT/"data/source_manifest.json").read_text(encoding="utf-8"))
    cfg={"project_title":"Project","episode_title":"Episode","student_name":"[STUDENT_NAME]","roll_number":"[ROLL_NUMBER]","course":"Speech and Video Processing"}
    result=generate(tmp_path,cfg,story,manifest)
    assert result.exists() and result.stat().st_size>1000
