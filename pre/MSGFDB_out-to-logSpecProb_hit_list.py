#!/usr/bin/python
import math
import os
import sys

usage_mesg = 'Usage: MSGFDB_out-to-logSpecProb_hit_list.py <MS-GFDB out file>'

if( len(sys.argv) != 2 ):
    print usage_mesg
    sys.exit(1)

filename_in = sys.argv[1]
if( not os.access(filename_in,os.R_OK) ):
    print "%s is not accessible."%filename_in
    print usage_mesg
    sys.exit(1)

filename_out = '%s.logSpecProb_hit_list'%filename_in
sys.stderr.write("Write %s ... "%filename_out)
f_out = open(filename_out,'w')
f_out.write("#input : %s\n"%filename_in)
f_out.write("#Spectrum_id\tCharge\tPrecursorMz\tMassDiff\tPeptide\tProtein\tMissedCleavages\tScore(-log10[SpecProb])\n")
f_in = open(filename_in,'r')
for line in f_in:
    if( line.startswith('#') ):
        continue
    tokens = line.strip().split("\t")
    filename = os.path.basename(tokens[0]).split('.')[0]
    scan_id = int(tokens[1])

    pep_seq = tokens[6].split('.')[1]
    prot_id = tokens[7].replace('XXX.','xf_')
    charge = int(tokens[5])
    precursor_mz = float(tokens[3])
    massdiff = float(tokens[4])*1e-6*(precursor_mz-18)
    SpecProb = float(tokens[-1]) 
    sp_id = '%s.%05d.%05d.%d'%(filename,scan_id,scan_id,charge)
    f_out.write("%s\t%d\t%f\t%f\t%s\t%s\t-1\t%f\n"%(sp_id,charge,precursor_mz,massdiff,pep_seq,prot_id,-1.0*math.log10(SpecProb)))
f_in.close()
f_out.close()
sys.stderr.write("Done\n")
