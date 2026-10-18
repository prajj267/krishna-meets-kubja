def validate_subtitles(cues, duration):
    previous=0.0
    for cue in cues:
        start,end=cue["start"],cue["end"]
        if start<previous or end<=start or end>duration+0.05:
            raise ValueError(f"Invalid subtitle timing: {cue}")
        previous=end
    return True

def estimated_scene_error(expected, actual):
    if len(expected) != len(actual):
        raise ValueError("Scene boundary count differs")
    return round(
        max((abs(a - b) for a, b in zip(expected, actual)), default=0.0)
        * 1000,
        6,
    )
