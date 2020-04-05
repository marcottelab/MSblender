#!/bin/bash
MSGFDB_JAR="$HOME/git/MSblender/extern/MSGFDB.jar"

## Path for the database, with decoy
DB="/work/ups/db/UPS2013_combined.fa"

## Directory containing spectrum data (mzXML, mzML, etc)
SOURCE_DIR="../mzXML.5ul/"

## Extension of your raw file: mzXML, mzML, etc
RAW_TYPE="mzXML"

## Number of threds
THREAD=2

#[-e EnzymeID] (0: No enzyme, 1: Trypsin (Default), 2: Chymotrypsin, 3: Lys-C, 4: Lys-N, 5: Glu-C, 6: Arg-C, 7: Asp-N, 8: alphaLP, 9: Endogenous peptides)
ENZYME=1

#[-m FragmentMethodID] (0: As written in the spectrum or CID if no info (Default), 1: CID, 2: ETD, 3: HCD, 4: Merge spectra from the same precursor)
FRAGMENT_METHOD=1

#[-inst InstrumentID] (0: Low-res LCQ/LTQ (Default), 1: High-res LTQ, 2: TOF)
INST=1

#[-nnet 0/1/2] (Number of allowed non-enzymatic termini, Default: 1)
NNET=0
	
#[-n NumMatchesPerSpec] (Number of matches per spectrum to be reported, Default: 1)
MATCHES_PER_SPEC=5

## Clean up DB first

DBNAME=$(basename $DB)
DBNAME=${DBNAME/.fasta/}
DBNAME=${DBNAME/.fa/}

for RAW in $(ls $SOURCE_DIR/*$RAW_TYPE)
do
  OUT=$(basename $RAW)
  OUT=${OUT/.$RAW_TYPE/}"."$DBNAME".MSGFDB.out"
  time java -Xmx8000M -jar $MSGFDB_JAR -d $DB -s $RAW -t 20ppm -e $ENZYME -nnet $NNET -n $MATCHES_PER_SPEC -o $OUT -m $FRAGMENT_METHOD -inst $INST -thread $THREAD -inst $INST
done
