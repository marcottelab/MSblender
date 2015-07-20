#!/bin/bash
f=${1##*mK/}

mkdir ${f%.tan*}-Results

wait


python /work/02609/kdrew/msblender/MSblender/pre/comet_txt-to-xcorr_hit_list.py $2
wait

python /work/02609/kdrew/msblender/MSblender/pre/tandem_out-to-logE_hit_list.py $1
wait

python /work/02609/kdrew/msblender/MSblender/pre/MSGF+_tsv-to-logSpecE_hit_list.py $3
wait


python  /work/02609/kdrew/msblender/MSblender/pre/select-best-PSM.py $1.logE_hit_list
wait

python /work/02609/kdrew/msblender/MSblender/pre/select-best-PSM.py ${2/txt/}xcorr_hit_list
wait

python /work/02609/kdrew/msblender/MSblender/pre/select-best-PSM.py $3.logSpecE_hit_list
wait

#echo X!Tandem        $1.logE_hit_list_best > msblender.conf
#wait
echo comet	     ${2/txt/}xcorr_hit_list_best > msblender.conf
#wait
echo MSGF+	     $3.logSpecE_hit_list_best >> msblender.conf
#echo X!Tandem 	     $1.logE_hit_list_best> msblender.conf

#echo comet	     $2.xcorr_hit_list_best >> msblender.conf
echo X!Tandem 	     $1.logE_hit_list_best >> msblender.conf

wait

python /work/02609/kdrew/msblender/MSblender/pre/make-msblender_in.py ./msblender.conf

wait

/work/02609/kdrew/msblender/MSblender/src/msblender ./msblender.msblender_in
wait


python /work/02609/kdrew/msblender/MSblender/post/filter-msblender.py ./msblender.msblender_in.msblender_out 001 > ./msblender.filter
wait

python /work/02609/kdrew/msblender/MSblender/post/msblender_out-to-pep_count-FDRpsm.py ./msblender.msblender_in.msblender_out 0.01 mFDRpsm
wait


python /work/02609/kdrew/msblender/MSblender/post/pep_count_with_fasta-to-prot_count.py ./*.pep_count_mFDRpsm001 /work/02609/kdrew/msblender/RiceL_IEX_uniprot/DB/uniprot-proteome%3AUP000000763_contam.combined.fasta
wait

mv msblender.* ${f%.tan*}-Results

