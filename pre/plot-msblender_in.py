#!/usr/bin/python
import os
import sys

filename_in = sys.argv[1]

target_score = dict()
decoy_score = dict()

f_in = open(filename_in,'r')
headers = f_in.readline().strip().split("\t")
if( len(headers) <= 3 ):
    sys.stderr.write("No multiple search engine.\n")
    f_in.close()
    sys.exit(1)

for tmp_engine in headers[2:]:
    target_score[tmp_engine] = []
    decoy_score[tmp_engine] = []

print headers
for line in f_in:
    tokens = line.strip().split("\t")
    for i in range(2,len(headers)):
        tmp_sp_count = 0
        if( tokens[i] != 'NA' ):
            tmp_sp_count = float(tokens[i])
        if( tokens[1] == '1' ):
            decoy_score[ headers[i] ].append( tmp_sp_count )
        elif( tokens[1] == '0' ):
            target_score[ headers[i] ].append( tmp_sp_count )
f_in.close()

import matplotlib.pyplot as plt

engine_list = sorted(headers[2:])
num_engine = len(engine_list)

fig = plt.figure(figsize=(12,12))
ax = dict()
for i in range(0,num_engine):
    engine_i = engine_list[i]
    for j in range(i+1,num_engine):
        tmp_idx = i*num_engine+j+1
        engine_j = engine_list[j]
        ax[tmp_idx] = fig.add_subplot(num_engine,num_engine,tmp_idx)
        ax[tmp_idx].plot(target_score[engine_i],target_score[engine_j],'kx')
        ax[tmp_idx].set_xlabel(engine_i)
        ax[tmp_idx].set_ylabel(engine_j)

plt.savefig('%s.png'%filename_in)
