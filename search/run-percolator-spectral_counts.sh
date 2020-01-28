#!/bin/bash
CRUX_EXE="$HOME/src/crux/crux-3.2.Linux.x86_64/bin/crux"

DB="../../db/XENLA_XenBase20190115_prot.fa"
JHS20191227_Epidermis_CON_2_2.XENLA_XenBase20190115_prot.tide-search.percolator.target.psms.txt

for PSM in $(ls *.percolator.target.psms.txt)
do
  OUT=${PSM/.percolator.target.psms.txt/}
  $CRUX_EXE spectral-counts --threshold 0.1 --protein-database $DB --fileroot $OUT --output-dir . $PSM
done
