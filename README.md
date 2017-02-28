SunPise
===
####How It Works
A Raspberry Pi grabs the sunrise time from the web each morning, and uses its attached camera module to record a time-lapse of the sunrise. It then posts the time-lapse to a [YouTube channel](https://www.youtube.com/channel/UCFsV7YLKRGnAX3VVVQzPAXg) where others can view it.

####Dependencies and Installation
Ensure the following packages are installed before attempting to run `sunpise.py`:

- [python3](https://www.python.org/download/releases/3.0/)
- [python-picamera](https://www.raspberrypi.org/documentation/usage/camera/python/README.md)
- [libav-tools](https://libav.org/)
- [google-api-python-client](https://github.com/google/google-api-python-client)

This script is launched in the Pi's Linux environment using `cron`. You can create the following job by entering the command `crontab -e` job and pasting the following line at the end of the config file :

	0 5 * * * /usr/bin/python3 /home/pi/sunpise/sunpise.py -u -l NYC -e sunrise >> /home/pi/sunpise/sunpise_log.txt
	0 17 * * * /usr/bin/python3 /home/pi/sunpise/sunpise.py -u -l NYC -e sunset >> /home/pi/sunpise/sunpise_log.txt
	* * * * * /home/pi/sunpise/tunnel.sh start rgiuliani 72.229.28.185

You can make use of the following commands to debug your camera's setup and network connection:

- View camera feed on Linux:

		nc -l -p 5001 | mplayer -fps 31 -cache 1024 -

- View camera feed on Mac:

		nc -l 5001 | mplayer -fps 31 -cache 1024 -

- Stream camera feed from Pi:

		raspivid -t 999999 -o - | nc [insert the IP address of the client] 5001

####To-do
- Implement error handling
- Switch from `os` to `subprocess`
- Automate OAuth 2.0 initial verification/authentication
