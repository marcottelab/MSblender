#!/bin/bash
COMET="$HOME/git/MSblender/extern/comet.linux.exe"
## Change this variable if you want to use your own params.
PARAM="$HOME/git/MSblender/search/comet.params"

## Path for the database, with decoy
DB="/work/ups/db/UPS2013_combined.fa"

## Extension of your raw file: mzXML, mzML, etc
RAW_TYPE="mzXML"

DBNAME=$(basename $DB)
DBNAME=${DBNAME/.fasta/}
DBNAME=${DBNAME/.fa/}

for RAW in $(ls ../mzXML.5ul/*$RAW_TYPE)
do
  OUT=$(basename $RAW)
  OUT=$PWD"/"${OUT/.$RAW_TYPE/}"."$DBNAME".comet"
  time $COMET -P$PARAM -N$OUT -D$DB $RAW
done
