#!/usr/bin/env python3
import argparse
import os
import core.video as video
import core.cinegrid as cinegrid
import core.utils as utils

templates = {
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

def main():
    # OS specific workaround
    if os.name == 'nt':
        settings = {
            't_font': 'c\\\\:/windows/fonts/arial.ttf'
        }
    else:
        settings = {
            't_font': '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        }


    parser = create_parser(settings)
    settings.update(parser.parse_args().__dict__)
    settings.update(templates[settings['template']])
    settings['output'] = os.path.expanduser(settings['output'])

    for filename in settings['FILE']:
        if os.path.exists(filename) is False:
            print('File does not exist: {}'.format(filename))
            continue
        vid = video.Video(filename)
        grid = cinegrid.Cinegrid(vid, settings)
        try:
            grid.generate()
        except FileExistsError as err:
            utils.print_with_timestamp(err)

    if settings['prompt']:
        input('Press Enter to continue.')

def create_parser(settings):
    parser = argparse.ArgumentParser(description='Generate cinegrid for the FILEs')
    parser.add_argument('FILE', nargs='+')
    parser.add_argument('--bgcolor', help='background color (default: %(default)s)',
                        default='#EAEAEA', metavar='COLOR')
    parser.add_argument('--border', help='border thickness in pixels (default: %(default)s)',
                        default=0, metavar='PIXELS', type=int)
    parser.add_argument('--b_color', help='border color (default: %(default)s)',
                        default='black', metavar='COLOR')
    parser.add_argument('--caps', help='number of frame captures (default: %(default)s)',
                        default=9, type=int)
    parser.add_argument('--columns', help='number of columns (default: %(default)s)',
                        default=3, type=int)
    parser.add_argument('--end', help='end point (in seconds) for frame captures (default: %(default)s)',
                        default=None, metavar='END', type=float)
    parser.add_argument('--end_percent', help='end point (percent) for frame captures (default: %(default)s)',
                        default=90, metavar='END', type=float)
    parser.add_argument('--h_fontsize', help=' (default: %(default)s)',
                        default=32, metavar='PIXELS', type=int)
    parser.add_argument('--header', help='toggles display of header (default: %(default)s)',
                        default=False, action='store_true')
    parser.add_argument('--interval', help='interval between captures (default: %(default)s)',
                        default=30, type=int)
    parser.add_argument('--max_filesize', help='maximum filesize in kilobytes (default: %(default)skb)',
                        default=3072, metavar='KB', type=float)
    parser.add_argument('--max_height', help='maximum height in pixels (default: %(default)s)',
                        default=5000, metavar='PIXELS', type=int)
    parser.add_argument('--max_width', help='maximum width in pixels (default: %(default)s)',
                        default=5000, metavar='PIXELS', type=int)
    parser.add_argument('--output', help='output directory (default: %(default)s)',
                        default='~/Pictures', metavar='DIR')
    parser.add_argument('--overwrite', help='overwrite existing cinegrid (default: %(default)s)',
                        default=False, action='store_true')
    parser.add_argument('--prompt', help='prompt before exiting (default: %(default)s)',
                        default=False, action='store_true')
    parser.add_argument('--shadow', help='render shadow around captures (default: %(default)s)',
                        default=False, action='store_true')
    parser.add_argument('--spacing', help='spacing between frames (default: %(default)s)',
                        default=0, type=int)
    parser.add_argument('--start', help='start point (in seconds) for frame captures (default: %(default)s)',
                        default=None, metavar='START', type=float)
    parser.add_argument('--start_percent', help='start point (percent) for frame captures (default: %(default)s)',
                        default=0, metavar='START', type=float)
    parser.add_argument('--template', help='configuration template [{}] (default: %(default)s)'.format(
        ', '.join(sorted(templates.keys()))),
                        default='3x3')
    parser.add_argument('--t_font', help='timestamp font (default: %(default)s)',
                        default=settings['t_font'], metavar='FONT')
    parser.add_argument('--t_fontsize', help='timestamp fontsize (default: %(default)s)',
                        default=64, metavar='PIXELS', type=int)
    parser.add_argument('--timestamp', help='toggles display of timestamps on captures (default: %(default)s)',
                        default=False, action='store_true')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0alpha')

    return parser


if __name__ == "__main__":
    main()
