#!/bin/bash

LIST="/aamon/jobs/transfers.list"
GET_SCRIPT="/aamon/code/transfer/get_files.bash"
TMPDIR="/aamon/tmp"
declare -A FIFOS
declare -A PIDS

mkdir -p "$TMPDIR"

mapfile -t TASKS < <(tail -n +2 "$LIST")
mapfile -t THREADS < <(printf '%s\n' "${TASKS[@]}" | awk '{print $4}' | sort -n -u)

cleanup() {
  for fifo in "${FIFOS[@]:-}"; do
    rm -f "$fifo"
  done
}
trap cleanup EXIT

for t in "${THREADS[@]}"; do
  fifo="$TMPDIR/transfer_thread_${t}.fifo"
  rm -f "$fifo"
  mkfifo "$fifo"
  FIFOS["$t"]="$fifo"

  (
    while IFS= read -r task || [ -n "$task" ]; do
      # split safely into array (preserves internal fields, collapses whitespace)
      read -r -a parts <<< "$task"
      device=${parts[0]:-}
      host=${parts[1]:-}
      port=${parts[2]:-}
      # trim accidental surrounding whitespace (optional)
      device=${device#"${device%%[![:space:]]*}"}; device=${device%"${device##*[![:space:]]}"} 
      host=${host#"${host%%[![:space:]]*}"};   host=${host%"${host##*[![:space:]]}"} 
      port=${port#"${port%%[![:space:]]*}"};   port=${port%"${port##*[![:space:]]}"} 
      "$GET_SCRIPT" "$device" "$host" "$port"
    done < "$fifo"
  ) &
  PIDS["$t"]=$!
done

for line in "${TASKS[@]}"; do
  # split dispatcher line into fields robustly and trim
  read -r -a parts <<< "$line"
  device=${parts[0]:-}; host=${parts[1]:-}; port=${parts[2]:-}; thread=${parts[3]:-}
  printf '%s %s %s\n' "$device" "$host" "$port" > "${FIFOS[$thread]}"
done

for pid in "${PIDS[@]}"; do
  wait "$pid"
done

bash /aamon/code/transfer/put_files.bash