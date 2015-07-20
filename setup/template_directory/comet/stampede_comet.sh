#!/bin/bash
#SBATCH -n 16
#SBATCH -p normal
#SBATCH -t 48:00:00
#SBATCH -o cmt.o%j
#SBATCH -A A-cm10			# charge job to myproject 

date
COMET="$WORK/msblender/MSblender/extern/comet.linux.exe"

DB="XXX_DB_COMBINED_FASTA_TEMPLATE_XXX"
DBNAME=$(basename $DB)
DBNAME=${DBNAME/.fasta/}

PARAM="./comet.params.new"

#SBATCH -J "cmt"
for MZXML in $(ls ../mzXML/*mzXML)
do
  OUT=$(basename $MZXML)
  OUT=${OUT/.mzXML/}"."$DBNAME".comet"
  time $COMET -P$PARAM -D$DB -N$OUT $MZXML
done

date
