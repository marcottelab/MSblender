#!/usr/bin/python
import os
import sys

psm_line = dict()
psm_type = dict()
psm_mvscore = dict()
f = open(sys.argv[1],'r')
f.readline()
for line in f:
    tokens = line.strip().split("\t")
    psm_id = tokens[0]
    is_decoy = tokens[1]
    mvscore = float(tokens[-1])
    psm_type[psm_id] = is_decoy
    psm_mvscore[psm_id] = mvscore
    psm_line[psm_id] = line.strip()
f.close()

count_perfect = 0
count_T = 0
count_D = 0
for psm_id in sorted(psm_mvscore.keys(),key=psm_mvscore.get,reverse=True):
    tmp_score = psm_mvscore[psm_id]
    if( psm_type[psm_id] == 'F' ):
        count_T += 1
    else:
        count_D += 1
    tmp_error = float(count_D)/(count_T+count_D)
    if( tmp_score == 1.0 ):
        print "%s\t%.4f"%(psm_line[psm_id],tmp_error)
        count_perfect += 1
    else:
        print "%s\t%.4f"%(psm_line[psm_id],tmp_error)

    if( tmp_score < 1.0 and tmp_error >= 0.01 ):
        print "#target=%d,decoy=%d,total=%d,fdr=%.3f"%(count_T, count_D, count_T+count_D, tmp_error)
        print "#N(mvscore=1.0):",count_perfect
        break
