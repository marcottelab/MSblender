#!/usr/bin/env python
import os
import sys
import re

usage_mesg = 'Usage: comet_txt-to-xcorr_hit_list.py <comet.txt file>'

if( len(sys.argv) != 2 ):
    print usage_mesg
    sys.exit(1)

filename_txt = sys.argv[1]
if( not os.access(filename_txt,os.R_OK) ):
    print "%s is not accessible."%filename_txt
    print usage_mesg
    sys.exit(1)

filename_base = re.sub('.txt','',filename_txt)
filename_out = '%s.xcorr_hit_list'%filename_base

sys.stderr.write("Write %s ... \n"%filename_out)
f_out = open(filename_out,'w')
f_out.write("#txt: %s\n"%filename_txt)
f_out.write("#Spectrum_id\tCharge\tPrecursorMass\tMassDiff\tPeptide\tProtein\tMissedCleavages\tScore(Xcorr)\n")

f_txt = open(filename_txt,'r')
f_txt.readline()
f_txt.readline()
for line in f_txt:
    tokens = line.strip().split("\t")
    ## Spectrum without hit
    if( len(tokens) == 3 ):
        continue
    scan_id = int(tokens[0])
    charge = int(tokens[1])
    sp_id = '%s.%05d.%05d.%d'%(filename_base.split('.')[0],scan_id,scan_id,charge)
    exp_neutral_mass = float(tokens[2])
    calc_neutral_mass = float(tokens[3])
    xcorr = float(tokens[5])
    peptide = tokens[11]
    protein = tokens[15]
    massdiff = exp_neutral_mass - calc_neutral_mass
    f_out.write("%s\t%d\t%f\t%f\t%s\t%s\t-1\t%f\n"%(sp_id,charge,exp_neutral_mass,massdiff,peptide,protein,xcorr))
f_out.close()

#CometVersion 2013.02 rev. 0 /work/ups/Vogel2009_UPS/comet.test/MSups_5ul.UPS2013_combined.comet 11/21/2013, 11:59:16 AM /work/ups/db/UPS2013_combined.fa
#scan    charge  exp_neutral_mass    calc_neutral_mass   e-value xcorr   delta_cn    sp_score    ions_matched    ions_total  plain_peptide   peptide prev_aa next_aa protein duplicate_protein_count
