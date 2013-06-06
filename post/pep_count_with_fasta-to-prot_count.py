#!/usr/bin/env python
import os
import sys

filename_pep_count = sys.argv[1]
filename_fa = sys.argv[2]

pep_count = dict()
pep2prot = dict()
f_pc = open(filename_pep_count,'r')
for line in f_pc:
    if( line.startswith('#') ):
        continue
    tokens = line.strip().split()
    pep_count[ tokens[0] ] = int(tokens[1])
    pep2prot[ tokens[0] ] = []
f_pc.close()

prot_id = ''
prot_list = dict()
f_fa = open(filename_fa,'r')
for line in f_fa:
    if( line.startswith('>') ):
        prot_id = line.strip().lstrip('>')
        prot_list[prot_id] = []
    else:
        prot_list[prot_id].append( line.strip() )
f_fa.close()

prot2pep = dict()
tmp_count = 1
for prot_id in prot_list.keys():
    if( prot_id.startswith('rv_') or prot_id.startswith('xf_') or prot_id.startswith('rev_') ):
        continue
    tmp_seq = ''.join(prot_list[prot_id])
    
    if( tmp_count % 1000 == 0 ):
        sys.stderr.write('Read %d seq: %s\n'%(tmp_count,prot_id))
    tmp_count += 1

    for pep_seq in pep_count.keys():
        if( pep_seq in tmp_seq ):
            pep2prot[pep_seq].append(prot_id)
            if( not prot2pep.has_key(prot_id) ):
                prot2pep[prot_id] = []
            prot2pep[prot_id].append(pep_seq)

filename_prot_count = filename_pep_count.replace('.pep_count','.prot_count')
f_prot_count = open(filename_prot_count,'w')
f_log = open('%s.log'%filename_prot_count,'w')

sys.stderr.write('Write %s\n'%filename_prot_count)
f_prot_count.write("#ProtID\tUnweighted\tWeighted\tUnique\n")
for prot_id in sorted(prot2pep.keys()):
    prot_seq = ''.join(prot_list[prot_id])
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

        if( unweighted > 0 ):
            tmp_start = prot_seq.find(pep_seq)
            while( tmp_start >= 0 ):
                tmp_start_aa = prot_seq[tmp_start-1]
                tmp_end = tmp_start+len(pep_seq)
                tmp_end_aa = '*'
                if( tmp_end < len(prot_seq) ):
                    tmp_end_aa = prot_seq[tmp_end] 
                f_log.write('%s\t%d\t%s.%s.%s\n'%(prot_id,tmp_start,tmp_start_aa,pep_seq,tmp_end_aa))
                tmp_start = prot_seq.find(pep_seq,tmp_end)

    if( unweighted == 0 ):
        continue
    
    f_prot_count.write("%s\t%d\t%.2f\t%d\n"%(prot_id,unweighted,weighted,unique))

sys.stderr.write("#total count:%d\n"%(sum(pep_count.values())))
f_prot_count.write("#total count:%d\n"%(sum(pep_count.values())))
f_log.close()
