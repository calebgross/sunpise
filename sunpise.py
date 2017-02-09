#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests, re, textwrap, os, sys, argparse, json, upload_video
from   argparse         import Namespace
from   apiclient.errors import HttpError
from   subprocess       import Popen, PIPE, STDOUT
from   datetime         import datetime
from   time             import sleep

parser = argparse.ArgumentParser()
parser.add_argument('-D','--debug', action='store_true', help='Debug mode', default=False)
parser.add_argument('-u','--upside-down', action='store_true', default=False, help='Lens positioned upside-down')
parser.add_argument('-e','--event-type', choices=['sunrise', 'sunset'], default='sunrise', help='Sunrise or sunset')
parser.add_argument('-i','--still-interval', default=1000, help='Exposure length',)
parser.add_argument('-d','--directory', default=os.getcwd()+'/', help='Directory where sunpise files are stored')
parser.add_argument('-s','--client-secrets', default='client_secrets.json', help='Client secrets file')
parser.add_argument('-l','--location', required=True, help='Camera\'s geographic location')
args = vars(parser.parse_args())

ip_info        = json.loads(requests.get('http://ipinfo.io').text)
city           = ip_info['city']
coordinates    = ip_info['loc'].split(',')

def main():

    # log heading
    print_header()

    # 1) get event times
    event_times = get_event_times()

    # 2) wait until dawn to start timelapse
    wait_until(event_times['start'])

    # 3) start capturing stills
    capture(event_times) 

    # 4) make video
    video_name = stitch()            

    # 5) upload video
    upload(video_name)             

    # 6) remove files from device      
    cleanup()                  

    print('\n==> Finished at',datetime.now().strftime('%H:%M')+'.\n')

def run_command(command):

    # log command
    printed_command = command
    prefix = 'Executing command: '
    wrapper = textwrap.TextWrapper(initial_indent=prefix,
        width=80, subsequent_indent=' '*int((len(prefix)/4)))
    print(wrapper.fill(printed_command))

    # execute command
    if not args['debug']:
        os.system(command)

def print_header():
    title_char = '~'
    title = (re.sub(r'-.*', '', args['location']).capitalize() + ' ' +
        args['event_type'].capitalize()  + ' ' + '-'*(len(args['event_type'])%2+2) + ' ' + 
        datetime.now().strftime('%d %b %Y'))
    title_margin = int(40 - float(len(title) + 2)/2)
    print(title_char * (2 * title_margin + 2 + len(title)))
    print(title_char * title_margin, title, title_char * title_margin)
    if args['debug']:
        print(title_char * (2 * title_margin + 2 + len(title)))
        print(title_char * 34, 'DEBUG MODE', title_char * 34)
    print(title_char * (2 * title_margin + 2 + len(title)), end='\n\n')

def print_times(event_times):
    for key in reversed(sorted(event_times.keys())):
        print(key.capitalize() + ':' + ' ' *(9-len(key)) +
            event_times[key].strftime('%H:%M'))

# get times for dawn and sunshine from the web
def get_event_times():

   # get start/end datetimes for sunrise/sunset
    payload     = {'lat': coordinates[0], 'lng': coordinates[1], 'date': 'today'}
    url         = 'http://api.sunrise-sunset.org/json'
    response    = json.loads(requests.get(url, params=payload).text)['results']
    
    # initialize data structures to iterate through response
    event_times = {}
    today       = datetime.now().date()
    event_names = {
        'sunrise': {
            'start': 'civil_twilight_begin',
            'end':   'sunrise'
        },
        'sunset' : {
            'start': 'sunset',
            'end':   'civil_twilight_end'
        }    
    }

    # for events start and end
    for event_name in sorted(event_names[args['event_type']].keys()):
        
        # create datetime with today's date and respective event time
        event_times[event_name] = datetime.strptime(
            response[event_names[args['event_type']][event_name]][:4], '%H:%M').replace(
            year=today.year, month=today.month, day=today.day)
    
    # log and return event times
    print_times(event_times)
    return event_times

