#!/usr/bin/env python
import os
import sys
import re
import pepxml
import math

usage_mesg = 'Usage: tandem_pepxml-to_logE_hit_list.py <.pepxml file>'

if( len(sys.argv) != 2 ):
    print usage_mesg
    sys.exit(1)

filename_pepxml = sys.argv[1]
if( not os.access(filename_pepxml,os.R_OK) ):
    print "%s is not accessible."%filename_pepxml
    print usage_mesg
    sys.exit(1)

PSM = pepxml.parse_by_filename(filename_pepxml)

filename_out = filename_pepxml
#filename_out = re.sub('.pepxml$','',filename_out)
filename_out += '.logE_hit_list'
sys.stderr.write("Write %s ... \n"%filename_out)
f_out = open(filename_out,'w')
f_out.write("# pepxml: %s\n"%filename_pepxml)
f_out.write("#Spectrum_id\tCharge\tPrecursorMz\tMassDiff\tPeptide\tProtein\tMissedCleavages\tScore(-log10[E-value])\n")
for spectrum_id in PSM.keys():
    charge = PSM[spectrum_id]['charge']
    precursor_mz = PSM[spectrum_id]['precursor_mz']
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
    f_out.write("%s\t%s\t%f\t%f\t%s\t%s\t%d\t%f\n"%(spectrum_id,charge,precursor_mz,massdiff,best_peptide,best_protein,missed_cleavages,math.log10(best_expect)*-1))
f_out.close()
