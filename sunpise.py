#!/usr/bin/python
# -*- coding: utf-8 -*-

from functions import *

if len(sys.argv) == 2:
    event_type = sys.argv[1]
else:
    event_type = 'sunrise'
debug          = True           
internet       = True           
still_interval = 1000           
location       = 'kailua-hawaii'
sunpise_dir    = '/home/pi/sunpise/'
client_secrets = 'client_secrets.json'
upside_down    = True
ip_info        = json.loads(requests.get('http://ipinfo.io').text)
city           = ip_info['city']
coordinates    = ip_info['loc'].split(',')

def main():

    # log heading
    print_title()

    # 1) get event times
    event_times = get_event_times()
    print_times(event_times)

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

if __name__ == "__main__":
    main()
