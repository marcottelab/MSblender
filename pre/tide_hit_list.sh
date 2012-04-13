#!/bin/bash
# can usually just use (readlink -f $0), but doesn't work if you 
# call the script with source versus calling directly.
scriptdir=$(dirname $(readlink -f ${BASH_SOURCE[0]}))
MAKE_HIT_LIST=$scriptdir"/tide_hit_list_help.py"
SELECT_BEST=$scriptdir"/select-best-PSM.py"
for OUT in $(ls *pepxml)
do
  python $MAKE_HIT_LIST $OUT
  python $SELECT_BEST $OUT".xcorr_hit_list"
done
