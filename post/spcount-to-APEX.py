#!/usr/bin/env python
import os
import sys

## Assuming that protein probability = 1.0
## APEX score = n_i / ( Oi_i * sum(n_k/Oi_k) ) * C
filename_spcount = sys.argv[1]
filename_Oi = sys.argv[2]
C = int(sys.argv[3])

Oi = dict()
f_Oi = open(filename_Oi,'r')
for line in f_Oi:
    if( line.startswith('#') ):
        continue
    tokens = line.strip().split("\t")
    Oi[tokens[0]] = float(tokens[2])
f_Oi.close()

spcount = dict()
apex_score = dict()
f_sp = open(filename_spcount,'r')
for line in f_sp:
    if( line.startswith('#') ):
        continue
    tokens = line.strip().split("\t")
    gene_id = tokens[0]
    spcount[gene_id] = float(tokens[1])
    tmp_apex = float(tokens[1]) / Oi[gene_id] 
    apex_score[gene_id] = tmp_apex
f_sp.close()

#C=10000
apex_factor = sum(apex_score.values())
for gene_id in sorted(apex_score.keys(),key=apex_score.get):
    print "%s\t%.1f\t%.3f"%(gene_id,spcount[gene_id],apex_score[gene_id]/apex_factor*C)

print "#Sum of APEX score(APEX factor): ",apex_factor
print "#C =",C
