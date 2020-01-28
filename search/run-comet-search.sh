#!/bin/bash
COMET_EXE="$HOME/src/comet/comet.2019014.linux.exe"

## Change this variable if you want to use your own params.
PARAM="comet.params"

## Path for the database, with decoy
DB="$HOME/MS/db/XENLA_XenBase20190115_prot.combined.fa"

## Extension of your raw file: mzXML, mzML, etc
RAW_TYPE="mzXML"

DBNAME=$(basename $DB)
DBNAME=${DBNAME/.fasta/}
DBNAME=${DBNAME/.fa/}

for RAW in $(ls ../mzXML/*$RAW_TYPE)
do
  OUT=$(basename $RAW)
  OUT=$PWD"/"${OUT/.$RAW_TYPE/}"."$DBNAME".comet"
  time $COMET_EXE -P$PARAM -N$OUT -D$DB $RAW
done
