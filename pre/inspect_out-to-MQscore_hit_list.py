#!/usr/bin/python
import os
import sys
import re

usage_mesg = 'Usage: inspect_out-to-MQscore_hit_list.py <InsPecT out file>'

if( len(sys.argv) != 2 ):
    print usage_mesg
    sys.exit(1)

filename_in = sys.argv[1]
if( not os.access(filename_in,os.R_OK) ):
    print "%s is not accessible."%filename_in
    print usage_mesg
    sys.exit(1)

filename_out = '%s.MQscore_hit_list'%filename_in
sys.stderr.write("Write %s ... "%filename_out)
f_out = open(filename_out,'w')
f_out.write("#input : %s\n"%filename_in)
f_out.write("#Spectrum_id\tCharge\tNeutralMass\tPeptide\tProtein\tMissedCleavages\tScore(MQScore)\n")
f_in = open(filename_in,'r')
for line in f_in:
    if( line.startswith('#') ):
        continue
    tokens = line.strip().split("\t")
    filename = os.path.basename(tokens[0]).split('.')[0]
    scan_id = int(tokens[1])
    pep_seq = tokens[2].split('.')[1]
    prot_id = tokens[3].replace('XXX.','xf_')
    charge = int(tokens[4])
    MQscore = float(tokens[5]) 
    precursor_mz = float(tokens[-2])
    neutral_mass = precursor_mz * charge
    sp_id = '%s.%05d.%05d.%d'%(filename,scan_id,scan_id,charge)
    f_out.write("%s\t%d\t%f\t%s\t%s\t-1\t%f\n"%(sp_id,charge,neutral_mass,pep_seq,prot_id,MQscore))
f_in.close()
f_out.close()
sys.stderr.write("Done\n")
