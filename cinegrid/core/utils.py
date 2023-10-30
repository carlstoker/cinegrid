import datetime
import json
import math
import os
import subprocess


def get_file_metadata(filename):
    command = [
        'ffprobe',
        '-show_entries', 'stream=height,width,duration:format=duration',
        '-of', 'json',
        '-v', 'error',
        filename
    ]
    return json.loads(subprocess.check_output(command))


def cleanup_metadata(filename, metadata):
    clean_metadata = {'filename': filename}

    for key in ['height', 'width', 'duration']:
        for dur in metadata['streams']:
            if key in dur:
                clean_metadata[key] = dur[key]
                break

    if 'duration' not in clean_metadata:
        clean_metadata['duration'] = metadata['format']['duration']

    clean_metadata.update({
        'duration': float(clean_metadata['duration']),
        'filesize': os.path.getsize(clean_metadata['filename']),
        'filesize_human': sizeof_fmt(os.path.getsize(clean_metadata['filename'])),
        'aspect_ratio': aspect_ratio(clean_metadata['width'], clean_metadata['height']),
        'basename': os.path.splitext(os.path.basename(filename))[0],
        'extension': os.path.splitext(os.path.basename(filename))[1]
    })

    return clean_metadata


def sizeof_fmt(num):
    suffixes = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']

    if num > 0:
        power = math.floor(math.log(num, 1024))
    else:
        power = 1

    if power > (len(suffixes) - 1):
        power = len(suffixes) - 1

    value = num / (1024 ** power)

    suffix = suffixes[power]

    return '{0:.1f} {1}'.format(value, suffix)


def aspect_ratio(width, height):
    ratios = {
        1.00: '1:1',
        1.25: '5:4',
        1.33: '4:3',
        1.43: '1.43:1 IMAX',
        1.60: '16:10',
        1.78: '16:9',
        1.85: '1.85:1',
        1.90: '1.90:1 IMAX',
        2.20: '2.20:1',
        2.35: '2.35:1'
    }
    ratio = float(width) / height

    ratio_name = ratios[min(ratios, key=lambda x: abs(x - ratio))]
    return ratio_name


def formatted_duration(duration):
    time_obj = datetime.datetime(1, 1, 1) + datetime.timedelta(seconds=duration)
    return '{:02}:{:02}:{:02}'.format(time_obj.hour, time_obj.minute, time_obj.second).replace(':', '\\:')


def print_with_timestamp(string, base_time=datetime.datetime.now()):
    print('[{}] {}'.format(datetime.datetime.strftime(base_time, '%H:%M:%S'), string))
