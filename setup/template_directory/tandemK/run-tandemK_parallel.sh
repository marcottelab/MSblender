#!/bin/bash

lock_and_run() {
	lockdir=./$1.lock
	if mkdir "$lockdir"
	then    
		echo >&2 "successfully acquired lock: $lockdir"
		../../MSblender/extern/tandem.linux.exe $1
	else    
		echo >&2 "cannot acquire lock, giving up on $lockdir"
		exit 0
	fi
}
export -f lock_and_run

~/parallel --gnu --j 12 --no-notice lock_and_run ::: *tandemK.xml

wait
date

