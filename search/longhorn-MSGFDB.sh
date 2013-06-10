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

module load jdk64

DB="$SCRATCH/HumanCells/DB.prot/HUMAN_ens69_prot_combined.fa"
MSGFDB_JAR="$HOME/src.MS/MSGFDB/20120607/MSGFDB.jar"

#$ -N MSGFDB.WuT

DBNAME=$(basename $DB)
DBNAME=${DBNAME/.fa/}

for MZML in $(ls ../mzML/*mzML)
do
  OUT=$(basename $MZML)
  OUT=${OUT/.mzML/}"."$DBNAME".MSGFDB_out"
  time java -Xmx8000M -jar $MSGFDB_JAR -d $DB -s $MZML -t 30ppm -e 1 -nnet 0 -n 5 -o $OUT
done
