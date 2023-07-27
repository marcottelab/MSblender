#!/usr/bin/env python
import os
import sys

best_hit = dict()
filename_in = sys.argv[1]

f_hit_list = open(filename_in,'r')
filename_out = filename_in+'_best'
f_out = open(filename_out,'w')
for line in f_hit_list:
    if( line.startswith('#') ):
        f_out.write("%s\n"%line.strip())
        continue
    tokens = line.strip().split("\t")
    sp_id = '.'.join(tokens[0].split('.')[:-1])
    charge = tokens[1]

    score = float(tokens[-1])
    if( not best_hit.has_key(sp_id) ):
        best_hit[sp_id] = {'charge':charge, 'line':line.strip(), 'score':score}
    elif( score > best_hit[sp_id]['score'] ):
        best_hit[sp_id] = {'charge':charge, 'line':line.strip(), 'score':score}
f_hit_list.close()

for sp_id in sorted(best_hit.keys()):
    f_out.write("%s\n"%(best_hit[sp_id]['line']))
f_out.close()
