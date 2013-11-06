#!/usr/bin/env python
import os
import sys
import math

filename_ms2 = sys.argv[1]
filename_base = filename_ms2.replace('.ms2_info','').replace('.mzML','').replace('.mzXML','')

rt_list = []
pmz_list = []
tot_ion_list = []

charge_tag_list = ['+0','+1','+2','+3','+4','>+4']
charge_tag_color = {'+0':'grey','+1':'yellow','+2':'red','+3':'blue','+4':'green','>+4':'magenta'}

rt2pmz = dict()
rt2tot_ion = dict()
charge_tag_count = dict()
for tmp_charge_tag in charge_tag_list:
    rt2pmz[tmp_charge_tag] = dict()
    rt2tot_ion[tmp_charge_tag] = dict()
    charge_tag_count[tmp_charge_tag] = 0

f_ms2 = open(filename_ms2,'r')
headers = f_ms2.readline().strip().split("\t")
for line in f_ms2:
    tokens = line.strip().split("\t")
    tmp_rt = float(tokens[1])
    tmp_charge = int(tokens[3])
    tmp_pmz = float(tokens[4])
    tmp_tot_ion = float(tokens[5])
    if( tmp_tot_ion != 0 ):
        tmp_tot_ion = math.log10(tmp_tot_ion)

    tmp_charge_tag = '+%d'%tmp_charge
    if( tmp_charge >= 5 ):
        tmp_charge_tag = '>+4'
    rt2pmz[tmp_charge_tag][tmp_rt] = tmp_pmz
    rt2tot_ion[tmp_charge_tag][tmp_rt] = tmp_tot_ion

    tot_ion_list.append(tmp_tot_ion)
    pmz_list.append(tmp_pmz)
    rt_list.append(tmp_rt)
    charge_tag_count[tmp_charge_tag] += 1
f_ms2.close()

#import matplotlib
#matplotlib.use('Agg')

max_pmz = int(max(pmz_list))
min_pmz = int(min(pmz_list))
pmz_step = [x for x in range(0, max_pmz+1, int(max_pmz*1.0/100) )]

min_tot_ion = int(min(tot_ion_list))
max_tot_ion = int(max(tot_ion_list))
tot_ion_step = [x*0.1 for x in range(0, (max_tot_ion+1)*10)]

## Cleanup
for tmp_charge_tag in charge_tag_list:
    if( charge_tag_count[tmp_charge_tag] == 0 ):
        charge_tag_list.remove(tmp_charge_tag)

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

#### Precursor M/Z
fig = plt.figure(figsize=(10,9))

ax1 = fig.add_subplot(3,1,1)
for tmp_charge_tag in charge_tag_list[::-1]:
    tmp_rt_list = sorted(rt2pmz[tmp_charge_tag].keys())
    ax1.plot(tmp_rt_list, [rt2pmz[tmp_charge_tag][x] for x in tmp_rt_list],marker='.',markerfacecolor=charge_tag_color[tmp_charge_tag],markeredgecolor='white',linestyle='None',label=tmp_charge_tag)
ax1.grid()
ax1.set_xlim(min(rt_list)-10, max(rt_list)+10)
ax1.set_ylim(min_pmz, max_pmz+100)
ax1.set_ylabel('Precursor m/z')
ax1.legend(loc='upper center',numpoints=1,ncol=6,prop=fm.FontProperties(size=9))
ax1.set_title(filename_base)

ax2 = fig.add_subplot(3,1,2)
for tmp_charge_tag in charge_tag_list[::-1]:
    if( tmp_charge_tag == '+2' or tmp_charge_tag == '+3' ):
        tmp_rt_list = sorted(rt2pmz[tmp_charge_tag].keys())
        ax2.plot(tmp_rt_list, [rt2pmz[tmp_charge_tag][x] for x in tmp_rt_list],marker='o',markeredgecolor=charge_tag_color[tmp_charge_tag],markerfacecolor='None',linestyle='None',markersize=4,label=tmp_charge_tag)
ax2.grid()
ax2.set_xlim(min(rt_list)-10, max(rt_list)+10)
ax2.set_ylim(min_pmz, max_pmz+100)
ax2.set_ylabel('Precursor m/z')
ax2.legend(loc='upper center',numpoints=1,ncol=6,prop=fm.FontProperties(size=9))

ax3 = fig.add_subplot(3,1,3)
for tmp_charge_tag in charge_tag_list[::-1]:
    if( tmp_charge_tag == '+2' or tmp_charge_tag == '+3' ):
        continue

    tmp_rt_list = sorted(rt2pmz[tmp_charge_tag].keys())
    ax3.plot(tmp_rt_list, [rt2pmz[tmp_charge_tag][x] for x in tmp_rt_list],marker='o',markeredgecolor=charge_tag_color[tmp_charge_tag],markerfacecolor='None',linestyle='None',markersize=4,label=tmp_charge_tag)
ax3.grid()
ax3.set_xlim(min(rt_list)-10, max(rt_list)+10)
ax3.set_ylim(min_pmz, max_pmz+100)
ax3.set_xlabel('Retention time (sec)')
ax3.set_ylabel('Precursor m/z')
ax3.legend(loc='upper center',numpoints=1,ncol=6,prop=fm.FontProperties(size=9))

