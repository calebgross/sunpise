SunPise
===
####How It Works
A Raspberry Pi (Model B) grabs the sunrise time from the web each morning, and uses its attached camera module to record a time-lapse of the sunrise. It then posts the time-lapse to a [YouTube channel](https://www.youtube.com/channel/UCFsV7YLKRGnAX3VVVQzPAXg) where others can view it.

The script is launched in the Pi's Linux environment using `crontab`.

####To-do
* Refactor and standardize code
* Rewrite the main loop to be more useable/readable
* Change the sunrise web page to make it easier to use the camera in other locations