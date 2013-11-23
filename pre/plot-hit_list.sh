#!/bin/bash
for HIT_LIST in $(ls *hit_list_best)
do
  echo $HIT_LIST
  $HOME/git/MSblender/pre/plot-hit_list.py $HIT_LIST
done
