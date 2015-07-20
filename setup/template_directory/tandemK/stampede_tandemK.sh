#!/bin/bash
#SBATCH -n 16
#SBATCH -p normal 
#SBATCH -t 48:00:00
# #SBATCH -t 02:00:00
# #SBATCH -p development

#SBATCH -o tK.o%j
#SBATCH -J "tK"
#SBATCH -A A-cm10			# charge job to myproject 


date

set -x

bash ./run-tandemK_parallel.sh

date
