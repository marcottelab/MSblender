#!/bin/bash
#$ -V                   # Inherit the submission environment
#$ -cwd                 # Start job in submission directory
#$ -j y                 # Combine stderr and stdout
#$ -o $JOB_NAME.o$JOB_ID
#$ -pe 1way 8		        # Requests 16 tasks/node, 32 cores total
#$ -q long              # Queue name "normal"
#$ -l h_rt=24:00:00     # Run time (hh:mm:ss)
#$ -M $EMAIL
#$ -m be                # Email at Begin and End of job
#$ -P data

set -x                  # Echo commands, use "set echo" with csh
CRUX="$HOME/src.MS/crux/1.40/bin/crux"

PROT="$SCRATCH/HumanCells/DB.prot/HUMAN_ens69_prot_combined"
DBNAME=$(basename $PROT)

## Required for GLIBC
module load gcc 

#$ -N crux.Tc
for MZML in $(ls ../mzML/*.mzML)
do
  OUT=$(basename $MZML)
  OUT=${OUT/.mzML/}
  time $CRUX search-for-matches --overwrite T --decoys none --parameter-file param.crux --output-dir . --fileroot $OUT.$DBNAME $MZML $PROT
done
