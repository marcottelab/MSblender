#!/bin/bash
OMSSA="$HOME/src.MS/omssa/omssa-2.1.9.linux/omssacl"

DB="$SCRATCH/HumanCells/DB.prot/HUMAN_uniprot_201306.with_prot_rev"
DBNAME=$(basename $DB)

for MGF in $(ls ../MGF/*mgf)
do
  OUT=$(basename $MGF)
  OUT=${OUT/.mgf/}"."$DBNAME".omssa.pepxml"

  ## http://proteomicsresource.washington.edu/omssa.php
  ## -e 16 semi-tryptic, 1 trypsin
  ## -mf 3 fixed carbamiodmethyl C
  ## -mv 1 variable oxidation of M
  ## -v 2 miss-cleavage
  ## -nt 8 processors

  #time $OMSSA -e 16 -i 1,4 -mf 3 -mv 1 -tem 1 -tom 1 -te 3.0  -he 1000000.0 -hl 5 -d $DB -fm $MGF -v 2 -nt 2 -op $OUT
  time $OMSSA -e 1 -i 1,4 -mv 1 -tem 1 -tom 1 -te 3.0  -he 1000000.0 -hl 5 -d $DB -fm $MGF -v 2 -nt 8 -op $OUT
done
