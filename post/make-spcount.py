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

str_FDR = "0"+("%.3f"%FDR_cutoff).split('.')[1]
filename_base = filename_msb_out.replace('.msblender_in','').replace('.msblender_out','')

filename_spcount = "%s.spcount_FDR%s"%(filename_base,str_FDR)
filename_pep = "%s.pep_list_FDR%s"%(filename_base,str_FDR)

sp2prot = dict()
psm2prot = dict()
prot2pep = dict()
sys.stderr.write('Read %s ... '%filename_prot_list)
f_prot_list = open(filename_prot_list,'r')
for line in f_prot_list:
    tokens = line.strip().split("\t")
    if( len(tokens) != 2 ):
        print "Error in prot_list:",tokens
        continue
        #sys.exit(1)
    psm_id = tokens[0]
    psm_tokens = psm_id.split('.')[:-1]
    sp_id = '%s.%s'%(psm_tokens[0],psm_tokens[1])
    pep_seq = psm_tokens[-1]

    if( not psm2prot.has_key(psm_id) ):
        psm2prot[psm_id] = []
    if( not sp2prot.has_key(sp_id) ):
        sp2prot[sp_id] = []
    for tmp_prot in tokens[1].split(','):
        psm2prot[psm_id].append(tmp_prot)
        sp2prot[sp_id].append(tmp_prot)
        if( not prot2pep.has_key(tmp_prot) ):
            prot2pep[tmp_prot] = []
        prot2pep[tmp_prot].append(pep_seq)
f_prot_list.close()
sys.stderr.write('Done\n')

sys.stderr.write('Read %s ... '%filename_msb_out)
is_decoy = dict()
sp2mvscore = dict()
f_msb_out = open(filename_msb_out,'r')
headers = f_msb_out.readline()
for line in f_msb_out:
    tokens = line.strip().split("\t")
    sp2mvscore[ tokens[0] ] = float(tokens[-1])
    is_decoy[tokens[0]] = tokens[1]
f_msb_out.close()
sys.stderr.write('Done\n')

sp_weight = dict()
sp_count = dict()
prot_list = []
sample_list = []
mvscore_list = []
tmp_idx = 0
for psm_id in sorted(sp2mvscore.keys(),key=sp2mvscore.get,reverse=True):
    mvscore_list.append( sp2mvscore[psm_id] )
    tmp_FDR = 1.0 - float(sum(mvscore_list))/len(mvscore_list)
    tmp_idx += 1

    if( tmp_FDR > FDR_cutoff ):
        break
    
    if( is_decoy[psm_id] == 'D' ):
        continue

    psm_tokens = psm_id.split('.')
    sample_name = psm_tokens[0]
    sample_list.append(sample_name)
    sp_id = '%s.%s'%(psm_tokens[0],psm_tokens[1])

    if( not sp_weight.has_key(sp_id) ):
        sp_weight[sp_id] = []
    sp_weight[sp_id].append(psm_id)

    if( not sp_count.has_key(sample_name) ):
        sp_count[sample_name] = dict()

    for tmp_prot in psm2prot[psm_id]:
        if( not sp_count[sample_name].has_key(tmp_prot) ):
            sp_count[sample_name][tmp_prot] = []
        prot_list.append(tmp_prot)
        sp_count[sample_name][tmp_prot].append( sp_id )

prot_list = sorted(list(set(prot_list)))
sample_list = sorted(list(set(sample_list)))

total_sp_count = 0
f_spcount = open(filename_spcount,'w')
f_pep = open(filename_pep,'w')
f_spcount.write("#ProtID\tTotalCount\t%s\n"%('\t'.join(sample_list)))
for tmp_prot in prot_list:
    if( tmp_prot.startswith('xf_') ):
        continue
    out_str = []
    for tmp_sample in sample_list:
        tmp_pep_map = dict()
        if( not sp_count[tmp_sample].has_key(tmp_prot) ):
            out_str.append('0.00')
        else:
            if( not sp_count[tmp_sample].has_key(tmp_prot) ):
                out_str.append('0.00')
            else:
                tmp_weighted_count = 0

                for sp_id in list(set(sp_count[tmp_sample][tmp_prot])):
                    tmp_weighted_spcount = 1.0/len( list(set(sp_weight[sp_id])) )
                    tmp_weighted_count += tmp_weighted_spcount
                    for tmp_psm_id in list(set(sp_weight[sp_id])):
                        tmp_pep = tmp_psm_id.split('.')[-1]
                        if( not tmp_pep_map.has_key(tmp_pep) ):
                            tmp_pep_map[tmp_pep] = 0
                        tmp_pep_map[tmp_pep] += tmp_weighted_spcount
                out_str.append('%.2f'%tmp_weighted_count)
        for tmp_pep in tmp_pep_map.keys():
            f_pep.write('%s\t%s\t%s\t%.2f\n'%(tmp_prot,tmp_sample,tmp_pep,tmp_pep_map[tmp_pep]))
    tmp_sum = sum([float(x) for x in out_str])
    total_sp_count += tmp_sum
    f_spcount.write("%s\t%.2f\t%s\n"%(tmp_prot,tmp_sum,'\t'.join(out_str)))
f_spcount.write("#Total Spectral counts: %.2f\n"%total_sp_count)
f_spcount.close()
f_pep.close()
