#!/usr/bin/python
import os
import sys

filename_mb_out = sys.argv[1]
FDR_cutoff = 0.005 

filename_base = filename_mb_out.replace('.msblender_in','').replace('.msblender_out','')

psm_mvScore = dict()
psm_TD = dict()

f_mb_out = open(filename_mb_out,'r')
f_mb_out.readline()
for line in f_mb_out:
    tokens = line.strip().split("\t")
    tmp_mvScore = float(tokens[-1])
    tmp_psm = tokens[0]
    psm_mvScore[tmp_psm] = float(tokens[-1])
    psm_TD[tmp_psm] = tokens[1]
f_mb_out.close()

count_T = 0
count_D = 0

D_pep_count = dict()
pep_count = dict()
sample_list = []
f_log = open('%s.pep_count_FDR0005.log'%filename_base,'w')
f_log.write('PSM_id\tFDR\tmvScore\n')
for tmp_psm in sorted(psm_mvScore.keys(),key=psm_mvScore.get,reverse=True):
    if( psm_TD[tmp_psm] == 'D' ):
        count_D += 1
    elif( psm_TD[tmp_psm] == 'F' ):
        count_T += 1
    else:
        print 'No T/D info:',tmp_psm
        sys.exit(1)
    
    tmp_FDR = 0.0
    if( psm_mvScore[tmp_psm] < 1.0 ):
        tmp_FDR = float(count_D)/(count_T+count_D)
    
    if( tmp_FDR < FDR_cutoff ):
        if( psm_TD[tmp_psm] == 'F' ):
            f_log.write('%s\t%.3f\t%.2f\n'%(tmp_psm,tmp_FDR,psm_mvScore[tmp_psm]))
            
            sample_name = tmp_psm.split('.')[0]
            sample_list.append(sample_name)
            tmp_pep = tmp_psm.split('.')[-1]
            if( not pep_count.has_key(tmp_pep) ):
                pep_count[tmp_pep] = dict()
            if( pep_count[tmp_pep].has_key(sample_name) ):
                pep_count[tmp_pep][sample_name] = 0
            pep_count[tmp_pep][sample_name] += 1
        else:
            if( not D_pep_count.has_key(tmp_pep) ):
                D_pep_count[tmp_pep] = 0
            D_pep_count[tmp_pep] += 1
f_log.close()

sample_list = sorted(list(set(sample_list)))

sys.stderr.write('Peptide FDR: %.3f\n'%( float(len(D_pep_count))/(len(pep_count)+len(D_pep_count)) ))
f_count = open('%s.pep_count_FDR0005'%filename_base,'w')
f_count.write('#PepSeq\tTotalCount\t%s\n'%('\t'.join(sample_list)))
for tmp_pep in sorted(pep_count.keys(),key=pep_count.get):
    out_list = []
    total_count = 0
    for tmp_sample in sample_list:
        if( pep_count[tmp_pep].has_key(tmp_sample) ):
            out_list.append( "%d"%pep_count[tmp_pep][tmp_sample] )
            total_count += pep_count[tmp_pep][tmp_sample]
        else:
            out_list.append('0')

    f_count.write('%s\t%d\t%s\n'%(tmp_pep,total_count,'\t'.join(out_list)))
f_count.close()
