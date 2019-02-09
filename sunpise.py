#!/usr/bin/python
# -*- coding: utf-8 -*-

from upload_video import *

# Sunpise core.
import requests
import re
import textwrap
import os
import argparse
import json
from   subprocess  import Popen, PIPE, STDOUT
from   datetime    import datetime, timedelta
from   dateutil.tz import tzlocal
from   pytz        import UTC
from   time        import sleep

# Upload video.
# import http.client
# import httplib2
# import random
# import sys
# import time
# from   apiclient.discovery import build
# from   apiclient.errors    import HttpError
# from   apiclient.http      import MediaFileUpload
# from   oauth2client.client import flow_from_clientsecrets
# from   oauth2client.file   import Storage
# from   oauth2client.tools  import argparser, run_flow


# Initialize variables.
# httplib2.RETRIES = 1
ip_info          = json.loads(requests.get('http://ipinfo.io').text)
city             = ip_info['city']
coordinates      = ip_info['loc'].split(',')

# Set up argument parser.
parser = argparse.ArgumentParser()
parser.add_argument('-c','--capture-interval', type=int, default=60,
    help='duration of recording, in seconds (use with -n)')
parser.add_argument('-D','--debug', action='store_true', default=False,
    help='debug mode')
parser.add_argument('-d','--directory', default=os.getcwd()+'/',
    help='directory where sunpise files are stored')
parser.add_argument('-e','--event-type', default='sunrise',
    help='sunrise or sunset', choices=['sunrise', 'sunset'])
parser.add_argument('-f','--client-secret', default='client_secret.json',
    help='client secret file')
parser.add_argument('-l','--location', default=city,
    help='camera\'s geographic location')
parser.add_argument('-n','--start-now', action='store_true', default=False,
    help='start recording now')
parser.add_argument('-s','--still-interval', type=int, default=1000,
    help='individual frame exposure length, in milliseconds')
parser.add_argument('-u','--upside-down', action='store_true', default=False,
    help='lens positioned upside-down')
args = vars(parser.parse_args())


def main():
    print_header()                    # Log heading.
    event_times = get_event_times()
    print_times(event_times)          # Get event times.
    wait_start(event_times['start'])  # Wait until event to start timelapse.
    capture(event_times)              # Start capturing stills.
    video_name = stitch()             # Make video.
    upload(video_name)                # Upload video.
    cleanup()                         # Remove files from device.


# Wrapper to create easily-readable log entries.
def run_command(command, log=True):
    prefix = 'Executing command: '
    wrapper = textwrap.TextWrapper(
        initial_indent=prefix,
        width=80,
        subsequent_indent=' ' * int((len(prefix) / 4))
        )
    if log:
        print(wrapper.fill(command))
    if not args['debug']:
        os.system(command)


# Log event type, date, and debug status.
def print_header():
    
    # Prepare header.
    title_char = '~'
    title = (args['location'].title() + ' ' +
             args['event_type'].capitalize()  + ' ' +
             '-'*(len(args['event_type'])%2+2) + ' ' + 
             datetime.now().strftime('%d %b %Y'))
    title_margin = int(40 - float(len(title) + 2) / 2)
    
    # Print header.
    print(title_char * (2 * title_margin + 2 + len(title)))
    print(title_char * title_margin, title, title_char * title_margin)
    if args['debug']:
        print(title_char * (2 * title_margin + 2 + len(title)))
        print(title_char * 36, 'DEBUG', title_char * 36)
    print(title_char * (2 * title_margin + 2 + len(title)), end='\n\n')    


# Pretty print event times.
def print_times(event_times):
    for key in reversed(sorted(event_times.keys())):
        print(args['event_type'].capitalize(), key + ':' + ' ' * 
            (9 - len(key)) + event_times[key].strftime('%H:%M'))


# Get times for dawn and sunshine from the web.
def get_event_times():

    if args['start_now']:
        return {'start': datetime.now().replace(tzinfo=tzlocal()),
                'end'  : datetime.now().replace(tzinfo=tzlocal()) +
                         timedelta(0, int(args['capture_interval']))}

    # Query API for sunrise/sunset info, and load into JSON for easy parsing.
    payload  = {'lat': coordinates[0], 'lng': coordinates[1], 'date': 'today'}
    url      = 'http://api.sunrise-sunset.org/json'
    response = json.loads(requests.get(url, params=payload).text)['results']
    
    # Initialize data structures to iterate through JSON response.
    today       = datetime.now()
    event_names = {'sunrise': {'start': 'civil_twilight_begin',
                               'end'  : 'sunrise'},
                   'sunset' : {'start': 'sunset',
                               'end'  : 'civil_twilight_end'}}

    # for events "start" and "end":
    #    1) create datetime object from API response string
    #    2) make the datetime timezone-aware (API returns in UTC)
    #    3) convert to local timezone
    #    4) complete the datetime with local year, month, and day
    #   5a) if sunrise, move the end time forward by one hour
    #   5b) if sunset, move the start time back by one hour
    mode        = ('sunrise', 'sunset').index(args['event_type'])
    event_times = {event_name: datetime.strptime(
        response[event_names[args['event_type']][event_name]],
        '%I:%M:%S %p').replace(
        year=today.year, tzinfo=UTC).astimezone(tzlocal()).replace(
        year=today.year, month=today.month, day=today.day) + timedelta(
        hours=(1 - 2 * mode) * (('end', 'start').index(event_name) == mode))
        for event_name in sorted(event_names[args['event_type']].keys())}

    return event_times


