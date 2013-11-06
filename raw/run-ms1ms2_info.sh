#!/bin/bash
for MZXML in $(ls *mzXML)
do
  $HOME/git/MSblender/raw/mzXML-to-ms1ms2_info.py $MZXML
  $HOME/git/MSblender/raw/plot-ms1_info.py $MZXML".ms1_info"
  $HOME/git/MSblender/raw/plot-ms2_info.py $MZXML".ms2_info"
done
