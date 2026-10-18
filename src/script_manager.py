import json
from pathlib import Path

def load_story(path):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    assert len(data.get("panels", [])) in range(10,16), "Story must contain 10–15 panels"
    seen=set()
    for panel in data["panels"]:
        for key in ("id","title","verses","visual","characters","narration","dialogue"):
            assert key in panel, f"{panel.get('id')} missing {key}"
        assert panel["id"] not in seen, "Duplicate panel id"
        seen.add(panel["id"])
    return data

def validate_manifest(story, path):
    manifest=json.loads(Path(path).read_text(encoding="utf-8"))
    mapped={p["id"] for p in story["panels"]}
    for e in manifest["entries"]:
        ids=e["panel"].split("-")
        # Entries use a single panel or a contiguous panel interval.
        if len(ids)==2 and ids[1].startswith("P"): ids=[ids[0],ids[1]]
        assert all(x in mapped for x in ids), f"Unknown panel mapping: {e['panel']}"
        assert 1 <= int(e["verse"]) <= 12
    return manifest
