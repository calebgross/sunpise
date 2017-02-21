#!/bin/bash

start_ngrok_cmd="/usr/local/bin/ngrok tcp 22"

if [ $(ps -ef | grep "$start_ngrok_cmd" | grep -v grep | wc -l) -eq 0 ]; then
    echo "Starting ngrok..."
    eval "$start_ngrok_cmd > /dev/null &" 
else
    echo "ngrok already running."
fi
