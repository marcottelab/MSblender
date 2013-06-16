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

DB="$SCRATCH/HumanCells/DB.prot/HUMAN_uniprot_201306.with_prot_rev.fa"
MSGFplus_JAR="$HOME/src.MS/MSGF+/20130410/MSGFPlus.jar"

DBNAME=$(basename $DB)
DBNAME=${DBNAME/.fa/}

#$ -N MSGF+.Huv

for MZXML in $(ls ../mzXML/*mzXML)
do
  OUT=$(basename $MZXML)
  OUT=${OUT/.mzXML/}"."$DBNAME".MSGFDB.mzid"
  TBL=${OUT/.mzid/.tsv}
  time java -Xmx8000M -jar $MSGFplus_JAR -d $DB -s $MZXML -o $OUT -t 30ppm -tda 0 -ntt 1
  time java -Xmx8000M -cp $MSGFplus_JAR edu.ucsd.msjava.ui.MzIDToTsv -i $OUT -o $TBL -showQValue 1 -showDecoy 1 -unroll 1
done
