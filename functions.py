#!/usr/bin/python

# SunpPise
# Caleb Gross

import requests
import re
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime
from time import sleep

def run_command(command):
	print('Executing command:',command)
	# if not testing:
	# 	print('not testing')
	# else:
	# 	print('testing')
		# event = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
		# poll process for new output until finished
		# while True:
		# 	nextline = event.stdout.readline()
		# 	if nextline == '' and event.poll() != None:
		# 		break
		# 	if nextline == '' or nextline.isspace():
		# 		break
		# 		print(nextline),

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
	print('Currently',datetime.now().time().strftime('%H:%M')+',', end=' ')
	if datetime.now() >= dawn:
		print('sun has started rising. Starting timelapse.')
		return
	else:
		time_delta = dawn - datetime.now()
		seconds_until_dawn = time_delta.seconds + 5
		print('sleeping',str(seconds_until_dawn),
			  'seconds until',dawn.strftime('%H:%M'+'.'))
		sleep(seconds_until_dawn)
		wait_until_dawn(dawn)

# take pictures
def capture(event_times, still_interval):
	capture_interval = event_times['sunshine'] - event_times['dawn']
	print('\n==> Step 1 of 4: Capturing stills...')
	print('Starting at ' + event_times['dawn'].strftime('%H:%M') + 
		', capturing stills every ' +
		str(int(still_interval/1000))+ ' seconds for ' +
		str(int(capture_interval.seconds/60)) + ' minutes.')
	capture = (
		'raspistill ' +
		'-o still_%04d.jpg ' +
		'-tl ' + str(still_interval) + ' ' +
		'-t ' + str(capture_interval.seconds*1000)
		)
	run_command(capture)
	return

# compile video from frames
def stitch():
	get_stills = 'ls still_*.jpg > stills_list.txt'
	video_name = 'sunpise_' + datetime.now().strftime('%m-%d-%y_%H-%M') + '.avi'
	make_video = (
		'mencoder ' +
		'-nosound ' +
		'-ovc lavc ' +
		'-lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 ' +
		'-vf scale=1920:1080 ' +
		'-o ' + video_name + 
		'-mf type=jpeg:fps=24 mf://@stills_list.txt'
		)
	print('\n==> Step 2 of 4: Stitching frames together...')
	run_command(get_stills)
	run_command(make_video)
	return video_name

# upload to YouTube
def upload(video_name):
	upload = (
		'/usr/local/bin/youtube-upload ' + 
		'-m <email> ' +
		'-p <password> ' +
		'-t "Kailua Sunrise - ' + datetime.now().strftime('%d %b %Y') + '" ' +
		'-c Entertainment ' + 
		video_name
		)
	print('\n==> Step 3 of 4: Uploading video...')
	run_command(upload)
	return

# delete files
def cleanup():
	cleanup = 'rm *.jpg; rm *.avi'
	print('\n==> Step 4 of 4: Removing files...')
	run_command(cleanup)
	return

