#!/usr/bin/env python
import os
import sys
import re
import pepxml
import math

usage_mesg = 'Usage: mascot_pepxml-to-ionscore_hit_list.py <.pepxml file>'

## It is required for SAX parser
if( not os.path.exists("pepXML.dtd") ):
    open('pepXML.dtd','w').close()

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
#filename_out = re.sub('.pep.xml$','',filename_out)

filename_out += '.ionscore_hit_list'
sys.stderr.write("Write %s ... \n"%filename_out)
f_out = open(filename_out,'w')
f_out.write("# pepxml: %s\n"%filename_pepxml)
f_out.write("#Spectrum_id\tCharge\tPrecursorMz\tMassDiff\tPeptide\tProtein\tMissedCleavages\tScore(ionscore)\n")
for spectrum_id in PSM.keys():
    charge = PSM[spectrum_id]['charge']
    precursor_mz = PSM[spectrum_id]['precursor_mz']
    best_peptide = ''
    best_protein = ''
    best_ionscore = 0
    missed_cleavages = 0
    massdiff = 0.0
    for tmp_hit in PSM[spectrum_id]['search_hit']:
        if( tmp_hit['ionscore'] > best_ionscore):
            best_peptide = tmp_hit['peptide']
            #best_protein = tmp_hit['protein_descr']
            best_protein = tmp_hit['protein']
            best_ionscore = tmp_hit['ionscore']
            missed_cleavages = tmp_hit['missed_cleavages']
            massdiff = tmp_hit['massdiff']
    f_out.write("%s\t%s\t%f\t%f\t%s\t%s\t%d\t%f\n"%(spectrum_id,charge,precursor_mz,massdiff,best_peptide,best_protein,missed_cleavages,best_ionscore))
f_out.close()


if( os.path.exists("pepXML.dtd") ):
    os.remove('pepXML.dtd')
