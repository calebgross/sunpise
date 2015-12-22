#!/usr/bin/python

# Charlottesville Sunrise Project
# Written by Caleb Gross
# University of Virginia
#
# A Raspberry Pi (Model B) grabs the sunrise time from the web, and
# records a timelapse of the sunrise each morning. It then posts the
# timelapse to a YouTube channel where others can view it.
#
# Uses:
# Raspberry Pi Model B
# Raspberry Pi Camera Module
# crontab
# Wi-Fi module

from bs4 import BeautifulSoup
import requests
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime, time
from time import sleep

# get Charlottesville sunrise time from the web
def getSunrise():
	url = "http://www.timeanddate.com/astronomy/usa/kailua-kona"
	r = requests.get(url).text
	data = r.text
	soup = BeautifulSoup(data)
	tag = soup.find("td", {"class" : "dawn"})
	dawn = tag.text						# sun begins to rise
	tag = soup.find("td", {"class" : "sunshine"})
	sunshine = tag.text					# sun is fully risen
	return [dawn, sunshine]					# return times

# at dawn, begin timelapse
def wait_start(sunTimes, still_interval):
	startTime = time(*(map(int, sunTimes[0].split(':'))))
	now = datetime.today().time()
	while startTime > now:
		print(now.strftime("%H:%M") + " not yet " + startTime.strftime("%H:%M"))
		sleep(60)					# wait for 60 seconds before trying again
		now = datetime.today().time()
	capture(sunTimes, still_interval)			# 1) get pics
	stitch()						# 2) create timelapse
	upload()						# 3) upload to YouTube
	cleanup()						# 4) delete files
	print("Done! at ",datetime.today().time().strftime("%H:%M"),"\n")

def runCommand(command):
	shellCommand = command
	event = Popen(shellCommand, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
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
	startTime = map(int, sunTimes[0].split(':'));
	start_seconds = startTime[0] * 3600 + startTime[1] * 60	# start time in sec
	endTime = map(int, sunTimes[1].split(':'));
	end_seconds = endTime[0] * 3600 + endTime[1] * 60       # end time in sec
	print("Start time is: ",startTime)
	print("Start seconds is:",start_seconds)
	print("End time is: ",endTime)
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
	testStills = "raspistill \
        -o image_%04d.jpg \
        -tl " + str(still_interval) + " \
        -t " + str(total_time)
	runCommand(testStills)

# compile video from frames
def stitch():
	getStills = "ls *.jpg > stills.txt"
	makeVideo = "mencoder \
        -nosound \
        -ovc lavc \
        -lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 \
        -vf scale=1920:1080 \
        -o tlcam.avi \
        -mf type=jpeg:fps=24 mf://@stills.txt"
	print('\n',"==> Step 2 of 4: Stitching frames together...")
	runCommand(getStills)
	runCommand(makeVideo)

# upload to youtube
def upload():
	date = datetime.today().strftime("%d %b %Y")
	uploadVideo = "/usr/local/bin/youtube-upload \
        -m <email> \
        -p <password> \
        -t 'Charlottesville Sunrise - " + date + "' -c 'Entertainment' \
        tlcam.avi"
	print('\n',"==> Step 3 of 4: Uploading video...")
	runCommand(uploadVideo)

# delete files
def cleanup():
	removeFiles = "rm *.jpg; rm tlcam.avi"
	print('\n',"==> Step 4 of 4: Removing files...")
	runCommand(removeFiles)

# main loop
getSunrise()
# print "==================================="
# print "========== ",datetime.today().strftime("%d %b %Y")," =========="
# print "==================================="
# times = getSunrise()
# still_interval = 1000	# still interval in ms
# print "Sunrise times: ",times
# wait_start(times, still_interval)

# testing
#testTimes = times
#testTimes[0] = u'18:23' # custom start time
#testTimes[1] = u'19:23' # custom end time
#print testTimes
#wait_start(testTimes, still_interval)
