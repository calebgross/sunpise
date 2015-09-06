SunPise
===
####How It Works
A Raspberry Pi (Model B) grabs the sunrise time from the web each morning, and uses its attached camera module to record a time-lapse of the sunrise. It then posts the time-lapse to a [YouTube channel](https://www.youtube.com/channel/UCFsV7YLKRGnAX3VVVQzPAXg) where others can view it.

The script is launched in the Pi's Linux environment using `cron`. You can create the following job by entering the command `crontab -e` job and pasting the following line at the end of the config file :

	0 5 * * * python ~/sunpise/sunpise.py >> ~/sunpise/sunpise_log.xt

You can make use of the following commands to debug your camera's setup and network connection:

View camera feed on Linux:

	nc -l -p 5001 | mplayer -fps 31 -cache 1024 -

View camera feed on Mac:

	nc -l 5001 | mplayer -fps 31 -cache 1024 -

Stream from Pi:

	raspivid -t 999999 -o - | nc [insert the IP address of the client] 5001

####To-do
* Refactor and standardize code
* Rewrite the main loop to be more useable/readable
* Change the sunrise web page to make it easier to use the camera in other locations