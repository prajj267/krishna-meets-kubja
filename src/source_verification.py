import json
from pathlib import Path

def check_manifest(path):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    assert data["source_url"]=="https://vedabase.io/en/library/sb/10/42/"
    assert data["canto"]==10 and data["chapter"]==42
    assert data["verification_status"] in {"verified_by_online_chapter_check","pending_manual_verification"}
    verses={int(e["verse"]) for e in data["entries"]}
    assert set(range(1,13)).issubset(verses)
    for e in data["entries"]:
        assert e["fact"] and e["panel"] and e["adaptation"]
    return data
