#!/usr/bin/python

# SunpPise
# Caleb Gross
#
# A Raspberry Pi (Model B) grabs the sunrise time from the web, and
# records a timelapse of the sunrise each morning. It then posts the
# timelapse to a YouTube channel where others can view it.
#
# Uses:
# - Raspberry Pi Model B
# - Raspberry Pi Camera Module
# - crontab
# - Wi-Fi module
#
# Dependencies:
# - raspistill
# - mencoder
# - youtube-upload

import requests
import re
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime, time
from time import sleep

# get times for dawn and sunshine from the web
def get_sunrise_events():
	url = 'http://www.gaisma.com/en/location/kailua-hawaii.html'
	html = requests.get(url).text
	events = dict.fromkeys(['dawn', 'sunshine'])
	for event in events.keys():
		pattern = r'<td class="'+event+'">(?P<time>.*)</td>'
		match = re.search(pattern, html).group(1)
		events[event] = match
	return events

# at dawn, begin timelapse
def wait_start(event_times, still_interval):
	start_time = time(*(map(int, event_times['dawn'].split(':'))))
	now = datetime.today().time()
	while start_time > now:
		print(now.strftime("%H:%M") + " is not yet " + start_time.strftime("%H:%M"))
		sleep(60)                       # wait for 60 seconds before trying again
		now = datetime.today().time()
	capture(sunTimes, still_interval)   # 1) get pics
	stitch()                            # 2) create timelapse
	upload()                            # 3) upload to YouTube
	cleanup()                           # 4) delete files
	print("Done at",datetime.today().time().strftime("%H:%M"),"\n")

def run_command(command):
	event = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
	# poll process for new output until finished
	while True:
        	nextline = event.stdout.readline()
        	if nextline == '' and event.poll() != None:
        		break
        		if nextline == '' or nextline.isspace():
        			break
        			print(nextline),

# take pictures
def capture(sunTimes, still_interval):
	# take a picture every [30] seconds for [60] minutes
	start_time = map(int, sunTimes[0].split(':'));
	start_seconds = start_time[0] * 3600 + start_time[1] * 60	# start time in sec
	end_time = map(int, sunTimes[1].split(':'));
	end_seconds = end_time[0] * 3600 + end_time[1] * 60       # end time in sec
	print("Start time is: ",start_time)
	print("Start seconds is:",start_seconds)
	print("End time is: ",end_time)
	print("End seconds is:",end_seconds)
	total_time = (end_seconds - start_seconds) * 1000 	# total time in ms
	total_time_min = total_time/float(60000)                # total time in min
	print("Total time is: ",total_time)
	still_interval_sec = still_interval/float(1000)		# still interval in sec
	now = datetime.today().time().strftime("%H:%M")
	print('\n',"==> Step 1 of 4: Taking stills...")
	print("Starting at " + str(now) + ", \
        capturing still every " + str(still_interval_sec) + "s \
        for " + str(total_time_min) + "min.")
	test_stills = "raspistill \
        -o image_%04d.jpg \
        -tl " + str(still_interval) + " \
        -t " + str(total_time)
	run_command(test_stills)

# compile video from frames
def stitch():
	get_stills = "ls *.jpg > stills.txt"
	make_video = "mencoder \
        -nosound \
        -ovc lavc \
        -lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 \
        -vf scale=1920:1080 \
        -o tlcam.avi \
        -mf type=jpeg:fps=24 mf://@stills.txt"
	print('\n',"==> Step 2 of 4: Stitching frames together...")
	run_command(get_stills)
	run_command(make_video)

# upload to youtube
def upload():
	date = datetime.today().strftime("%d %b %Y")
	upload_video = "/usr/local/bin/youtube-upload \
        -m <email> \
        -p <password> \
        -t 'Charlottesville Sunrise - " + date + "' -c 'Entertainment' \
        tlcam.avi"
	print('\n',"==> Step 3 of 4: Uploading video...")
	run_command(upload_video)

# delete files
def cleanup():
	remove_files = "rm *.jpg; rm tlcam.avi"
	print('\n',"==> Step 4 of 4: Removing files...")
	run_command(remove_files)
