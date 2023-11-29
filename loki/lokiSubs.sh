#!/bin/sh
if [ -z "${EXT}" ]; then
  EXT="mkv"
fi
OUT_DIR=""
if [ -n "${1}" ]; then
  OUT_DIR="${1}/"
fi

for i in *".${EXT}"; do
  j="`echo "${i}" | sed 's%\.'"${EXT}"'$%%'`"
  mkvmerge -o "${OUT_DIR}${j}.mkv" "${i}" "Subs/${j}/"*'_English.srt'
done
