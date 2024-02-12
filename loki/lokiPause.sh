#!/bin/bash

# Duration
H="${1}"
if [ -z "${H}" ]; then
  H=$(( 23 - `date +%H` ))
fi

# Find
PID=$(ps Ax | grep -v grep | grep HandBrake | awk '{print $1}' | head -n 1)
if [ -z "${PID}" ]; then
  echo "HandBrake not running" 1>&2
  exit 0
fi

# Stop
kill -SIGSTOP $PID

# Restart
(sleep $(( 3600 * $H )) && \
  kill -SIGCONT $PID ) \
  & disown
