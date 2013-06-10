#!/bin/bash
#$ -V
#$ -cwd
#$ -j y
#$ -o $JOB_NAME.o$JOB_ID
#$ -pe 1way 8
#$ -q long
#$ -l h_rt=24:00:00
#$ -M $EMAIL
#$ -m be
#$ -P hpc
set -x

#$ -N comet.WuT
COMET="$HOME/src.MS/comet/2013010/comet.2013010.linux.exe"

for MZML in $(ls ../mzML/*mzML)
do
  OUT=$(basename $MZML)
  OUT=$PWD"/"${OUT/.mzML/}
  time $COMET -N$OUT $MZML
done
