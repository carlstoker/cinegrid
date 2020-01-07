#!/usr/bin/env python3
import argparse
import datetime
import json
import os
import progressbar
import shutil
import subprocess
from tempfile import TemporaryDirectory

# Configuration templates
template = {
    '3x3': {'caps': 9, 'columns': 3},
    'big': {'caps': 100, 'columns': 10},
    'custom': {},
    'huge': {'columns': 25, 'caps': 'maximum'},
    'mpc': {
        'header': True,
        'timestamp': True,
        'caps': 9,
        'columns': 3,
        'shadow': True,
        'border': 2,
        'spacing': 4
    }
}


def add_header(video, settings):
    print_with_timestamp('Adding header to montage.')

    t = datetime.datetime(1, 1, 1) + datetime.timedelta(seconds=(video.get_metadata()['duration']))
    duration_formatted = '{:02}:{:02}:{:02}'.format(t.hour, t.minute, t.second)

    label = [
        'File Name: {basename}{extension}'.format(**settings),
        'File Size: {filesize_human} ({filesize:,d} bytes)'.format(**video.get_metadata()),
        'Resolution: {width}x{height} ({aspect_ratio})'.format(**video.get_metadata()),
        'Duration: {}'.format(duration_formatted)
    ]

    command = [
        'convert',
        'montage.png',
        '-gravity', 'NorthWest',
        '-splice', '0x{}'.format(settings['h_fontsize'] * 5),
        '-pointsize', '{h_fontsize}'.format(**settings),
        '-annotate', '+5+2', '\n'.join(label),
        '-append',
        '-layers', 'merge',
        'montage.png'
    ]

    if settings['command_prefix']:
        command.insert(0, settings['command_prefix'])
    subprocess.call(command, cwd=settings['temp'])

    return None


def aspect_ratio(height, width):
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
    ratio_name = ratios[min(ratios, key=lambda x:abs(x-ratio))]
    return ratio_name


def generate_cinegrid(video, settings):
    settings.update({
        'filename': video.get_metadata()['filename'],
        'basename': os.path.splitext(os.path.basename(video.get_metadata()['filename']))[0],
        'extension': os.path.splitext(os.path.basename(video.get_metadata()['filename']))[1]
    })
    settings['montage_filename'] = '{output}/{basename}-{template}.jpg'.format(**settings)

    if not settings['overwrite'] and os.path.isfile(settings['montage_filename']):
        print_with_timestamp('Cinegrid exists. Skipping {filename}'.format(**settings))
        return False

    if settings['start_percent'] is not None and settings['start'] is None:
        settings['start'] = video.get_metadata()['duration'] * (settings['start_percent'] / 100.0)
    if settings['end_percent'] is not None and settings['end'] is None:
        settings['end'] = video.get_metadata()['duration'] * (settings['end_percent'] / 100.0)

    settings['duration'] = settings['end'] - settings['start']

    # Set interval based on duration / number of caps
    # Otherwise set number of caps based on duration/interval
    if 'caps' in settings:
        if settings['caps'] == 'maximum':
            settings['caps'] = int(
                settings['max_width'] / (video.get_metadata()['height'] * 200 / video.get_metadata()['width'])
            ) * settings['columns']
        settings['interval'] = settings['duration'] / settings['caps']
    else:
        settings['caps'] = int(settings['duration'] / settings['interval'])

    settings['rows'] = int(settings['caps'] / settings['columns'])

    settings.update({
        'max_frame_width': int(settings['max_width'] / settings['columns'])
    })

    with TemporaryDirectory() as settings['temp']:
        make_framecaptures(video, settings)
        make_montage(settings)
        if settings['header']:
            add_header(video, settings)
        resize_montage(settings)
        print_with_timestamp('Cinegrid completed. Filename: {montage_filename}'.format(**settings))


