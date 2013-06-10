#!/bin/bash
PEP="$SCRATCH/HumanCells/DB.prot/HUMAN_ens69_prot_combined.fa.pepix"
PROT="$SCRATCH/HumanCells/DB.prot/HUMAN_ens69_prot_combined.fa.protix"

TIDE="$HOME/src.MS/tide/1.0_x86_64/tide-search"
TIDEOUT="$HOME/src.MS/tide/1.0_x86_64/tide-results"

DBNAME=$(basename $PEP)
DBNAME=${DBNAME/.combined.fa.pepix/}

for SR in $(ls ../spectrumrecords/*spectrumrecords)
do
  echo $SR
  OUT=$(basename $SR)
  OUT=${OUT/.spectrumrecords/}"."$DBNAME".tide"
  PROTOBUF=$OUT".protobuf"
  time $TIDE --peptides=$PEP --proteins=$PROT --spectra=$SR --results="protobuf" --results_file=$PROTOBUF
  time $TIDEOUT --proteins=$PROT --results_file=$PROTOBUF --spectra=$SR --out_format="pep.xml" --out_filename=$OUT
done
