#!/usr/bin/bash

url="$1"
interval="$2"
dest="$3"

if [ -z "$url" ] || [ -z "$dest" ] || [ -z "$interval" ]; then
    echo RSS feed URL, interval, and output destination need to be supplied
    exit 1
fi

while true ; do
    wget "$url" -O "$dest" -nv
    touch "$dest"
    sleep $interval
done
