#!/usr/bin/env python
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
header_list = f_in.readline().strip().lstrip('#').split("\t")
filename_idx = header_list.index('SpecFile')
scan_id_idx = header_list.index('Scan#')
pep_idx = header_list.index('Peptide')
prot_idx = header_list.index('Protein')
charge_idx = header_list.index('Charge')
precursor_mz_idx = header_list.index('Precursor')
if( 'PMError(ppm)' in header_list ):
    pmerror_idx = header_list.index('PMError(ppm)')
if( 'PMError(Da)' in header_list ):
    pmerror_idx = header_list.index('PMError(Da)')
spec_prob_idx = header_list.index('SpecProb')

for line in f_in:
    if( line.startswith('#') ):
        continue
    tokens = line.strip().split("\t")
    filename = os.path.basename(tokens[filename_idx]).split('.')[0]
    scan_id = int(tokens[scan_id_idx])

    pep_seq = tokens[pep_idx].split('.')[1].upper()
    prot_id = tokens[prot_idx].replace('XXX.','xf_')
    charge = int(tokens[charge_idx])
    precursor_mz = float(tokens[precursor_mz_idx])
    massdiff = float(tokens[pmerror_idx])*1e-6*(precursor_mz-18)
    SpecProb = float(tokens[spec_prob_idx]) 
    #logSpecProb = 50
    #if( SpecProb != 0 ):
    #    logSpecProb = math.log10(SpecProb)*-1.0
    logSpecProb = 50
    if( SpecProb != 0 ):
        logSpecProb = math.log10(SpecProb)*-1.0
    sp_id = '%s.%05d.%05d.%d'%(filename,scan_id,scan_id,charge)
    f_out.write("%s\t%d\t%f\t%f\t%s\t%s\t-1\t%f\n"%(sp_id,charge,precursor_mz,massdiff,pep_seq,prot_id,logSpecProb))
f_in.close()
f_out.close()
sys.stderr.write("Done\n")
