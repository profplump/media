#!/bin/bash

MPATH="/Volumes/Shared/TV"
if [ -n "${1}" ]; then
	if [ -d "${1}" ]; then
		MPATH="${1}"
	fi
fi
echo "Using MPATH: ${MPATH}"

RUNCHECK="`ps auwx | grep xargs | grep video/findRecode0`"
if [ -z "${RUNCHECK}" ]; then
	export NO_LAST_RECODE_FILE=1
	find "${MPATH}" -type d -print0 | \
		xargs -0 -I RPLSTR -n 1 ~/bin/video/findRecode0 RPLSTR | \
		xargs -0 -n 1 -t ~/bin/video/recode &
	RUNCHECK=$!
	echo "Started recoder as PID: ${RUNCHECK}"
else
	echo 'findRecode already running:'
	echo "${RUNCHECK}"
fi

# Background this too so we can get HB fully detached
(while [ 1 ]; do
	# Slowly
	for i in {1..2}; do
		echo
		sleep 5
	done

	# Grab a status
	HB="`ps auwx | grep -v grep | grep -i handbrake`"
	if [ -z "${HB}" ]; then
		HB="`ps awux | grep -v grep | grep -i video/findRecode`"
	fi
	if [ -z "${HB}" ]; then
		HB="`ps awux | grep -v grep | grep "${RUNCHECK}"`"
	fi

	# Stop when we find nothing to monitor
	if [ -z "${HB}" ]; then
		echo
		echo Done
		date
		echo
		echo
		exit 0
	fi

	# Display status
	echo "${HB}"
	echo
done) &

echo "Started monitor as PID: ${!}"
exit 0