def make_framecaptures(video, settings):
    print_with_timestamp(
        'Generating {caps} frame captures for {filename} from {start} for {duration:.2f} seconds'.format(**settings))
    for i in progressbar.progressbar(range(1, settings['caps']+1)):
        # Sets capture time. Increases i by 1 so the first frame isn't always black
        capture_time = settings['start'] + (i * settings['interval'])

        t = datetime.datetime(1, 1, 1) + datetime.timedelta(seconds=capture_time)
        capture_time_formatted = '{:02}:{:02}:{:02}'.format(t.hour, t.minute, t.second).replace(':', '\\\\:')

        filters = ['showinfo']
        if settings['timestamp']:
            filters.append(
                'drawtext=font={}:text={}:fontsize={}:borderw=5:bordercolor=black:fontcolor=white:x=w-tw-10:y=h-th-10'
                .format(settings['t_font'], capture_time_formatted, settings['t_fontsize']))

        if video.get_metadata()['width'] > settings['max_frame_width']:
            filters.append('scale={max_frame_width}:-1'.format(**settings))

        filters = ','.join(filters)

        command = [
            'ffmpeg',
            '-ss', str(capture_time),
            '-i', settings['filename'],
            '-y',
            '-vframes', '1',
            '-vf', filters,
            '-loglevel', 'fatal',
            '{}/img{:05d}.jpg'.format(settings['temp'], i)
        ]
        subprocess.call(command)

    return None


def make_montage(settings):
    print_with_timestamp('Generating montage')

    command = [
        'montage',
        '-background', '{bgcolor}'.format(**settings),
        '-border', '{border}'.format(**settings),
        '-bordercolor', '{b_color}'.format(**settings),
        '-geometry', '+{spacing}+{spacing}'.format(**settings),
        '-tile', '{columns}x'.format(**settings),
        '*.jpg',
        'montage.png'
    ]

    if settings['shadow']:
        command.insert(5, '-shadow')

    if settings['command_prefix']:
        command.insert(0, settings['command_prefix'])
    subprocess.call(command, cwd=settings['temp'])

    return None


