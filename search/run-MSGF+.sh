#!/bin/bash

DB="$SCRATCH/HumanCells/DB.prot/HUMAN_ens69_prot_combined.fa"

MSGFplus_JAR="$HOME/src.MS/MSGF+/20130410/MSGFPlus.jar"

DBNAME=$(basename $DB)
DBNAME=${DBNAME/.fa/}

for MZML in $(ls ../mzML/*mzML)
do
  OUT=$(basename $MZML)
  OUT=${OUT/.mzML/}"."$DBNAME".MSGFDB.mzid"
  time java -Xmx8000M -jar $MSGFplus_JAR -d $DB -s $MZML -o $OUT -t 30ppm -tda 0 -ntt 0
done
