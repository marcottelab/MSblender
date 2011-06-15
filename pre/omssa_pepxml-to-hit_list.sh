#!/bin/bash
MAKE_HIT_LIST=$(dirname $0)"/omssa_pepxml-to-logE_hit_list.py"
SELECT_BEST=$(dirname $0)"/select-best-PSM.py"
echo $SCRIPT
for OUT in $(ls *pepxml)
do
  $MAKE_HIT_LIST $OUT
  $SELECT_BEST $OUT".logE_hit_list"
done
