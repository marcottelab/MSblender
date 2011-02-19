#!/usr/bin/python
import os
import sys

psm_line = dict()
psm_type = dict()
psm_mvscore = dict()
filename_msb_out = sys.argv[1]

cutoff = sys.argv[2]
if( len(cutoff) == 4 ):
    cutoff = float(sys.argv[2])*0.001
elif( len(cutoff) == 3 ):
    cutoff = float(sys.argv[2])*0.01
else:
    print "Wrong format for cutoff. Use 0001 (for 0.1%) or 001 (for 1%) instead."
    sys.exit(1)

f = open(filename_msb_out,'r')
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
sum_error = 0
count_T = 0
count_D = 0
for psm_id in sorted(psm_mvscore.keys(),key=psm_mvscore.get,reverse=True):
    tmp_score = psm_mvscore[psm_id]
    if( psm_type[psm_id] == 'D' ):
        count_D += 1
        print "%s\t%.4f"%(psm_line[psm_id],mean_error)
        continue
    
    count_T += 1
    sum_error += (1.0 - psm_mvscore[psm_id])
    mean_error = sum_error/count_T
    if( psm_mvscore[psm_id] == 1.0 ):
        count_perfect += 1
    
    print "%s\t%.4f"%(psm_line[psm_id],mean_error)

    if( mean_error > cutoff ):
        print "#target=%d,decoy=%d,total=%d, N(mvscore=1.0)=%d"%(count_T, count_D, count_T+count_D, count_perfect)
        break
