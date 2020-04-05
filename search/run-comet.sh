#!/bin/bash
COMET="$HOME/git/MSblender/extern/comet.linux.exe"

## Change this variable if you want to use your own params.
PARAM="$HOME/git/MSblender/search/comet.params"

## Path for the database, with decoy
## Make a symbolic link of your database as "COMBINED.fa"
DB="COMBINED.fa"

## Extension of your raw file: mzXML, mzML, etc
RAW_TYPE="mzXML"

DBNAME=$(basename $DB)
DBNAME=${DBNAME/.fasta/}
DBNAME=${DBNAME/.fa/}

for RAW in $(ls ../mzXML/*$RAW_TYPE)
do
  OUT=$(basename $RAW)
  OUT=$PWD"/"${OUT/.$RAW_TYPE/}"."$DBNAME".comet"
  time $COMET -P$PARAM -N$OUT -D$DB $RAW
done