# wait until dawn
def wait_until(start):

    print('Currently', datetime.now().time().strftime('%H:%M')+',', end=' ')

    # check if sun is rising/setting
    if datetime.now() >= start or args['debug']:
        if args['event_type'] == 'sunrise':
            action = 'rising'
        elif args['event_type'] == 'sunset':
            action = 'setting'
        print('sun has started ' + action + '. Starting timelapse.')
        return

    # wait until start and check again
    else:
        time_delta = start - datetime.now()
        seconds_until_start = time_delta.seconds + 5
        print('sleeping',str(seconds_until_start),
              'seconds until',start.strftime('%H:%M'+'.'))
        sleep(seconds_until_start)
        wait_until(start)

# take pictures
def capture(event_times):
    capture_interval = event_times['end'] - event_times['start']
    #capture_interval = 300000
    capture = (
        'raspistill ' +
        '--burst ' + 
        '-o ' + args['directory'] + 'stills/still_%04d.jpg ' +
        '-tl ' + str(args['still_interval']) + ' ' +
        '-t ' + str(capture_interval.seconds*1000)
        )
    if args['upside_down']:
        capture += ' --hflip --vflip'
    print('\n==> Step 1 of 4 (' +
        datetime.now().strftime('%H:%M') + '): Capturing stills...')
    print('Starting at ' + event_times['start'].strftime('%H:%M') + 
        ', capturing stills every ' +
        str(int(args['still_interval']/1000))+ ' seconds for ' +
        str(int(capture_interval.seconds/60)) + ' minutes.')
    run_command(capture)  
    
    # account for unprocessed stills so avconv can process input
    if not args['debug']:
        filenames = os.listdir('/home/pi/sunpise/stills')
        change_filename = lambda filename, new_filename: ('mv ' +
            '/home/pi/sunpise/stills/' + filename +
            ' ' +
            '/home/pi/sunpise/stills/' + new_filename
            )
        i = 0
        for filename in sorted(filenames):
            new_filename = 'still_' + str(int(i)).zfill(4) + '.jpg'
            os.system(change_filename(filename, new_filename))
            i += 1

    return

# compile video from frames
def stitch():
    video_name = 'sunpise' + datetime.now().strftime('_%m-%d-%y_%H-%M') + '.avi'
    make_video = (
        'avconv ' +
        '-f image2 ' + 
        '-i ' + args['directory'] + 'stills/still_%04d.jpg ' + 
        '-r 12 ' + 
        '-s 1920x1080 ' + 
        args['directory'] + video_name
        )
    print('\n==> Step 2 of 4 (' +
        datetime.now().strftime('%H:%M') + '): Stitching frames together...')
    run_command(make_video)
    return video_name

# upload to YouTube
def upload(video_name):
    location_formatted = re.sub(r'-.*', '', args['location']).capitalize()
    event_type_formatted = args['event_type'].capitalize()
    if args['debug']:
        args['directory'] = ''
        video_name = 'test.avi'
    yt_args = Namespace(
        auth_host_name='localhost', 
        auth_host_port=[8080, 8090], 
        category='22', 
        description='Test Description', 
        file=args['directory'] + video_name, 
        keywords='', 
        logging_level='ERROR',
        noauth_local_webserver=True,
        privacyStatus='public',
        title=location_formatted + ' ' + event_type_formatted + ' - ' + 
            datetime.now().strftime('%d %b %Y')
        )
    youtube = upload_video.get_authenticated_service(yt_args)
    print('\n==> Step 3 of 4 (' +
        datetime.now().strftime('%H:%M') + '): Uploading video...')
    try:
        upload_video.initialize_upload(youtube, yt_args)
    except HttpError as e:
        print(("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)))
    return

# delete files
def cleanup():
    cleanup = 'rm ' + args['directory'] + 'stills/*.jpg; rm ' + args['directory'] +'*.avi'
    print('\n==> Step 4 of 4 (' +
        datetime.now().strftime('%H:%M') + '): Removing files...')
    run_command(cleanup)
    return

if __name__ == "__main__":
    main()