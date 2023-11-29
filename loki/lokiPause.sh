#!/bin/bash

# Duration
H="${1}"
if [ -z "${H}" ]; then
  H=$(( 23 - `date +%H` ))
fi

# Stop
PID=$(ps Ax | grep -v grep | grep HandBrake | awk '{print $1}' | head -n 1)
kill -SIGSTOP $PID

# Restart
(sleep $(( 3600 * $H )) && \
  kill -SIGCONT $PID ) \
  & disown
