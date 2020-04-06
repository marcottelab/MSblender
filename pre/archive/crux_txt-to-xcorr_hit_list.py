#!/usr/bin/env python
import math
import os
import sys
import re

usage_mesg = 'Usage: crux_txt-to-xcorr_hit_list.py <crux target.txt file>'

if( len(sys.argv) != 2 ):
    print usage_mesg
    sys.exit(1)

filename_in = sys.argv[1]
if( not os.access(filename_in,os.R_OK) ):
    print "%s is not accessible."%filename_in
    print usage_mesg
    sys.exit(1)

filename_out = '%s.xcorr_hit_list'%filename_in.replace('.target.txt','')
sys.stderr.write("Write %s ... "%filename_out)
f_out = open(filename_out,'w')
f_out.write("#input : %s\n"%filename_in)
f_out.write("#Spectrum_id\tCharge\tPrecursorMz\tMassDiff\tPeptide\tProtein\tMissedCleavages\tScore(Xcorr)\n")

f_in = open(filename_in,'r')
headers = f_in.readline().strip().split("\t")
idx_scan_id = headers.index('scan')
idx_charge = headers.index('charge')
idx_neutral_mass = headers.index('spectrum neutral mass')
idx_peptide_mass = headers.index('peptide mass')
idx_precursor_mz = headers.index('spectrum precursor m/z')
idx_pep_seq = headers.index('sequence')
idx_prot_id = headers.index('protein id')
idx_xcorr = headers.index('xcorr score')

for line in f_in:
    if( line.startswith('#') ):
        continue
    tokens = line.strip().split("\t")
    filename = os.path.basename(filename_in).split('.')[0]
    scan_id = int(tokens[idx_scan_id])

    pep_seq = tokens[idx_pep_seq].upper()
    prot_id = tokens[idx_prot_id].replace('XXX.','xf_')
    prot_id = re.sub('\([0-9]+\)','',prot_id)
    charge = int(tokens[idx_charge])
    precursor_mz = float(tokens[idx_precursor_mz])
    massdiff = float(tokens[idx_neutral_mass]) - float(tokens[idx_peptide_mass])
    xcorr = float(tokens[idx_xcorr]) 
    sp_id = '%s.%05d.%05d.%d'%(filename,scan_id,scan_id,charge)
    f_out.write("%s\t%d\t%f\t%f\t%s\t%s\t-1\t%f\n"%(sp_id,charge,precursor_mz,massdiff,pep_seq,prot_id,xcorr))
f_in.close()
f_out.close()
sys.stderr.write("Done\n")
