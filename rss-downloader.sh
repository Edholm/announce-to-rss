#!/usr/bin/bash

url="$1"
dest="$2"
interval=1800  # 30*60 seconds

if [ -z "$url" ] || [ -z "$dest" ]; then
    echo RSS feed URL and output destination need to be supplied.
    exit 1
fi

while true ; do
    wget "$url" -O "$dest" -nv
    touch "$dest"
    sleep $interval
done
