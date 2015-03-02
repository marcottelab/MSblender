#!/usr/bin/python 
import sys
import os
import random

usage_mesg = 'Usage: fasta-reverse.py <fasta file>'
if( len(sys.argv) != 2 ):
    sys.stderr.write('Error! Invalide argument.\n%s\n'%(usage_mesg))
    sys.exit(1)

filename_fasta = sys.argv[1]
if( not os.access(filename_fasta,os.R_OK) ):
    sys.stderr.write("%s is not accessible.\n%s\n"%(filename_fasta,usage_mesg))
    sys.exit(1)

f_fasta = open(filename_fasta,'r')
header = ''
seq = dict()
for line in f_fasta:
    if(line.startswith('>')):
        header = line.strip().lstrip('>').split()[0]
        seq[header] = ''
    else:
        seq[header] += line.strip().upper()
f_fasta.close()

f_target = open("%s.target"%filename_fasta,'w')
f_reverse = open("%s.reverse"%filename_fasta,'w')
for h in seq.keys():
    f_reverse.write(">rv_%s\n%s\n"%(h,seq[h][::-1]))
    f_target.write(">%s\n%s\n"%(h,seq[h]))
f_reverse.close()
f_target.close()
