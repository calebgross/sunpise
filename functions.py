#!/usr/bin/python

# SunpPise
# Caleb Gross

import requests
import re
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime
from time import sleep

# get times for dawn and sunshine from the web
def get_event_times():
	url = 'http://www.gaisma.com/en/location/kailua-hawaii.html'
	html = requests.get(url).text
	events = dict.fromkeys(['dawn', 'sunshine'])
	today = datetime.now().date()
	for event in events.keys():
		pattern = r'<td class="'+event+'">(?P<time>.*)</td>'
		match = re.search(pattern, html).group(1)
		event_time = datetime.strptime(match, '%H:%M').replace(
			year=today.year, month=today.month, day=today.day)
		events[event] = event_time
	return events

# wait until dawn
def wait_until_dawn(dawn):
	if datetime.now() <= dawn:
		print('were good')
		return
	else:
		# print('Currently',datetime.strftime('%H:%M', datetime.now()+',',
		# 	  'waiting until',datetime.strftime('%H:%M', dawn))
		time_delta = dawn - datetime.now()
		seconds_until_dawn = time_delta.seconds
		print(seconds_until_dawn)
		sleep(seconds_until_dawn+5)

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
def capture(sunTimes, capture_interval):
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
	capture_interval_sec = capture_interval/float(1000)		# still interval in sec
	now = datetime.today().time().strftime("%H:%M")
	print('\n',"==> Step 1 of 4: Taking stills...")
	print("Starting at " + str(now) + ", \
		capturing still every " + str(capture_interval_sec) + "s \
		for " + str(total_time_min) + "min.")
	test_stills = "raspistill \
	-o image_%04d.jpg \
	-tl " + str(capture_interval) + " \
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
	upload = "/usr/local/bin/youtube-upload \
	-m <email> \
	-p <password> \
	-t 'Kailua Sunrise - " + date + "' -c 'Entertainment' \
	tlcam.avi"
	print('\n',"==> Step 3 of 4: Uploading video...")
	run_command(upload)

# delete files
def cleanup():
	cleanup = "rm *.jpg; rm tlcam.avi"
	print('\n',"==> Step 4 of 4: Removing files...")
	run_command(cleanup)
