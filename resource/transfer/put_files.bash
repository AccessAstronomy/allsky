#!/bin/bash

server_path=/dataserver/users/skycams/
local_path=/aamon/transfers/allsky/

mkdir -p /aamon/data/reports
find /aamon/transfers -type f \( -iname '*.log' -o -iname '*.dat' \) -exec cp --parents -t /aamon/data/reports {} +

done=0
while [ $done = 0 ]
do
        rsync -arzP --remove-source-files --ignore-existing $local_path telescoop@kapteyn.astro.rug.nl:$server_path -e ssh
        if [ "$?" = "0" ] ; then
            done=1
        else
            sleep 5
        fi
done
