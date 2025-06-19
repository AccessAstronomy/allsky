#!/bin/bash
bash $HOME/slacker_2.bash $1 spiral_note_pad "#005477"
LOGFILE=$(find /home/Archive/ -type f -name "*.log" -printf "%T@ %p\n" | sort -n | tail -1 | cut -d' ' -f2-)
echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOGFILE"