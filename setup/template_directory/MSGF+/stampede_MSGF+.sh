#!/bin/bash
#SBATCH -n 16
#SBATCH -p normal
#SBATCH -t 48:00:00
#SBATCH -o mg+.o%j
#SBATCH -J "mg+"
#SBATCH -A A-cm10			# charge job to myproject 

date

set -x

#module load jdk64

MSGFplus_JAR="$WORK/msblender/MSblender/extern/MSGFPlus.jar"

#DB="../DB/uniprot-proteome%3AUP000000763_contam.combined.fasta"
DB="XXX_DB_COMBINED_FASTA_TEMPLATE_XXX"

DBNAME=$(basename $DB)
DBNAME=${DBNAME/.fasta/}

for MZXML in $(ls ../mzXML/*mzXML)
do
  OUT=$(basename $MZXML)
  OUT=${OUT/.mzXML/}"."$DBNAME".MSGF+.mzid"
  TBL=${OUT/.mzid/.tsv}
  time java -Xmx20000M -jar $MSGFplus_JAR -d $DB -s $MZXML -o $OUT -t 10ppm -tda 0 -ntt 2 -e 1 -inst 3
  time java -Xmx20000M -cp $MSGFplus_JAR edu.ucsd.msjava.ui.MzIDToTsv -i $OUT -o $TBL -showQValue 1 -showDecoy 1 -unroll 0
done

date
