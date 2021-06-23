import core.video
import os

def test_get_metadata():
    filename = os.getcwd() + '\\tests\\sintel_trailer-480p.mp4'

    video = core.video.Video(filename)

    assert video.get_metadata()['filename'] == filename
    assert video.get_metadata()['basename'] == 'sintel_trailer-480p'
    assert video.get_metadata()['extension'] == '.mp4'

    assert video.get_metadata()['height'] == 480
    assert video.get_metadata()['width'] == 854
    assert video.get_metadata()['aspect_ratio'] == '16:9'

    assert video.get_metadata()['duration'] == 52.208333

    assert video.get_metadata()['filesize'] == 4372373
    assert video.get_metadata()['filesize_human'] == '4.2 MiB'
