#!/bin/bash
MSGFplus_JAR="$HOME/git/MSblender/extern/MSGFPlus.jar"

## Path for the database, with decoy
DB="COMBINED.fa"

DBNAME=$(basename $DB)
DBNAME=${DBNAME/.fa/}

## Directory containing spectrum data (mzXML, mzML, etc)
SOURCE_DIR="../mzXML/"

## Extension of your raw file: mzXML, mzML, etc
RAW_TYPE="mzXML"

## Number of threads 
THREAD=8

#[-e EnzymeID] (0: unspecific cleavage, 1: Trypsin (Default), 2: Chymotrypsin, 3: Lys-C, 4: Lys-N, 5: glutamyl endopeptidase, 6: Arg-C, 7: Asp-N, 8: alphaLP, 9: no cleavage)
ENZYME=1

#[-m FragmentMethodID] (0: As written in the spectrum or CID if no info (Default), 1: CID, 2: ETD, 3: HCD)
FRAGMENT_METHOD=0

#[-inst InstrumentID] (0: Low-res LCQ/LTQ (Default), 1: Orbitrap/FTICR/Lumos, 2: TOF, 3: Q-Exactive)
INST=1
	
#[-ntt 0/1/2] (Number of Tolerable Termini, Default: 2)
#E.g. For trypsin, 0: non-tryptic, 1: semi-tryptic, 2: fully-tryptic peptides only.
NTT=2

#[-mod ModificationFileName] (Modification file, Default: standard amino acids with fixed C+57)

for RAW in $(ls $SOURCE_DIR/*$RAW_TYPE)
do
  MZID=$(basename $RAW)
  MZID=${MZID/.$RAW_TYPE/}"."$DBNAME".MSGF+.mzid"
  time java -Xmx8000M -jar $MSGFplus_JAR -inst $INST -d $DB -s $RAW -o $MZID -t 20ppm -tda 0 -ntt $NTT -thread $THREAD
  OUT=${MZID/.mzid/}".tsv"
  java -Xmx8000M -cp $MSGFplus_JAR edu.ucsd.msjava.ui.MzIDToTsv -i $MZID -o $OUT -unroll 0
done