# Sleep until event start.
def wait_start(start):

    # Print current time.
    print('Currently', datetime.now().time().strftime('%H:%M')+',', end=' ')

    # Check if event has started.
    if datetime.now().replace(tzinfo=tzlocal()) >= start:
        print('sun has started ' +
              ('rising' if args['event_type'] == 'sunrise' else 'setting') +
              '. Starting timelapse.')
        return
    else:
        
        # Determine how long to wait until event starts.
        time_delta = start - datetime.now().replace(tzinfo=tzlocal())
        seconds_until_start = time_delta.seconds + 5
        if seconds_until_start >= 3600:
            sleep_time = str(round(seconds_until_start/3600, 2)) + ' hours'
        elif seconds_until_start >= 60:
            sleep_time = str(round(seconds_until_start/60, 2)) + ' minutes'
        else:
            sleep_time = str(seconds_until_start) + ' seconds'

        # Sleep until calculated time.
        print('sleeping', sleep_time, 'until', start.strftime('%H:%M') + '.')
        sleep(seconds_until_start)
        wait_start(start)


# Take pictures for specified interval.
def capture(event_times):
    if not args['start_now']:
        capture_interval = (event_times['end'] - event_times['start']).seconds
    else:
        capture_interval = args['capture_interval']
    stills_dir = args['directory'] + 'stills/'
    capture = ('raspistill ' +
               '--roi 0.15,0.2,0.75,0.45 ' +
               '--height 875 ' +
               '--width 1944 ' +
               '--burst ' + 
               '--output ' + stills_dir + 'still_%04d.jpg ' +
               '--timelapse ' + str(args['still_interval']) + ' ' +
               '--timeout ' + str(capture_interval*1000))
    if args['upside_down']:
        capture += ' --hflip --vflip'
    print('\n==> Step 1 of 4 (' +
        datetime.now().strftime('%H:%M') + '): Capturing stills...')
    print('Starting at ' + event_times['start'].strftime('%H:%M') + 
        ', capturing stills every ' +
        str(int(args['still_interval']/1000))+ ' seconds for ' +
        str(int(capture_interval/60)) + ' minutes.')
    run_command(capture)  
    
    # Account for unprocessed stills so avconv can process input.
    filenames = os.listdir(stills_dir)
    for i, filename in enumerate(sorted(filenames)):
        new_filename = 'still_' + str(int(i)).zfill(4) + '.jpg'
        run_command(
            'mv ' + stills_dir + filename + ' ' + stills_dir + new_filename,
            False)

    return


# Compile frames into video.
def stitch():
    video_name = 'sunpise' + datetime.now().strftime('_%m-%d-%y_%H-%M') + '.avi'
#     make_video = ('avconv ' +
#                   '-f image2 ' + 
#                   '-i ' + args['directory'] + 'stills/still_%04d.jpg ' + 
#                   '-r 24 ' + 
#                   '-qscale 1 ' +
#                   args['directory'] + video_name)
    make_video = ('ffmpeg ' +
                  '-i ' + args['directory'] + 'stills/still_%04d.jpg ' + 
                  '-r 24 ' + 
                  '-s hd1080 ' + 
                  '-vcodec libx264 ' + 
                  args['directory'] + video_name)
    print('\n==> Step 2 of 4 (' +
        datetime.now().strftime('%H:%M') + '): Stitching frames together...')
    run_command(make_video)
    return video_name


# Upload to YouTube.
def upload(video_name):

    # Prepare arguments to YouTube API.
    location_formatted = re.sub(r'-.*', '', args['location']).title()
    event_type_formatted = args['event_type'].capitalize()
    options = dict(
      category      = '22',
      description   = '',
      file          = args['directory'] + (video_name if not args['debug'] else 'vid.mp4'), 
      keywords      = '',
      logging_level = 'ERROR',
      privacyStatus = 'private',
      title         = location_formatted + ' ' + event_type_formatted + ' - ' + 
                      datetime.now().strftime('%d %b %Y')
      )

    print('\n==> Step 3 of 4 (' +
        datetime.now().strftime('%H:%M') + '): Uploading video...')

    # authenticate to YouTube
    youtube = get_authenticated_service()

    if not args['debug']:

        # initialize upload to YouTube
        try:
            initialize_upload(youtube, options)
        except HttpError as e:
            print(("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)))
    return


# Delete stills and generated video file.
def cleanup():
    cleanup = ('rm ' + args['directory'] + 'stills/*.jpg; rm ' +
        args['directory'] + '*.avi')
    print('\n==> Step 4 of 4 (' +
        datetime.now().strftime('%H:%M') + '): Removing files...')
    run_command(cleanup)
    print('\n==> Finished at',datetime.now().strftime('%H:%M')+'.\n')
    return


if __name__ == "__main__":
    main()
