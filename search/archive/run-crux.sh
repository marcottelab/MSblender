#!/bin/bash
CRUX="$HOME/src.MS/crux/1.40/bin/crux"

PROT="$SCRATCH/HumanCells/DB.prot/HUMAN_ens69_prot_combined"
DBNAME=$(basename $PROT)

for MZML in $(ls ../mzML/*.mzML)
do
  OUT=$(basename $MZML)
  OUT=${OUT/.mzML/}
  time $CRUX search-for-matches --overwrite T --decoys none --parameter-file param.crux --output-dir . --fileroot $OUT.$DBNAME $MZML $PROT
done
