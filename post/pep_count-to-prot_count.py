#!/usr/bin/python
import os
import sys

filename_pep_count = sys.argv[1]
filename_prot_list = sys.argv[2]

pep_count = dict()
f_pc = open(filename_pep_count,'r')
for line in f_pc:
    if( line.startswith('#') ):
        continue
    tokens = line.strip().split()
    pep_count[ tokens[0] ] = int(tokens[1])
f_pc.close()

pep2prot = dict()
prot2pep = dict()
f_pl = open(filename_prot_list,'r')
for line in f_pl:
    if( line.startswith('#') ):
        continue
    tokens = line.strip().split("\t")
    pep_seq = tokens[0].split('.')[-1]
    if( pep_seq == '' ):
        continue

    for prot_id in tokens[1].split(','):
        if( not pep2prot.has_key(pep_seq) ):
            pep2prot[pep_seq] = []
        pep2prot[pep_seq].append(prot_id)
        if( not prot2pep.has_key(prot_id) ):
            prot2pep[prot_id] = []
        prot2pep[prot_id].append(pep_seq)
f_pl.close()

print "#ProtID\tUnweighted\tWeighted\tUnique"
for prot_id in sorted(prot2pep.keys()):
    if( prot_id.startswith('rv_') ):
        continue

    unweighted = 0
    weighted = 0
    unique = 0
    for pep_seq in list(set(prot2pep[prot_id])):
        if( not pep_count.has_key(pep_seq) ):
            continue
        unweighted += pep_count[pep_seq]
        tmp_pep2prot = len(list(set(pep2prot[pep_seq])))
        weighted += 1.0*pep_count[pep_seq]/tmp_pep2prot
        if( tmp_pep2prot == 1 ):
            unique += pep_count[pep_seq]

    if( unweighted == 0 ):
        continue
    print "%s\t%d\t%.2f\t%d"%(prot_id,unweighted,weighted,unique)

print "#total count:%d"%(sum(pep_count.values()))
