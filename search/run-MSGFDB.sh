#!/bin/bash
DB="$SCRATCH/HumanCells/DB.prot/HUMAN_ens69_prot_combined.fa"
MSGFDB_JAR="$HOME/src.MS/MSGFDB/20120607/MSGFDB.jar"

DBNAME=$(basename $DB)
DBNAME=${DBNAME/.fa/}

for MZXML in $(ls ../mzXML/*mzXML)
do
  OUT=$(basename $MZXML)
  OUT=${OUT/.mzXML/}"."$DBNAME".MSGFDB_out"
  time java -Xmx8000M -jar $MSGFDB_JAR -d $DB -s $MZXML -t 30ppm -e 1 -nnet 0 -n 5 -o $OUT
done
