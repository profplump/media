#!/bin/sh

BASE_DIR="${HOME}/bin/media/TVDB"
TV_DIR="/Volumes/Shared/TV"

source "${BASE_DIR}/venv/bin/activate"
if [ "${1}" == "ALL" ]; then
  for i in "${TV_DIR}/"*; do
    python3 "${BASE_DIR}/main.py" "${i}"
  done
else
  python3 "${BASE_DIR}/main.py" "${@}"
fi
