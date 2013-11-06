#!/usr/bin/env python
import os
import sys
import math

filename_ms1 = sys.argv[1]
filename_base = filename_ms1.replace('.ms1_info','').replace('.mzML','').replace('.mzXML','')

rt2ms2 = dict()
rt2tot_ion = dict()

f_ms1 = open(filename_ms1,'r')
headers = f_ms1.readline().strip().split("\t")
if( len(headers) != 4 ):
    sys.stderr.write('Format error (not ms1_info file): %s\n'%filename_ms1)
    sys.exit(1)

for line in f_ms1:
    tokens = line.strip().split("\t")
    tmp_ret_time = float(tokens[1])
    rt2ms2[tmp_ret_time] = int(tokens[2])
    rt2tot_ion[tmp_ret_time] = int(tokens[3])
f_ms1.close()

ret_time_list = sorted(rt2ms2.keys())

#import matplotlib
#matplotlib.use('Agg')

import matplotlib.pyplot as plt

fig = plt.figure(figsize=(10,8))

ax1 = fig.add_subplot(2,1,1)
ax1.plot(ret_time_list, [math.log10(rt2tot_ion[x]) for x in ret_time_list], 'k-', label='total ions')
ax1.set_xlabel('Retention time (sec)')
ax1.set_ylabel('Total Ion Intensity, log10')
ax1.set_xlim(0,max(ret_time_list))
ax1.set_title("%s (ms1=%d, ms2=%d)"%(filename_base,len(rt2ms2),sum(rt2ms2.values())))
ax1.grid()

ax2 = fig.add_subplot(2,1,2)
ax2.plot(ret_time_list, [rt2ms2[x] for x in ret_time_list], 'k-', label='ms2 count')
ax2.set_xlim(0,max(ret_time_list))
ax2.set_ylim(0,max(rt2ms2.values())+1)
ax2.set_xlabel('Retention time (sec)')
ax2.set_ylabel('MS2 count')
ax2.grid()

filename_png = '%s.png'%filename_ms1
sys.stderr.write('Write %s\n'%filename_png)
plt.savefig(filename_png)
