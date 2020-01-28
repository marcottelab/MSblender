#!/bin/bash
CRUX_EXE="$HOME/src/crux/crux-3.2.Linux.x86_64/bin/crux"
NUM_THREADS=8

for PIN in $(ls *.pep.xml)
do
  OUT_NAME=$(basename $PIN)
  OUT_NAME=${OUT_NAME/.pep.xml/}
  echo $PIN $OUT_NAME

  $CRUX_EXE percolator --overwrite T --decoy-prefix rv_ --output-dir . --fileroot $OUT_NAME --protein T $PIN
done
