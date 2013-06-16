#!/bin/bash
#$ -V                   # Inherit the submission environment
#$ -cwd                 # Start job in submission directory
#$ -j y                 # Combine stderr and stdout
#$ -o $JOB_NAME.o$JOB_ID
#$ -pe 1way 8		# Requests 16 tasks/node, 32 cores total
#$ -q long # Queue name "normal"
#$ -l h_rt=24:00:00     # Run time (hh:mm:ss)
#$ -M $EMAIL
#$ -m be                # Email at Begin and End of job
#$ -P data

set -x                  # Echo commands, use "set echo" with csh

#$ -N omssa.full

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
