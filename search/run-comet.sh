#!/bin/bash
COMET="$HOME/src.MS/comet/2013010/comet.2013010.linux.exe"

for MZML in $(ls ../mzML/*mzML)
do
  OUT=$(basename $MZML)
  OUT=$PWD"/"${OUT/.mzML/}
  time $COMET -N$OUT $MZML
done
