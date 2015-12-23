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

from functions import *

def main():
	# event_times = get_sunrise_events()
	# print(event_times)
	still_interval = 1000	# still interval in ms
	# wait_start(event_times, still_interval)
	# print "==================================="
	# print "========== ",datetime.today().strftime("%d %b %Y")," =========="
	# print "==================================="

	# testing
	test_times = {'dawn': u'18:23', 'sunshine': u'19:23'}
	print(test_times)
	wait_start(test_times, still_interval)

if __name__ == "__main__":
    main()