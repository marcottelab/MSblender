#!/usr/bin/env python
import math
import os
import sys
import re

usage_mesg = 'Usage: MSGF+_tsv-to-logSpecE_hit_list.py <MS-GF+ tsv file>'

if( len(sys.argv) != 2 ):
    print usage_mesg
    sys.exit(1)

filename_in = sys.argv[1]
if( not os.access(filename_in,os.R_OK) ):
    print "%s is not accessible."%filename_in
    print usage_mesg
    sys.exit(1)

filename_out = '%s.logSpecE_hit_list'%filename_in
sys.stderr.write("Write %s ... "%filename_out)
f_out = open(filename_out,'w')
f_out.write("#input : %s\n"%filename_in)
f_out.write("#Spectrum_id\tCharge\tPrecursorMass\tMassDiff\tPeptide\tProtein\tMissedCleavages\tScore(-log10[SpecE])\n")

#SpecFile   SpecID  ScanNum FragMethod  Precursor   IsotopeError    PrecursorError(ppm) Charge  Peptide Protein DeNovoScore MSGFScore   SpecEValue  EValue
f_in = open(filename_in,'r')
header_list = f_in.readline().strip().lstrip('#').split("\t")
filename_idx = header_list.index('SpecFile')
scan_id_idx = header_list.index('SpecID')
pep_idx = header_list.index('Peptide')
prot_idx = header_list.index('Protein')
charge_idx = header_list.index('Charge')
precursor_mz_idx = header_list.index('Precursor')
if( 'PrecursorError(ppm)' in header_list ):
    pmerror_idx = header_list.index('PrecursorError(ppm)')
spec_prob_idx = header_list.index('SpecEValue')

for line in f_in:
    if( line.startswith('#') ):
        continue
    tokens = line.strip().split("\t")
    filename = os.path.basename(tokens[filename_idx]).split('.')[0]
    scan_id = int(tokens[scan_id_idx].replace('scan=',''))

    pep_seq = tokens[pep_idx].upper()
    pep_seq = re.sub(r'[0-9+.]','',pep_seq)
    prot_id = tokens[prot_idx]
    charge = int(tokens[charge_idx])
    precursor_mz = float(tokens[precursor_mz_idx])
    precursor_mass = precursor_mz*charge
    massdiff = float(tokens[pmerror_idx])*1e-6*(precursor_mz-18)
    SpecE = float(tokens[spec_prob_idx]) 
    
    logSpecE = 100
    if( SpecE != 0 ):
        logSpecE = math.log10(SpecE)*-1.0
    
    sp_id = '%s.%05d.%05d.%d'%(filename,scan_id,scan_id,charge)
    f_out.write("%s\t%d\t%f\t%f\t%s\t%s\t-1\t%f\n"%(sp_id,charge,precursor_mass,massdiff,pep_seq,prot_id,logSpecE))
f_in.close()
f_out.close()
sys.stderr.write("Done\n")
