#!/usr/bin/python
import os
import sys

filename_hit_list = sys.argv[1]

target_list = []
decoy_list = []


f_hit_list = open(filename_hit_list,'r')
header_pepxml = f_hit_list.readline()
headers = f_hit_list.readline().strip().split("\t")
score_label = headers[-1]
for line in f_hit_list:
    if( line.startswith('#') ):
        continue
    tokens = line.strip().split("\t")
    prot_id = tokens[5]
    score = float(tokens[-1])
    if( prot_id.startswith('xf_') ):
        decoy_list.append( score )
    else:
        target_list.append( score )
f_hit_list.close()

max = max(decoy_list+target_list)
min = min(decoy_list+target_list)
#print max,min

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

fig = plt.figure(figsize=(12,6))
fig.text(.5,.93,filename_hit_list,ha='center')

ax1 = fig.add_subplot(1,2,1)
(target_n, target_bins, target_patches) = ax1.hist(target_list, bins=100, histtype='step', align='mid', edgecolor='blue', label='Target')
(decoy_n, decoy_bins, decoy_patches) = ax1.hist(decoy_list, bins=target_bins, histtype='step', align='mid', edgecolor='red', label='Decoy')

cum_target_count = 0
cum_decoy_count = 0
for i in range(0,len(target_bins)):
    rev_i = len(target_bins) - i - 2
    if( rev_i == 0 ):
        break
    cum_target_count += target_n[rev_i]
    cum_decoy_count += decoy_n[rev_i]
    fdr = float(cum_decoy_count) / (cum_target_count+cum_decoy_count)
    if( fdr > 0.01 ):
        #print rev_i, cum_target_count, cum_decoy_count
        ax1.axvline(x=target_bins[rev_i], linestyle='--', color='grey', linewidth=2, label="1%% FDR(score=%.2f;N=%d)"%(target_bins[rev_i],cum_target_count))
        break
ax1.grid()
ax1.set_ylabel("Raw frequency")
ax1.set_xlabel(score_label)
ax1.legend( prop=fm.FontProperties(size=12) )

ax2 = fig.add_subplot(1,2,2)
(target_n, target_bins, target_patches) = ax2.hist(target_list, bins=100, histtype='step', align='mid', edgecolor='blue', normed=True, label='Target')
(decoy_n, decoy_bins, decoy_patches) = ax2.hist(decoy_list, bins=target_bins, histtype='step', align='mid', edgecolor='red', normed=True, label='Decoy')
ax2.grid()
ax2.set_ylabel("Normalized frequency")
ax2.set_xlabel(score_label)
ax2.legend( prop=fm.FontProperties(size=12) )

#plt.show()
sys.stderr.write("Write %s.png ... "%filename_hit_list)
plt.savefig("%s.png"%filename_hit_list)
sys.stderr.write("Done\n")
