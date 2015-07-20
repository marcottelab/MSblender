#!/bin/bash
#SBATCH -n 16
#SBATCH -p development
#SBATCH -t 02:00:00
#SBATCH -o msb.o%j
#SBATCH -A A-cm10			# charge job to myproject 
#SBATCH -J "msb"

date

module load gsl

bash ./loop_run.sh

wait

date
