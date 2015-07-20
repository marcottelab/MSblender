#!/bin/bash

module load gsl

for f in ./tandemK/*.out;
do
#./comet/RiceL_IEX_01-1a_20150611.uniprot-proteome%3AUP000000763_contam.combined.tandemK.out.uniprot-proteome%3AUP000000763_contam.combined.comet.txt is not accessible.

#f2=${f%.Rice*}.uniprot-proteome%3AUP000000763_contam.combined.comet.txt 
f2=${f%.tandemK.out}.comet.txt 
f3=${f%.tandemK.out}.MSGF+.tsv

f=${f##*mK/}
f2=${f2##*mK/}
f3=${f3##*mK/}

bash run_msblender.sh ./tandemK/$f ./comet/$f2 ./MSGF+/$f3
#echo $f
#echo $f2
#echo $f3
done

