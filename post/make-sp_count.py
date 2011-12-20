#!/usr/bin/python
import sys
import os

usage_mesg = 'make-sp_count.py <.msblender_out> <.prot_list> <FDR cutoff>'

if( len(sys.argv) != 4 ):
    print usage_mesg
    sys.exit(1)

filename_msb_out = sys.argv[1]
filename_prot_list = sys.argv[2]
FDR_cutoff = float(sys.argv[3])

sys.stderr.write('Read %s ... '%filename_prot_list)
sp2prot = dict()
f_prot_list = open(filename_prot_list,'r')
for line in f_prot_list:
    tokens = line.strip().split("\t")
    sp2prot[ tokens[0] ] = tokens[1]
f_prot_list.close()
sys.stderr.write('Done\n')

sys.stderr.write('Read %s ... '%filename_msb_out)
sp2mvscore = dict()
f_msb_out = open(filename_msb_out,'r')
headers = f_msb_out.readline()
for line in f_msb_out:
    tokens = line.strip().split("\t")
    sp2mvscore[ tokens[0] ] = float(tokens[-1])
f_msb_out.close()
sys.stderr.write('Done\n')

sp_count = dict()
sp_weight = dict()
prot_list = []
sample_list = []
mvscore_list = []
tmp_idx = 0
for sp_pep_id in sorted(sp2mvscore.keys(),key=sp2mvscore.get,reverse=True):
    mvscore_list.append( sp2mvscore[sp_pep_id] )
    tmp_FDR = 1.0 - float(sum(mvscore_list))/len(mvscore_list)
    tmp_idx += 1

    if( tmp_FDR > FDR_cutoff ):
        break

    if( sp2prot[sp_pep_id].startswith('xf_') ):
        continue

    sp_pep_tokens = sp_pep_id.split('.')
    sample_name = sp_pep_tokens[0]
    sample_list.append(sample_name)
    sp_id = '%s.%s'%(sp_pep_tokens[0],sp_pep_tokens[1])

    if( not sp_weight.has_key(sp_id) ):
        sp_weight[sp_id] = []
    sp_weight[sp_id].append(sp_pep_id)

    if( not sp_count.has_key(sample_name) ):
        sp_count[sample_name] = dict()
    if( not sp_count[sample_name].has_key(sp2prot[sp_pep_id]) ):
        sp_count[sample_name][sp2prot[sp_pep_id]] = []
        prot_list.append(sp2prot[sp_pep_id])
    sp_count[sample_name][ sp2prot[sp_pep_id] ].append( sp_id )

prot_list = sorted(list(set(prot_list)))
sample_list = sorted(list(set(sample_list)))

total_sp_count = 0
print "ProtID\tTotalCount\t%s"%('\t'.join(sample_list))
for tmp_prot in prot_list:
    out_str = []
    for tmp_sample in sample_list:
        if( not sp_count[tmp_sample].has_key(tmp_prot) ):
            out_str.append('0.00')
        else:
            if( not sp_count[tmp_sample].has_key(tmp_prot) ):
                out_str.append('0.00')
            else:
                tmp_weighted_count = 0

                for sp_id in list(set(sp_count[tmp_sample][tmp_prot])):
                    tmp_weighted_count += 1.0/len( list(set(sp_weight[sp_id])) )
                out_str.append('%.2f'%tmp_weighted_count)
    
    tmp_sum = sum([float(x) for x in out_str])
    total_sp_count += tmp_sum
    print "%s\t%.2f\t%s"%(tmp_prot,tmp_sum,'\t'.join(out_str))
print "#Total Spectral counts: %.2f"%total_sp_count
