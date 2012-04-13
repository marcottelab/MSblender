#!/usr/bin/python
import os
import sys
import re
# Blake: this is the only thing that makes tide different from sequest: uses
# altered pepxml.py
import pepxml_tide as pepxml

usage_mesg = 'Usage: sequest_pepxml-to-xcorr_hit_list.py <.pepxml file>'

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
filename_out += '.xcorr_hit_list'
sys.stderr.write("Write %s ... \n"%filename_out)
f_out = open(filename_out,'w')
f_out.write("# pepxml: %s\n"%filename_pepxml)
f_out.write("#Spectrum_id\tCharge\tPrecursorMz\tMassDiff\tPeptide\tProtein\tMissedCleavages\tScore(Xcorr)\n")
for spectrum_id in PSM.keys():
    charge = PSM[spectrum_id]['charge']
    precursor_mz = PSM[spectrum_id]['precursor_mz']
    best_peptide = ''
    best_protein = ''
    best_xcorr = 0
    missed_cleavages = -1
    massdiff = 0
    for tmp_hit in PSM[spectrum_id]['search_hit']:
        if( tmp_hit['xcorr'] > best_xcorr ):
            best_xcorr = tmp_hit['xcorr']
            best_peptide = tmp_hit['peptide']
            best_protein = tmp_hit['protein']
            best_deltacn = tmp_hit['deltacn']
            missed_cleavages = tmp_hit['missed_cleavages']
            massdiff = tmp_hit['massdiff']
    f_out.write("%s\t%s\t%f\t%f\t%s\t%s\t%d\t%f\n"%(spectrum_id,charge,precursor_mz,massdiff,best_peptide,best_protein,missed_cleavages,best_xcorr))
f_out.close()
