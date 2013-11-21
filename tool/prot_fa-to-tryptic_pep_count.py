#!/usr/bin/env python
import os
import sys
import re

filename_fa = sys.argv[1]

seq_h = ''
seq_list = dict()
f_fa = open(filename_fa,'r')
for line in f_fa:
    if( line.startswith('>') ):
        seq_h = line.strip().lstrip('>')
        seq_list[seq_h] = []
    else:
        seq_list[seq_h].append(line.strip())
f_fa.close()

re_tryptic = re.compile(r'[KR]')
for tmp_h in sorted(seq_list.keys()):
    tmp_seq = ''.join(seq_list[tmp_h])
    tmp_pep_count = len([x for x in re_tryptic.split(tmp_seq) if len(x) > 6 ])
    print "%s\t%s"%(tmp_h,tmp_pep_count)
