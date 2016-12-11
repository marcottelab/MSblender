#!/usr/bin/env python
import math
import os
import sys
import re

usage_mesg = 'Usage: %s.py <.txt file from PD>'%sys.argv[0]

if( len(sys.argv) != 2 ):
    print usage_mesg
    sys.exit(1)

filename_in = sys.argv[1]
if( not os.access(filename_in,os.R_OK) ):
    print "%s is not accessible."%filename_in
    print usage_mesg
    sys.exit(1)

filename_out = '%s.xcorr_hit_list'%filename_in.replace('.txt','')
sys.stderr.write("Write %s ... "%filename_out)
f_out = open(filename_out,'w')
f_out.write("#input : %s\n"%filename_in)
f_out.write("#Spectrum_id\tCharge\tPrecursorMz\tMassDiff\tPeptide\tProtein\tMissedCleavages\tScore(Xcorr)\n")

f_in = open(filename_in,'r')
headers = f_in.readline().strip().split("\t")
idx_scan_id = headers.index('"First Scan"')
idx_charge = headers.index('"Charge"')
idx_precursor_mz = headers.index('"m/z [Da]"')
idx_delta_mass = headers.index('"Delta Mass [Da]"')
idx_pep_seq = headers.index('"Sequence"')
idx_prot_id = headers.index('"Protein Descriptions"')
idx_prot_acc = headers.index('"Protein Group Accessions"')
idx_xcorr = headers.index('"XCorr"')
idx_filename = headers.index('"Spectrum File"')
idx_missed_cleavages = headers.index('"# Missed Cleavages"')

for line in f_in:
    if( line.startswith('#') ):
        continue
    tokens = line.strip().replace('"','').split("\t")
    
    filename = re.sub('\.(?i)RAW$','',tokens[idx_filename])
    scan_id = int(tokens[idx_scan_id])

    pep_seq = tokens[idx_pep_seq].upper()
    prot_acc = tokens[idx_prot_acc]
    prot_id = '%s|%s'%(prot_acc,tokens[idx_prot_id])

    charge = int(tokens[idx_charge])
    precursor_mz = float(tokens[idx_precursor_mz])
    massdiff = float(tokens[idx_delta_mass])
    xcorr = float(tokens[idx_xcorr]) 
    missed_cleavages = int(tokens[idx_missed_cleavages])
    sp_id = '%s.%05d.%05d.%d'%(filename,scan_id,scan_id,charge)
    f_out.write("%s\t%d\t%f\t%f\t%s\t%s\t%d\t%f\n"%(sp_id,charge,precursor_mz,massdiff,pep_seq,prot_id,missed_cleavages,xcorr))
f_in.close()
f_out.close()
sys.stderr.write("Done\n")

#### Snippet of output txt 
#"Confidence Level"	"Search ID"	"Processing Node No"	"Sequence"	"Unique Sequence ID"	"PSM Ambiguity"	"Protein Descriptions"	"# Proteins"	"# Protein Groups"	"Protein Group Accessions"	"Modifications"	"Activation Type"	"DeltaScore"	"DeltaCn"	"Rank"	"Search Engine Rank"	"Peptides Matched"	"XCorr"	"# Missed Cleavages"	"Isolation Interference [%]"	"Ion Inject Time [ms]"	"Intensity"	"Charge"	"m/z [Da]"	"MH+ [Da]"	"Delta Mass [Da]"	"Delta Mass [PPM]"	"RT [min]"	"First Scan"	"Last Scan"	"MS Order"	"Ions Matched"	"Matched Ions"	"Total Ions"	"Spectrum File"	"Annotation"
#"Middle"	"A"	"2"	"QQYESVAAK"	"1"	"Unambiguous"	"Q5JVS8 Q5JVS8_HUMAN|VIM|B0YJC5 B0YJC5_HUMAN|VIM|P08670 VIME_HUMAN|VIM|B0YJC4 B0YJC4_HUMAN|VIM"	"4"	"4"	"tr;sp"	""	"CID"	"0.3313"	"0.0000"	"1"	"1"	"838"	"1.63"	"0"	"40"	"400"	"1.624e+04"	"2"	"512.25800"	"1023.50871"	"0.00"	"-1.82"	"13.02"	"687"	"687"	"MS2"	"0/0"	"0"	"0"	"20120401_Huvec1b_TBZ.RAW"	""
#"Middle"	"A"	"2"	"mSSPKRSSK"	"2"	"Unconsidered"	"B3KS81 SRRM5_HUMAN|SRRM5"	"1"	"1"	"sp"	"M1(Oxidation)"	"CID"	""	"0.3313"	"2"	"2"	"838"	"1.09"	"2"	"40"	"400"	"1.624e+04"	"2"	"512.25800"	"1023.50871"	"-0.01"	"-16.11"	"13.02"	"687"	"687"	"MS2"	"0/0"	"0"	"0"	"20120401_Huvec1b_TBZ.RAW"	""
