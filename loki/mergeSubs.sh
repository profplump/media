#!/bin/sh

BASE_FILE="${1}"
if [ -z "${BASE_FILE}" -o ! -e "${BASE_FILE}" ]; then
  echo "Invalid base file: ${BASE_FILE}" 1>&2
  exit 1
fi

BASE="`basename "${BASE_FILE}"`"
DIR="`dirname "${BASE_FILE}"`"
SE="`echo "${BASE}" | sed 's%^.*\(S[0-9][0-9]E[0-9][0-9]*\).*$%\1%'`"
if [ -z "${SE}" ]; then
  echo "No SeasonEpisode block in base file: ${BASE}" 1>&2
  exit 1
fi

MUX_SUBS=""
IFS=$'\n'
for i in \
  `find "${DIR}" -type f -path "*${SE}*" -a \
    \( -name '*.srt' -o -name '*.vtt' -o -name '*.idx' \)`;
do
  case "${i}" in
    *.vtt)
      ;;
    *)
      ;;
  esac
  echo $i
done
