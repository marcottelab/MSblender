#!/usr/bin/python
import os
import sys
import re
import pepxml

usage_mesg = 'Usage: inspect-pepxml2hit_list.py <.pepxml file>'

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
filename_out += '.hit_list'
sys.stderr.write("Write %s ... \n"%filename_out)
f_out = open(filename_out,'w')
f_out.write("# pepxml: %s\n"%filename_pepxml)
f_out.write("#Spectrum_id\tCharge\tNeutralMass\tPeptide\tProtein\tMissedCleavages\tAbsScore(MQScore)\tRelScore(DeltaScore)\n")
for spectrum_id in PSM.keys():
    charge = PSM[spectrum_id]['charge']
    neutral_mass = PSM[spectrum_id]['neutral_mass']
    best_peptide = ''
    best_protein = ''
    best_mqscore = -100
    best_deltascore = 0
    missed_cleavages = 0
    for tmp_hit in PSM[spectrum_id]['search_hit']:
        if( tmp_hit['hit_rank'] != 1 ):
            continue
        if( tmp_hit['mqscore'] > best_mqscore ):
            best_mqscore = tmp_hit['mqscore']
            best_peptide = tmp_hit['peptide']
            best_protein = tmp_hit['protein']
            best_deltascore = tmp_hit['deltascore']
            missed_cleavages = tmp_hit['missed_cleavages']
    if( best_mqscore > -100 ):
        f_out.write("%s\t%s\t%f\t%s\t%s\t%d\t%f\t%f\n"%(spectrum_id,charge,neutral_mass,best_peptide,best_protein,missed_cleavages,best_mqscore,best_deltascore))
f_out.close()
