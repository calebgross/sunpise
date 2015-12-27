#!/usr/bin/python

import requests
import re
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime
from time import sleep

from sunpise import debug, still_interval, location
from credentials import youtube

def run_command(command):

	# sanitize and log command
	printed_command = command
	for credential in youtube.values():
		printed_command = printed_command.replace(credential, '########')
	print('Executing command:',printed_command)

	# execute command
	if not debug:
		event = Popen(
			command,
			shell=True,
			stdin=PIPE,
			stdout=PIPE,
			stderr=STDOUT,
			close_fds=True
			)

		# poll process for new output until finished
		while True:
			next_line = event.stdout.readline()
			if next_line == '' and event.poll() != None:
				break
			if next_line == '' or next_line.isspace():
				break
			print(next_line),

# get times for dawn and sunshine from the web
def get_event_times():

	# retrieve data
	url = 'http://www.gaisma.com/en/location/' + location + '.html'
	html = requests.get(url).text

	# parse hypertext
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
def wait_until(dawn):

	print('Currently',datetime.now().time().strftime('%H:%M')+',', end=' ')

	# check if sun is rising
	if datetime.now() >= dawn:
		print('sun has started rising. Starting timelapse.')
		return

	# wait until dawn and check again
	else:
		time_delta = dawn - datetime.now()
		seconds_until_dawn = time_delta.seconds + 5
		print('sleeping',str(seconds_until_dawn),
			  'seconds until',dawn.strftime('%H:%M'+'.'))
		sleep(seconds_until_dawn)
		wait_until(dawn)

# take pictures
def capture(event_times):
	capture_interval = event_times['sunshine'] - event_times['dawn']
	capture = (
		'raspistill ' +
		'-o still_%04d.jpg ' +
		'-tl ' + str(still_interval) + ' ' +
		'-t ' + str(capture_interval.seconds*1000)
		)
	print('\n==> Step 1 of 4: Capturing stills...')
	print('Starting at ' + event_times['dawn'].strftime('%H:%M') + 
		', capturing stills every ' +
		str(int(still_interval/1000))+ ' seconds for ' +
		str(int(capture_interval.seconds/60)) + ' minutes.')
	run_command(capture)
	return

# compile video from frames
def stitch():
	video_name = 'sunpise' + datetime.now().strftime('_%m-%d-%y_%H-%M') + '.avi'
	make_video = (
		'mencoder ' +
		'mf://still_*.jpg' +
		'-mf type=jpg:fps=24' +
		'-nosound ' +
		'-ovc lavc ' +
		'-lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 ' +
		'-vf scale=1920:1080 ' +
		'-o ' + video_name
		)
	print('\n==> Step 2 of 4: Stitching frames together...')
	run_command(make_video)
	return video_name

# upload to YouTube
def upload(video_name):
	location_formatted = re.sub(r'-.*', '', location).capitalize()
	upload = (
		'/usr/local/bin/youtube-upload ' + 
		'-m ' + youtube['email'] + ' ' +
		'-p ' + youtube['password'] + ' ' +
		'-t "' + location_formatted + ' Sunrise - ' +
			datetime.now().strftime('%d %b %Y') + '" ' +
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

