#!/usr/bin/env python
import math
import os
import sys
import re
import tandem_out

usage_mesg = 'Usage: tandem_out-to-logE_hit_list.py <X!Tandem out file>'

if( len(sys.argv) != 2 ):
    print usage_mesg
    sys.exit(1)

filename_in = sys.argv[1]
print filename_in
filename_base = filename_in.split('/')[-1].split('.')[0]

if( not os.access(filename_in,os.R_OK) ):
    print "%s is not accessible."%filename_in
    print usage_mesg
    sys.exit(1)

PSM = tandem_out.parse_by_filename(filename_in)
#MSups_5ul.09112.09112.2	2	2113.017700	-0.000600	MDQTLAVYQQILTSMPSR	P41159|LEP_HUMAN_UPS|147|50000.0	-1	4.343800

filename_out = '%s.logE_hit_list'%filename_in
sys.stderr.write("Write %s ... \n"%filename_out)
f_out = open(filename_out,'w')
f_out.write("#input : %s\n"%filename_in)
f_out.write("#Spectrum_id\tCharge\tPrecursorMass\tMassDiff\tPeptide\tProtein\tMissedCleavages\tScore(-log10[E-value])\n")
for spectrum_id in PSM.keys():
    charge = PSM[spectrum_id]['charge']
    precursor_mass = PSM[spectrum_id]['precursor_mass']
    best_peptide = ''
    best_protein = ''
    best_hyperscore = 0
    missed_cleavages = 0
    massdiff = 0
    for tmp_hit in PSM[spectrum_id]['search_hit']:
        if( tmp_hit['hyperscore'] > best_hyperscore ):
            best_hyperscore = tmp_hit['hyperscore']
            best_peptide = tmp_hit['peptide']
            best_protein = tmp_hit['protein']
            best_expect = tmp_hit['expect']
            missed_cleavages = tmp_hit['missed_cleavages']
            massdiff = tmp_hit['massdiff']
    spectrum_str = '%s.%05d.%05d.%d'%(filename_base,spectrum_id,spectrum_id,charge)
   
    f_out.write("%s\t%s\t%f\t%f\t%s\t%s\t%d\t%f\n"%(spectrum_str,charge,precursor_mass,massdiff,best_peptide,best_protein,missed_cleavages,math.log10(best_expect)*-1))
f_out.close()
