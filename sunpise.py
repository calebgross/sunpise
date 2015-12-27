#!/usr/bin/python

# SunpPise
# Caleb Gross
#
# A Raspberry Pi grabs the sunrise time from the web, and records a timelapse of
# the sunrise each morning. It then posts the timelapse to a YouTube channel
# where others can view it.
#
# Uses:
# - Raspberry Pi Model B
# - Raspberry Pi Camera Module
# - crontab
# - Wi-Fi dongle
#
# Dependencies:
# - raspistill
# - mencoder
# - youtube-upload

from functions import *

testing        = True # development aid
still_interval = 1000 # still interval in ms	

def main():
	print('=================================')
	print('==========',datetime.now().strftime('%d %b %Y'),'==========')
	print('=================================')

	if testing:
		print('Testing!')
		event_times = {
		'dawn': datetime.now().replace(hour=0, minute=45, microsecond=0),
		'sunshine': datetime.now().replace(hour=7, minute=5, microsecond=0)
		}
	else:
		event_times = get_event_times()          
	for key in event_times:
		print(key + ':',event_times[key].strftime('%H:%M'))
	wait_until(event_times['dawn'])     
	capture(event_times) 
	video_name = stitch()                  
	upload(video_name)                     
	cleanup()                            
	print('\n==> Finished at',datetime.now().strftime('%H:%M')+'.\n')

if __name__ == "__main__":
    main()
