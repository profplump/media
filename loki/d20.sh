#!/bin/bash
set -e

DST="${1}"
SRC="${2}"
SUBS="${3}"
OFFSET="${4}"

# Sanity
if [ ! -r "${SRC}" ] || [ ! -r "${SUBS}" ]; then
	echo "Invalid source or subtitles: ${SRC} | ${SUBS}" 1>&2
	exit 1
fi
if [ -e "${DST}" ]; then
	echo "Invalid destination: ${DST}" 1>&2
	exit 1
fi
if [ -z "${OFFSET}" ]; then
	OFFSET=0
fi

SUBS_SRT="`mktemp -t 'd20subs'`"
dos2unix.pl "${SUBS}" | vtt_srt.pl | srt_shift.pl "${OFFSET}" - > "${SUBS_SRT}"

mkvmerge -o "${DST}" "${SRC}" "${SUBS_SRT}"
rm -f "${SUBS_SRT}"
mkvpropedit "${DST}" --edit track:s1 --set language=eng --edit track:a1 --set language=eng
