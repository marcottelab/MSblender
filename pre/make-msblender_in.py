#!/usr/bin/python
import os 
import sys
import math

usage_mesg = 'Usage: make-msblender_in.py <msblender_in.conf file>'
decoy_tag_list = ['xf_','XXX.','rev_','rv_']

sp2hit = dict()
search_median = dict()
search_stdev = dict()

search_engine_list = []
filename_conf = sys.argv[1]
f_conf = open(filename_conf,'r')
for line in f_conf:
    if( line.startswith('#') ):
        continue
    tokens = line.strip().split()
    search_engine_name = tokens[0]
    search_engine_list.append( search_engine_name )

    score_list = []
    filename_hit_list = tokens[1]
    f_hit_list = open(filename_hit_list,'r')
    for line in f_hit_list:
        if( line.startswith('#') ):
            continue
        tokens = line.strip().split("\t")
        sp_id =  tokens[0]
        charge = tokens[1]
        pep_seq = tokens[4]
        prot_id = tokens[5]

        sp_pep_id_list = []
        sp_id_tokens = sp_id.split('.')
        if( sp_id_tokens[-3] == sp_id_tokens[-2] ):
            sp_pep_id_list.append( '%s.%05d.%s.%s'%('.'.join(sp_id_tokens[:-3]),int(sp_id_tokens[-2]),sp_id_tokens[-1],pep_seq) )
        else:
            #for tmp_id in range(int(sp_id_tokens[-3]),int(sp_id_tokens[-2])+1):
            for tmp_id in [int(sp_id_tokens[-3]),int(sp_id_tokens[-2])]:
                sp_pep_id_list.append( '%s.%05d.%s.%s'%('.'.join(sp_id_tokens[:-3]),tmp_id,sp_id_tokens[-1],pep_seq) )

        for sp_pep_id in sp_pep_id_list:
            if( not sp2hit.has_key( sp_pep_id ) ):
                sp2hit[sp_pep_id] = dict()
            sp2hit[sp_pep_id][search_engine_name] = {'prot_id':prot_id, 'score': float(tokens[-1])}
            score_list.append(float(tokens[-1]))
    f_hit_list.close()

    score_list = sorted(score_list)
    idx_median = int( len(score_list)*0.5 )
    score_median = score_list[idx_median]
    score_mean = float(sum(score_list))/len(score_list)
    #var_list = sorted([abs(x - score_median) for x in score_list])
    #score_mad = sorted([abs(x - score_median) for x in score_list])[idx_median]
    var_list = sorted([(x - score_mean)**2 for x in score_list])
    score_stdev = math.sqrt(float(sum(var_list))/len(score_list))
    if( len(score_list) % 2 == 0 ):
        score_median = (score_list[idx_median-1] + score_list[idx_median])*0.5
        #score_mad_list = sorted([abs(x - score_median) for x in score_list])
        #score_mad = (score_mad_list[idx_median-1] + score_mad_list[idx_median])*0.5
    search_median[search_engine_name] = score_median
    #search_mad[search_engine_name] = score_mad * 1.4826
    search_stdev[search_engine_name] = score_stdev
    sys.stderr.write("%s,%d,%f,%f\n"%(search_engine_name,idx_median,score_median,score_stdev))
f_conf.close()

search_engine_list = sorted(search_engine_list)

filename_out = filename_conf.replace('.conf','')
filename_prot_list = filename_out +'.prot_list'
filename_out += '.msblender_in'

freq = dict()
f_out = open(filename_out,'w')
f_prot_list = open(filename_prot_list,'w')
f_out.write("sp_pep_id\tdecoy\t%s\n"%("\t".join(["%s_score"%x for x in search_engine_list])))
for sp_pep_id in sorted(sp2hit.keys()):
    output_list = []
    is_decoy = 0
    prot_list = []
    for tmp_search_engine_name in search_engine_list:
        if( sp2hit[sp_pep_id].has_key( tmp_search_engine_name ) ):
            tmp_score = sp2hit[sp_pep_id][tmp_search_engine_name]['score']
            tmp_score = (tmp_score - search_median[tmp_search_engine_name])/search_stdev[tmp_search_engine_name]
            output_list.append( "%f"%tmp_score )
            prot_list.append(sp2hit[sp_pep_id][tmp_search_engine_name]['prot_id'])
            for tmp_decoy_tag in decoy_tag_list:
                if( sp2hit[sp_pep_id][tmp_search_engine_name]['prot_id'].startswith(tmp_decoy_tag) ):
                    is_decoy = 1
        else:
            output_list.append( 'NA' )
    prot_list = list(set(prot_list))
    f_prot_list.write("%s\t%s\n"%(sp_pep_id,','.join(prot_list)))
    f_out.write("%s\t%d\t%s\n"%(sp_pep_id, is_decoy, '\t'.join(output_list) ))
    count_nonNA = len(output_list) - output_list.count('NA')
    if( not freq.has_key(count_nonNA) ):
        freq[count_nonNA] = []
    freq[count_nonNA].append(sp_pep_id)
f_out.close()
f_prot_list.close()

for count_nonNA in sorted(freq.keys()):
    sys.stderr.write("%d - %d\n"%(count_nonNA, len(freq[count_nonNA])))

max_nonNA = max(freq.keys())
f_max = open('%s.overlap_%d_psm.txt'%(filename_conf.replace('.conf',''),max_nonNA),'w')
f_max.write('%s\n'%('\n'.join(sorted(freq[max_nonNA]))))
f_max.close()
