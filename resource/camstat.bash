#!/usr/bin/env bash

echo "[CAMERA STATUS]" > camstat.out
echo "DATE =" $(date) >> camstat.out

HOST="localhost"
PORT=1883
CMD_TOPIC="cmnd/eosrpcam/POWER"
RESP_TOPIC="stat/eosrpcam/POWER"
TIMEOUT=5

TMPFILE="$(mktemp)"
trap 'rm -f "$TMPFILE"' EXIT

mosquitto_sub -h "$HOST" -p "$PORT" -t "$RESP_TOPIC" -C 1 -W "$TIMEOUT" > "$TMPFILE" 2>/dev/null &
SUB_PID=$!

sleep 0.15

mosquitto_pub -h "$HOST" -p "$PORT" -t "$CMD_TOPIC" -n 2>/dev/null || true

wait $SUB_PID 2>/dev/null || true

if [ -s "$TMPFILE" ]; then
    echo "PLUG_STATUS =" $(cat "$TMPFILE") >> camstat.out
else
    echo "PLUG_STATUS = None" >> camstat.out
fi

if gphoto2 --auto-detect 2>/dev/null | grep -q "Canon"; then
    echo "CAMERA_STATUS = Connected" >> camstat.out
else
    echo "CAMERA_STATUS = None" >> camstat.out
fi