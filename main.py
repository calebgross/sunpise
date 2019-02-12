#!/usr/bin/env python

from argparse  import ArgumentParser
from os        import getcwd
from sunpise   import *

parser = ArgumentParser()
parser.add_argument('-c', '--capture-interval',
                    type=int, default=60,
                    help='duration of recording, in seconds (use with -n)')
parser.add_argument('-D', '--debug',
                    action='store_true', default=False,
                    help='debug mode')
parser.add_argument('-d', '--directory',
                    default=getcwd() + '/',
                    help='directory where sunpise files are stored')
parser.add_argument('-e', '--event-type',
                    default='sunrise', choices=['sunrise', 'sunset'],
                    help='sunrise or sunset')
parser.add_argument('-f', '--client-secret',
                    default='client_secret.json',
                    help='client secret file')
parser.add_argument('-l', '--location',
                    default=city,
                    help='camera\'s geographic location')
parser.add_argument('-n', '--start-now',
                    action='store_true', default=False,
                    help='start recording now')
parser.add_argument('-s', '--still-interval',
                    type=int, default=1000,
                    help='time between frames, in milliseconds')
parser.add_argument('-r', '--rotation',
                    type=int, default=0,
                    help='degrees to rotate')
parser.add_argument('-p', '--private',
                    action='store_true', default=False,
                    help='make video private')
args = vars(parser.parse_args())

def main():
    print_header(args)
    event_times = get_event_times(args)
    print_times(args, event_times)
    wait_start(args, event_times['start'])
    print('\n==> Step 1 of 4 (' + datetime.now().strftime('%H:%M') + '): Capturing stills...')
    capture(args, event_times)
    print('\n==> Step 2 of 4 (' + datetime.now().strftime('%H:%M') + '): Stitching frames together...')
    video_name = stitch(args)
    print('\n==> Step 2 of 4 (' + datetime.now().strftime('%H:%M') + '): Stitching frames together...')
    upload(args, video_name)
    print('\n==> Step 4 of 4 (' + datetime.now().strftime('%H:%M') + '): Removing files...')
    cleanup(args)
    print('\n==> Finished at', datetime.now().strftime('%H:%M')+'.\n')

if __name__ == '__main__':
    main()
