#!/bin/bash
MAKE_HIT_LIST=$(dirname $0)"/MSGF+_tsv-to-logSpecE_hit_list.py"
SELECT_BEST=$(dirname $0)"/select-best-PSM.py"
echo $SCRIPT
for OUT in $(ls *.tsv)
do
  $MAKE_HIT_LIST $OUT
  $SELECT_BEST $OUT".logSpecE_hit_list"
done
