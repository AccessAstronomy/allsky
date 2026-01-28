#!/bin/bash

device=$1
host=$2
port=$3

rasp_path=/home/Archive/
server_path=/aamon/transfers/allsky/

done=0
while [ $done -eq 0 ]; do
    nc -vz $host $port
    if [ $? -eq 0 ]; then
        rsync -arzP --timeout=15 --remove-source-files -e "ssh -p $port -o ServerAliveInterval=5 -o ServerAliveCountMax=8" "$device@$host:$rasp_path" "$server_path"
        if [ $? -eq 0 ]; then
            done=1
        else
            sleep 15
        fi
    else
        done=1
    fi
done