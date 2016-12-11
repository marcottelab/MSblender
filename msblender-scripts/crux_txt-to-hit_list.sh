#!/bin/bash
MAKE_HIT_LIST=$(dirname $0)"/crux_txt-to-xcorr_hit_list.py"
SELECT_BEST=$(dirname $0)"/select-best-PSM.py"
echo $SCRIPT
for OUT in $(ls *target.txt)
do
  $MAKE_HIT_LIST $OUT
  OUT_LIST=${OUT/.target.txt/}".xcorr_hit_list"
  $SELECT_BEST $OUT_LIST
done
