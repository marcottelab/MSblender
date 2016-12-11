#!/bin/bash
MAKE_HIT_LIST=$(dirname $0)"/comet_txt-to-xcorr_hit_list.py"
SELECT_BEST=$(dirname $0)"/select-best-PSM.py"

echo $SCRIPT
for OUT in $(ls *comet.txt)
do
  $MAKE_HIT_LIST $OUT
  $SELECT_BEST ${OUT/.txt/}".xcorr_hit_list"
done
