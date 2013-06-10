#!/bin/bash
COMET="$HOME/src.MS/comet/2013010/comet.2013010.linux.exe"

for MZML in $(ls ../mzML/*mzML)
do
  time $COMET -N$PWD $MXML
done