def print_with_timestamp(string):
    print('[{}] {}'.format(datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'), string))

    return None


def resize_montage(settings):
    print_with_timestamp('Resizing montage to within {max_width}x{max_height}.'.format(**settings))
    command = [
        'mogrify',
        '-resize', '{max_width}x{max_height}>'.format(**settings),
        'montage.png'
    ]

    if settings['command_prefix']:
        command.insert(0, settings['command_prefix'])
    subprocess.call(command, cwd=settings['temp'])

    print_with_timestamp('Compressing montage to {max_filesize}kb.'.format(**settings))
    command = [
        'convert',
        'montage.png',
        '-define', 'jpeg:extent={max_filesize}kb'.format(**settings),
        'montage.jpg'.format(**settings)
    ]

    if settings['command_prefix']:
        command.insert(0, settings['command_prefix'])
    subprocess.call(command, cwd=settings['temp'])
    shutil.move('{}/montage.jpg'.format(settings['temp']), settings['montage_filename'])
    return None


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024:
            return '{:.1f} {}{}'.format(num, unit, suffix)
        num /= 1024.0
    return '{:.1f} {}{}'.format(num, 'Yi', suffix)


class Video:
    __metadata = {}

    def __init__(self, filename):
        self.update_metadata(filename)

    def get_metadata(self):
        return self.__metadata

    def update_metadata(self, filename):
        self.__metadata['filename'] = filename

        command = [
            'ffprobe',
            '-show_entries', 'stream=height,width,duration:format=duration',
            '-of', 'json',
            '-v', 'error',
            filename
        ]
        j = json.loads(subprocess.check_output(command))

        for key in ['height', 'width', 'duration']:
            for d in j['streams']:
                if key in d:
                    self.__metadata[key] = d[key]
                    break

        if 'duration' not in self.__metadata:
            self.__metadata['duration'] = j['format']['duration']

        self.__metadata.update({
            'duration': float(self.__metadata['duration']),
            'filesize': os.path.getsize(filename),
            'filesize_human': sizeof_fmt(os.path.getsize(filename)),
            'aspect_ratio': aspect_ratio(self.__metadata['height'], self.__metadata['width'])
        })

        return None


def main():
    # OS specific workaround
    if os.name == 'nt':
        settings = {
            't_font': 'c\\\\:/windows/fonts/arial.ttf',
            'command_prefix': 'magick'
        }
    else:
        settings = {
            't_font': '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        }

    parser = argparse.ArgumentParser(description='Generate cinegrid for the FILEs')
    parser.add_argument('FILE', nargs='+')
    parser.add_argument('--bgcolor', help='background color (default: %(default)s)',
                        default='#EAEAEA', metavar='COLOR'),
    parser.add_argument('--border', help='border thickness in pixels (default: %(default)s)',
                        default=0, metavar='PIXELS', type=int),
    parser.add_argument('--b_color', help='border color (default: %(default)s)',
                        default='black', metavar='COLOR'),
    parser.add_argument('--caps', help='number of frame captures (default: %(default)s)',
                        default=9, type=int),
    parser.add_argument('--columns', help='number of columns (default: %(default)s)',
                        default=3, type=int),
    parser.add_argument('--end', help='end point (in seconds) for frame captures (default: %(default)s)',
                        default=None, metavar='END', type=float),
    parser.add_argument('--end_percent', help='end point (percent) for frame captures (default: %(default)s)',
                        default=90, metavar='END', type=float),
    parser.add_argument('--h_fontsize', help=' (default: %(default)s)',
                        default=32, metavar='PIXELS', type=int)
    parser.add_argument('--header', help='toggles display of header (default: %(default)s)',
                        default=False, action='store_true'),
    parser.add_argument('--interval', help='interval between captures (default: %(default)s)',
                        default=30, type=int)
    parser.add_argument('--max_filesize', help='maximum filesize in kilobytes (default: %(default)skb)',
                        default=3072, metavar='KB', type=float),
    parser.add_argument('--max_height', help='maximum height in pixels (default: %(default)s)',
                        default=5000, metavar='PIXELS', type=int),
    parser.add_argument('--max_width', help='maximum width in pixels (default: %(default)s)',
                        default=5000, metavar='PIXELS', type=int),
    parser.add_argument('--output', help='output directory (default: %(default)s)',
                        default='~/Pictures', metavar='DIR')
    parser.add_argument('--overwrite', help='overwrite existing cinegrid (default: %(default)s)',
                        default=False, action='store_true')
    parser.add_argument('--prompt', help='prompt before exiting (default: %(default)s)',
                        default=False, action='store_true'),
    parser.add_argument('--shadow', help='render shadow around captures (default: %(default)s)',
                        default=False, action='store_true'),
    parser.add_argument('--spacing', help='spacing between frames (default: %(default)s)',
                        default=0, type=int),
    parser.add_argument('--start', help='start point (in seconds) for frame captures (default: %(default)s)',
                        default=None, metavar='START', type=float),
    parser.add_argument('--start_percent', help='start point (percent) for frame captures (default: %(default)s)',
                        default=0, metavar='START', type=float),
    parser.add_argument('--template', help='configuration template [{}] (default: %(default)s)'.format(
                        ', '.join(sorted(template.keys()))),
                        default='3x3')
    parser.add_argument('--t_font', help='timestamp font (default: %(default)s)',
                        default=settings['t_font'], metavar='FONT'),
    parser.add_argument('--t_fontsize', help='timestamp fontsize (default: %(default)s)',
                        default=64, metavar='PIXELS', type=int),
    parser.add_argument('--timestamp', help='toggles display of timestamps on captures (default: %(default)s)',
                        default=False, action='store_true'),
    parser.add_argument('--version', action='version', version='%(prog)s 1.0alpha')
    settings.update(parser.parse_args().__dict__)
    settings.update(template[settings['template']])
    settings['output'] = os.path.expanduser(settings['output'])

    for filename in settings['FILE']:
        v = Video(filename)
        generate_cinegrid(v, settings)
    if settings['prompt']:
        input('Press Enter to continue.')


if __name__ == "__main__":
    main()
