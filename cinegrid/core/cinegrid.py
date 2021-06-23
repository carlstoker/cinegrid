import datetime
import os
import progressbar
import shutil
import subprocess
from tempfile import TemporaryDirectory
import core.utils as utils

class Cinegrid:
    def __init__(self, video, settings):  
        self.video = video
        self.settings = settings


    def generate(self):
        self.update_settings()

        with TemporaryDirectory() as self.settings['temp']:
            self.extract_frames()
            self.make_montage()
            self.resize_montage()
            self.move_montage()
            utils.print_with_timestamp('Cinegrid completed. Filename: {}'.format(self.get_montage_filename()))

    def update_settings(self):
        self.settings.update({
            'filename': self.get_filename(),
            'basename': self.get_basename(),
            'extension': self.get_extension()
        })

        if self.settings['overwrite'] is False and os.path.isfile(self.get_montage_filename()):
            raise FileExistsError('Cinegrid exists. Skipping {}'.format(self.get_filename()))

        if self.settings['start_percent'] is not None and self.settings['start'] is None:
            self.settings['start'] = self.video.get_metadata()['duration'] * (self.settings['start_percent'] / 100.0)
        if self.settings['end_percent'] is not None and self.settings['end'] is None:
            self.settings['end'] = self.video.get_metadata()['duration'] * (self.settings['end_percent'] / 100.0)

        self.settings['duration'] = self.settings['end'] - self.settings['start']

        # Set interval based on duration / number of caps
        # Otherwise set number of caps based on duration/interval
        if 'caps' in self.settings:
            if self.settings['caps'] == 'maximum':
                self.settings['caps'] = int(
                    self.settings['max_width'] / (
                            self.video.get_metadata()['height'] * 200 / self.video.get_metadata()['width'])
                ) * self.settings['columns']
            self.settings['interval'] = self.settings['duration'] / self.settings['caps']
        else:
            self.settings['caps'] = int(self.settings['duration'] / self.settings['interval'])

        self.settings['rows'] = int(self.settings['caps'] / self.settings['columns'])

        self.settings.update({
            'max_frame_width': int(self.settings['max_width'] / self.settings['columns'])
        })

    def extract_frames(self):
        self.print_status()
        for i in range(1, self.settings['caps'] + 1):
            # Sets capture time. Increases i by 1 so the first frame isn't always black
            capture_time = self.settings['start'] + (i * self.settings['interval'])

            capture_time_formatted = utils.formatted_duration(capture_time)

            t = datetime.datetime(1, 1, 1) + datetime.timedelta(seconds=capture_time)
            capture_time_formatted = '{:02}:{:02}:{:02}'.format(t.hour, t.minute, t.second).replace(':', '\\\\:')

            filters = ['showinfo']
            if self.settings['timestamp']:
                filters.append(
                    'drawtext=font={}:text={}:fontsize={}:borderw=5:'
                    'bordercolor=black:fontcolor=white:x=w-tw-10:y=h-th-10 '.format(
                        self.settings['t_font'], capture_time_formatted, self.settings['t_fontsize'])
                    )

            if self.video.get_metadata()['width'] > self.settings['max_frame_width']:
                filters.append('scale={max_frame_width}:-1'.format(**self.settings))

            filters = ','.join(filters)

            command = [
                'ffmpeg',
                '-ss', str(capture_time),
                '-i', self.settings['filename'],
                '-y',
                '-vframes', '1',
                '-vf', filters,
                '-loglevel', 'fatal',
                '{}/img{:05d}.jpg'.format(self.settings['temp'], i)
            ]
            subprocess.call(command)

    def make_montage(self):
        utils.print_with_timestamp('Generating montage')

        command = [
            'montage',
            '-background', '{bgcolor}'.format(**self.settings),
            '-border', '{border}'.format(**self.settings),
            '-bordercolor', '{b_color}'.format(**self.settings),
            '-geometry', '+{spacing}+{spacing}'.format(**self.settings),
            '-tile', '{columns}x'.format(**self.settings),
            '*.jpg',
            'montage.png'
        ]

        if self.settings['shadow']:
            command.insert(5, '-shadow')

        if 'command_prefix' in self.settings:
            command.insert(0, self.settings['command_prefix'])

        
        subprocess.call(command, cwd=self.settings['temp'])

        if self.settings['header']:
            self.add_header()

    def add_header(self):
        utils.print_with_timestamp('Adding header to montage.')

        duration_formatted = utils.formatted_duration(self.video.get_metadata()['duration'])

        label = [
            'File Name: {basename}{extension}'.format(**self.settings),
            'File Size: {filesize_human} ({filesize:,d} bytes)'.format(**self.video.get_metadata()),
            'Resolution: {width}x{height} ({aspect_ratio})'.format(**self.video.get_metadata()),
            'Duration: {}'.format(duration_formatted)
        ]

        command = [
            'convert',
            'montage.png',
            '-gravity', 'NorthWest',
            '-splice', '0x{}'.format(self.settings['h_fontsize'] * 5),
            '-pointsize', '{h_fontsize}'.format(**self.settings),
            '-annotate', '+5+2', '\n'.join(label),
            '-append',
            '-layers', 'merge',
            'montage.png'
        ]

        if 'command_prefix' in self.settings:
            command.insert(0, self.settings['command_prefix'])
        subprocess.call(command, cwd=self.settings['temp'])

    def resize_montage(self):
        utils.print_with_timestamp('Resizing montage to within {max_width}x{max_height}.'.format(**self.settings))
        command = [
            'mogrify',
            '-resize', '{max_width}x{max_height}>'.format(**self.settings),
            'montage.png'
        ]

        if 'command_prefix' in self.settings:
            command.insert(0, self.settings['command_prefix'])
        subprocess.call(command, cwd=self.settings['temp'])

        utils.print_with_timestamp('Compressing montage to {max_filesize}kb.'.format(**self.settings))
        command = [
            'convert',
            'montage.png',
            '-define', 'jpeg:extent={max_filesize}kb'.format(**self.settings),
            'montage.jpg'
        ]

        if 'command_prefix' in self.settings:
            command.insert(0, self.settings['command_prefix'])
        subprocess.call(command, cwd=self.settings['temp'])

    def move_montage(self):
        utils.print_with_timestamp('Moving image from {temp} to {output}.'.format(**self.settings))
        shutil.move('{}/montage.png'.format(self.settings['temp']), self.get_montage_filename())

    def get_filename(self):
        return self.video.get_metadata()['filename']

    def get_basename(self):
        return self.video.get_metadata()['basename']

    def get_extension(self):
        return self.video.get_metadata()['extension']

    def get_montage_filename(self):
        return '{output}/{basename}-{template}.jpg'.format(**self.settings)

    def print_status(self):
        template = 'Generating {caps} frame captures for {filename} from {start} for {duration:.2f} seconds'
        utils.print_with_timestamp(template.format(**self.settings))
