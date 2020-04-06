#!/bin/bash
MAKE_HIT_LIST=$(dirname $0)"/MSGFDB_out-to-logSpecProb_hit_list.py"
SELECT_BEST=$(dirname $0)"/select-best-PSM.py"
echo $SCRIPT
for OUT in $(ls *out)
do
  $MAKE_HIT_LIST $OUT
  $SELECT_BEST $OUT".logSpecProb_hit_list"
done
