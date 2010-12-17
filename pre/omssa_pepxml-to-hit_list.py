#!/usr/bin/python
import os
import sys
import re
import pepxml
import math

usage_mesg = 'Usage: omssa_pepxml-to-logE_hit_list.py <.pepxml file>'

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
filename_out = re.sub('.pepxml$','',filename_out)
filename_out += '.logE_hit_list'
sys.stderr.write("Write %s ... \n"%filename_out)
f_out = open(filename_out,'w')
f_out.write("# pepxml: %s\n"%filename_pepxml)
f_out.write("#Spectrum_id\tCharge\tNeutralMass\tPeptide\tProtein\tMissedCleavages\tScore(-log10[E-value])\n")
for spectrum_id in PSM.keys():
    charge = PSM[spectrum_id]['charge']
    neutral_mass = PSM[spectrum_id]['neutral_mass']
    best_peptide = ''
    best_protein = ''
    best_expect = 1000000
    best_pvalue = 0
    missed_cleavages = 0
    for tmp_hit in PSM[spectrum_id]['search_hit']:
        if( tmp_hit['expect'] < best_expect ):
            best_pvalue = tmp_hit['pvalue']
            best_peptide = tmp_hit['peptide']
            best_protein = tmp_hit['protein_descr']
            best_expect = tmp_hit['expect']
            missed_cleavages = tmp_hit['missed_cleavages']
    if( best_expect == 0.0 ):
        best_expect = 1e-15
    f_out.write("%s\t%s\t%f\t%s\t%s\t%d\t%f\n"%(spectrum_id,charge,neutral_mass,best_peptide,best_protein,missed_cleavages,-1.0*math.log10(best_expect)))
f_out.close()


if( os.path.exists("pepXML.dtd") ):
    os.remove('pepXML.dtd')