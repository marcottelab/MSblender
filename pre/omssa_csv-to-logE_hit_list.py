#!/usr/bin/env python
import os
import sys
import pepxml
import math

usage_mesg = 'Usage: omssa_csv-to-logE_hit_list.py <omssa csv file>'

if( len(sys.argv) != 2 ):
    print usage_mesg
    sys.exit(1)

filename_csv = sys.argv[1]
if( not os.access(filename_csv,os.R_OK) ):
    print "%s is not accessible."%filename_csv
    print usage_mesg
    sys.exit(1)

PSM = dict()
f_csv = open(filename_csv,'r')
for line in f_csv:
    if( line.startswith('Spectrum number') ):
        continue
    tokens = line.strip().split(',')
    charge = int(tokens[-4])
    sp_tokens = tokens[1].split('.')
    spectrum_id = "%s.%05d.%05d.%d"%(sp_tokens[0],int(sp_tokens[1]),int(sp_tokens[2]),charge)
    pep_seq = tokens[2]
    e_value = float(tokens[3])
    precursor_mz = float(tokens[4])/charge
    prot_id = tokens[9]
    theoretical_mass = float(tokens[-3])
    if( not PSM.has_key(spectrum_id) ):
        PSM[spectrum_id] = []
    PSM[spectrum_id].append({'charge':charge, 'pep_seq':pep_seq, 'e_value':e_value, 'precursor_mz':precursor_mz, 'massdiff':theoretical_mass - precursor_mz, 'prot_id':prot_id})
f_csv.close()

filename_out = '%s.logE_hit_list'%filename_csv
sys.stderr.write("Write %s ... \n"%filename_out)

f_out = open(filename_out,'w')
f_out.write("#csv: %s\n"%filename_csv)
f_out.write("#Spectrum_id\tCharge\tPrecursorMz\tMassDiff\tPeptide\tProtein\tMissedCleavages\tScore(-log10[E-value])\n")
for spectrum_id in PSM.keys():
    best_evalue = 1000000
    best_psm = 'NA'
    for tmp in PSM[spectrum_id]:
        if( tmp['e_value'] < best_evalue ):
            best_evalue = tmp['e_value']
            best_psm = tmp

    if( best_evalue == 1000000 ):
        continue
    elif( best_evalue < 1e-15 ):
        best_evalue = 1e-15

    f_out.write("%s\t%s\t%f\t%f\t%s\t%s\tNA\t%f\n"%(spectrum_id,best_psm['charge'],best_psm['precursor_mz'],best_psm['massdiff'],best_psm['pep_seq'],best_psm['prot_id'],-1.0*math.log10(best_evalue)))
f_out.close()
