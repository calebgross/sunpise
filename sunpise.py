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

debug          = True            # development flag
still_interval = 1000            # still interval in milliseconds
location       = 'kailua-hawaii' # camera location
title_margin   = 20
title_char     = '~'

def main():

	# log heading
	title = (re.sub(r'-.*', '', location).capitalize() + ' - ' + 
		datetime.now().strftime('%d %b %Y'))
	print(title_char * (2 * title_margin + 2 + len(title)))
	print(title_char * title_margin, title, title_char * title_margin)
	print(title_char * (2 * title_margin + 2 + len(title)))

	# 1) get times for dawn and sunshine
	if debug:
		event_times = {
		'dawn': datetime.now().replace(hour=0, minute=45, microsecond=0),
		'sunshine': datetime.now().replace(hour=7, minute=5, microsecond=0)
		}
	else:
		event_times = get_event_times()      
	for key in sorted(event_times.keys()):
		print(key.capitalize() + ':' + ' ' *(9-len(key)) +
			event_times[key].strftime('%H:%M'))

	# 2) wait until dawn to start timelapse
	wait_until(event_times['dawn'])

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
