import core.utils
import datetime
import os


def test_sizeof_fmt():
    assert core.utils.sizeof_fmt(1) == "1.0 B"
    assert core.utils.sizeof_fmt(1024**1) == "1.0 KiB"
    assert core.utils.sizeof_fmt(1024**2) == "1.0 MiB"
    assert core.utils.sizeof_fmt(1024**3) == "1.0 GiB"
    assert core.utils.sizeof_fmt(1024**4) == "1.0 TiB"
    assert core.utils.sizeof_fmt(1024**5) == "1.0 PiB"
    assert core.utils.sizeof_fmt(1024**6) == "1.0 EiB"
    assert core.utils.sizeof_fmt(1024**7) == "1.0 ZiB"
    assert core.utils.sizeof_fmt(1024**8) == "1.0 YiB"
    assert core.utils.sizeof_fmt(1024**9) == "1024.0 YiB"


def test_aspect_ratio():
    assert core.utils.aspect_ratio(1920, 1080) == "16:9"
    assert core.utils.aspect_ratio(1, 1) == "1:1"
    assert core.utils.aspect_ratio(5, 4) == '5:4'
    assert core.utils.aspect_ratio(4, 3) == '4:3'
    assert core.utils.aspect_ratio(1.43, 1) == '1.43:1 IMAX'
    assert core.utils.aspect_ratio(16, 10) == '16:10'
    assert core.utils.aspect_ratio(16, 9) == '16:9'
    assert core.utils.aspect_ratio(1.85, 1) == '1.85:1'
    assert core.utils.aspect_ratio(1.90, 1) == '1.90:1 IMAX'
    assert core.utils.aspect_ratio(2.20, 1) == '2.20:1'
    assert core.utils.aspect_ratio(2.35, 1) == '2.35:1'


def test_get_file_metadata():
    filename = os.getcwd() + '\\tests\\sintel_trailer-480p.mp4'
    metadata = core.utils.get_file_metadata(filename)
    assert metadata['streams'][0]['duration'] == '52.208333'
    assert metadata['streams'][0]['height'] == 480
    assert metadata['streams'][0]['width'] == 854


def test_cleanup_metadata():
    filename = os.getcwd() + '\\tests\\sintel_trailer-480p.mp4'
    metadata = {
        'programs': [], 
        'streams': [
                {
                    'width': 854,
                    'height': 480,
                    'duration':
                    '52.208333'
                }, {
                    'duration': '51.946667'
                }
            ],
        'format': {
            'duration': '52.209000'
        }
    }
    clean_metadata = core.utils.cleanup_metadata(filename, metadata)

    assert clean_metadata['filename'] == filename
    assert clean_metadata['basename'] == 'sintel_trailer-480p'
    assert clean_metadata['extension'] == '.mp4'

    assert clean_metadata['height'] == 480
    assert clean_metadata['width'] == 854
    assert clean_metadata['aspect_ratio'] == '16:9'

    assert clean_metadata['duration'] == 52.208333

    assert clean_metadata['filesize'] == 4372373
    assert clean_metadata['filesize_human'] == '4.2 MiB'


def test_formatted_duration():
    assert core.utils.formatted_duration(duration = 0) == '00\\:00\\:00'
    assert core.utils.formatted_duration(duration = 60) == '00\\:01\\:00'
    assert core.utils.formatted_duration(duration = 3600) == '01\\:00\\:00'
    assert core.utils.formatted_duration(duration = 7200) == '02\\:00\\:00'


def test_print_with_timestamp(capsys):
    core.utils.print_with_timestamp('foo', datetime.datetime(1, 1, 1, 0, 0, 0))
    captured = capsys.readouterr()
    assert captured.out == '[00:00:00] foo\n'

    core.utils.print_with_timestamp('foo', datetime.datetime(1, 1, 1, 0, 0, 1))
    captured = capsys.readouterr()
    assert captured.out == '[00:00:01] foo\n'

    core.utils.print_with_timestamp('foo', datetime.datetime(1, 1, 1, 0, 1, 0))
    captured = capsys.readouterr()
    assert captured.out == '[00:01:00] foo\n'

    core.utils.print_with_timestamp('foo', datetime.datetime(1, 1, 1, 1, 0, 0))
    captured = capsys.readouterr()
    assert captured.out == '[01:00:00] foo\n'
