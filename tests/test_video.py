import cv2
import numpy as np
from src.frame_extraction import extract
from src.synchronization import validate_subtitles
from src.video_generator import motion_frame,_wrap,_ts

def test_frame_extraction_reads_rendered_fixture(tmp_path):
    video=tmp_path/"fixture.avi"
    writer=cv2.VideoWriter(str(video),cv2.VideoWriter_fourcc(*"MJPG"),5,(160,90))
    assert writer.isOpened()
    for i in range(15): writer.write(np.full((90,160,3),i*10,dtype=np.uint8))
    writer.release()
    result=extract(video,tmp_path/"frames",1)
    assert result["frame_count"]>=2
    frame=cv2.imread(str(tmp_path/"frames"/"frame_0000.png"))
    assert frame.shape[:2]==(90,160)

def test_subtitle_outside_media_rejected():
    try:
        validate_subtitles([{"start":1,"end":4}],3)
        assert False,"Expected invalid cue to fail"
    except ValueError:
        pass

def test_zoom_pan_dimensions_and_timestamp():
    image=np.zeros((90,160,3),dtype=np.uint8)
    a=motion_frame(image,0,10,0,320,180)
    b=motion_frame(image,9,10,1,320,180)
    assert a.shape==(180,320,3) and b.shape==a.shape
    assert _ts(1.25)=="00:00:01,250"
    assert len(_wrap("a long child-friendly subtitle text",10).splitlines())>1
