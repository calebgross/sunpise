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

from functions import *

def main():
	event_times = get_sunrise_events()
	print(event_times)
	still_interval = 1000	# still interval in ms
	wait_start(event_times, still_interval)
	# main loop
	# print "==================================="
	# print "========== ",datetime.today().strftime("%d %b %Y")," =========="
	# print "==================================="

	# testing
	#testTimes = times
	#testTimes[0] = u'18:23' # custom start time
	#testTimes[1] = u'19:23' # custom end time
	#print testTimes
	#wait_start(testTimes, still_interval)

if __name__ == "__main__":
    main()