filename_png = '%s_pmz.png'%filename_ms2
sys.stderr.write('Write %s\n'%filename_png)
plt.savefig(filename_png)

#### TOT ION
fig = plt.figure(figsize=(10,9))
ax1 = fig.add_subplot(3,1,1)
for tmp_charge_tag in charge_tag_list[::-1]:
    tmp_rt_list = sorted(rt2pmz[tmp_charge_tag].keys())
    ax1.plot(tmp_rt_list, [rt2tot_ion[tmp_charge_tag][x] for x in tmp_rt_list],marker='.',markerfacecolor=charge_tag_color[tmp_charge_tag],markeredgecolor='white',linestyle='None',label=tmp_charge_tag)
ax1.grid()
ax1.set_xlim(min(rt_list)-10, max(rt_list)+10)
ax1.set_ylim(min_tot_ion, max_tot_ion+1)
ax1.set_ylabel('Total Ion Intensity, log10')
ax1.legend(loc='upper center',numpoints=1,ncol=6,prop=fm.FontProperties(size=9))
ax1.set_title(filename_base)

ax2 = fig.add_subplot(3,1,2)
for tmp_charge_tag in charge_tag_list[::-1]:
    if( tmp_charge_tag == '+2' or tmp_charge_tag == '+3' ):
        tmp_rt_list = sorted(rt2pmz[tmp_charge_tag].keys())
        ax2.plot(tmp_rt_list, [rt2tot_ion[tmp_charge_tag][x] for x in tmp_rt_list],marker='o',markeredgecolor=charge_tag_color[tmp_charge_tag],markerfacecolor='None',linestyle='None',markersize=4,label=tmp_charge_tag)
ax2.grid()
ax2.set_xlim(min(rt_list)-10, max(rt_list)+10)
ax2.set_ylim(min_tot_ion, max_tot_ion+1)
ax2.set_ylabel('Total Ion Intensity, log10')
ax2.legend(loc='upper center',numpoints=1,ncol=6,prop=fm.FontProperties(size=9))

ax3 = fig.add_subplot(3,1,3)
for tmp_charge_tag in charge_tag_list[::-1]:
    if( tmp_charge_tag == '+2' or tmp_charge_tag == '+3' ):
        continue

    tmp_rt_list = sorted(rt2pmz[tmp_charge_tag].keys())
    ax3.plot(tmp_rt_list, [rt2tot_ion[tmp_charge_tag][x] for x in tmp_rt_list],marker='o',markeredgecolor=charge_tag_color[tmp_charge_tag],markerfacecolor='None',linestyle='None',markersize=4,label=tmp_charge_tag)
ax3.grid()
ax3.set_xlim(min(rt_list)-10, max(rt_list)+10)
ax3.set_ylim(min_tot_ion, max_tot_ion+1)
ax3.set_xlabel('Retention time (sec)')
ax3.set_ylabel('Total Ion Intensity, log10')
ax3.legend(loc='upper center',numpoints=1,ncol=6,prop=fm.FontProperties(size=9))

filename_png = '%s_tot_ion.png'%filename_ms2
sys.stderr.write('Write %s\n'%filename_png)
plt.savefig(filename_png)

#### Dist 
fig = plt.figure(figsize=(11,5))
ax4 = fig.add_subplot(1,3,1)
ax4.set_position([0.05,0.2,0.17,0.6])
ax4.pie([charge_tag_count[x] for x in charge_tag_list],labels=['%s(N=%d)'%(x,charge_tag_count[x]) for x in charge_tag_list], colors=[charge_tag_color[x] for x in charge_tag_list], radius=0.7)

ax5 = fig.add_subplot(1,3,3)
ax5.set_position([0.35,0.1,0.28,0.8])
for tmp_charge_tag in charge_tag_list:
    ax5.hist(rt2pmz[tmp_charge_tag].values(),bins=pmz_step,histtype='step',edgecolor=charge_tag_color[tmp_charge_tag],label=tmp_charge_tag)
ax5.set_xlim(min_pmz-50, max_pmz+50)
ax5.set_ylabel('Frequency')
ax5.set_xlabel('Precursor m/z')
ax5.legend(prop=fm.FontProperties(size=9))
ax5.set_title(filename_base)
ax5.grid()

ax6 = fig.add_subplot(3,3,9)
ax6.set_position([0.70,0.1,0.28,0.8])
for tmp_charge_tag in charge_tag_list:
    ax6.hist(rt2tot_ion[tmp_charge_tag].values(),bins=tot_ion_step,histtype='step',edgecolor=charge_tag_color[tmp_charge_tag],label=tmp_charge_tag)
ax6.set_ylabel('Frequency')
ax6.set_xlabel('Total Ion Intensity, log10')
ax6.legend(prop=fm.FontProperties(size=9))
ax6.grid()
filename_png = '%s_hist.png'%filename_ms2
sys.stderr.write('Write %s\n'%filename_png)
plt.savefig(filename_png)
