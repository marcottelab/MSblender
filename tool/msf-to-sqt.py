#!/usr/bin/python
import os
import sys
import sqlite3

## msf-to-sqt.py : MSF file converter to SQT format
## Author: Taejoon Kwon < taejoon.kwon at 9mai1 dOt c0m >
## Copyright: (c) 2011, 2012, Taejoon Kwon
## License: Artistic License 2.0
##  This program is free software; you can redistribute it and/or modify it
##  under the Artistic License 2.0
##  http://www.opensource.org/licenses/artistic-license-2.0

## Reference to SQT format
## http://noble.gs.washington.edu/proj/crux/sqt-format.html
#######################
program_name= 'msf-to-sqt.py'
program_version = '0.1'
#######################

filename_msf = sys.argv[1]

conn = sqlite3.connect(filename_msf)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

sql_workflow = 'select * from WorkflowInfo'

sql_AA = 'select OneLetterCode as aa\
        ,MonoisotopicMass as mono_mass\
        ,AverageMass as avg_mass\
        from AminoAcids where OneLetterCode!=" "'

sql_PSM = 'select P.SpectrumID as sp_id\
        ,P.Sequence as pep_seq\
        ,P.PeptideID as pep_id\
        ,P.TotalIonsCount as expected_ions\
        ,P.MatchedIonsCount as matched_ions\
        ,PNS.ScoreName as score_name\
        ,PS.ScoreValue as score\
    from PeptideScores as PS \
    inner join ProcessingNodeScores as PNS \
		on PNS.ProcessingNodeID=PS.ProcessingNodeID\
        and PNS.ScoreID=PS.ScoreID\
    inner join Peptides as P \
		on P.ProcessingNodeNumber=PS.ProcessingNodeNumber \
		and P.PeptideID=PS.PeptideID\
    where P.ConfidenceLevel=1'
### Check Level 1,2,3 whether they are exclusive or not. See what happens if the level is not set. 

## SH.Mass: neutralized precursor mass
## MP.Mass: original precursor mass (no charge correction)
sql_spectra = 'select SH.SpectrumID as sp_id\
        ,SH.FirstScan as low_scan\
		,SH.LastScan as high_scan\
		,SH.Charge as charge\
		,SH.RetentionTime as process_time\
        ,SH.Mass as mass\
        ,MP.Intensity as intensity\
	from SpectrumHeaders AS SH\
	inner join MassPeaks as MP\
        on MP.MassPeakID=SH.MassPeakID'

sql_prot = 'select PP.PeptideID as pep_id\
        , PA.Description as prot_name\
    from PeptidesProteins as PP\
    inner join ProteinAnnotations AS PA\
        on PA.ProteinID=PP.ProteinID'

##  Add water and cystine fixed modification + dynamic modification for mass calcuation. 

sys.stderr.write("Read basic info ... ")
cur.execute(sql_workflow)
info = cur.fetchone()
cur.execute(sql_AA)
aa_mass = dict()
for row_AA in cur:
    aa_mass[ row_AA['aa'] ] = row_AA['avg_mass']
sys.stderr.write("Done\n")

def pep_mass(tmp_pep):
    rv = 0.0
    for tmp_aa in tmp_pep:
        rv += aa_mass[tmp_aa]
    return rv

sys.stderr.write("Read spectrum headers ... ")
sp_headers = dict()
cur.execute(sql_spectra)
for row_sp in cur:
    sp_headers[ row_sp['sp_id'] ] = row_sp
sys.stderr.write("Done\n")

sys.stderr.write("Read peptide-protein mapping ... ")
pep2prot = dict()
cur.execute(sql_prot)
for row_prot in cur:
    if( not pep2prot.has_key(row_prot['pep_id']) ):
        pep2prot[row_prot['pep_id']] = []
    pep2prot[row_prot['pep_id']].append( row_prot['prot_name'] )
sys.stderr.write("Done\n")

sys.stderr.write("Read peptide-spectrum matching ... ")
psm = dict()
cur.execute(sql_PSM)
for row_psm in cur:
    if( not psm.has_key( row_psm['sp_id'] ) ):
        psm[ row_psm['sp_id'] ] = []
    psm[ row_psm['sp_id'] ].append(row_psm)
sys.stderr.write("Done\n")

#######################################3
## Headers
filename_out = filename_msf.replace('.msf','')+'.sqt'
sys.stderr.write("Write %s ... "%filename_out)
f_out = open(filename_out,'w')
not_available = 'NA'
precursor_mass_method = 'average'
fragment_mass_method = 'mono'
f_out.write("H\tSQTGenerator\t%s\n"%program_name)
f_out.write("H\tSQTGeneratorVersion\t%s\n"%program_version)
f_out.write("H\tDatabase\t%s\n"%not_available)
f_out.write("H\tPrecursorMasses\t%s\n"%precursor_mass_method)
f_out.write("H\tFragmentMasses\t%s\n"%fragment_mass_method)
f_out.write("H\tStartTime\t%s\n"%info['WorkflowStartDate'])
f_out.write("H\tStaticMod\t%s\n"%not_available)
f_out.write("H\tDynamicMod\t%s\n"%not_available)

for sp_id in sorted(sp_headers.keys(),key=lambda x:int(x)):
    if( not psm.has_key(sp_id) ):
        continue
    tmp_sp = sp_headers[sp_id]
    
    psm_map = dict()
    for tmp_psm in psm[sp_id]:
        if( not psm_map.has_key(tmp_psm['pep_seq']) ):
            psm_map[ tmp_psm['pep_seq'] ] = {'pep_id': tmp_psm['pep_id']}
            psm_map[ tmp_psm['pep_seq'] ]['matched_ions'] = tmp_psm['matched_ions']
            psm_map[ tmp_psm['pep_seq'] ]['expected_ions'] = tmp_psm['expected_ions']
        psm_map[ tmp_psm['pep_seq'] ][ tmp_psm['score_name'] ] = tmp_psm['score']
    
    SpScore_sorted = sorted([tmp_psm['SpScore'] for tmp_psm in psm_map.values()])
    XCorr_sorted = sorted([tmp_psm['XCorr'] for tmp_psm in psm_map.values()],reverse=True)
    
    ## Spectrum record
    f_out.write("S\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%f\t%d\n"%\
        ( tmp_sp['low_scan'],tmp_sp['high_scan'],tmp_sp['charge']\
         ,tmp_sp['process_time'],info['MachineName'],tmp_sp['mass']\
         ,tmp_sp['intensity'],SpScore_sorted[0],len(psm_map) ))
    
    prev_xcorr = 0.0
    for pep_seq in sorted(psm_map.keys(),key=lambda x: psm_map[x]['XCorr'],reverse=True):
        sp = psm_map[pep_seq]['SpScore']
        xcorr = psm_map[pep_seq]['XCorr']
        sp_rank = SpScore_sorted.index(sp) + 1
        xcorr_rank = XCorr_sorted.index(xcorr) + 1
        matched_ions = psm_map[pep_seq]['matched_ions']
        expected_ions = psm_map[pep_seq]['expected_ions']
        calc_mass = pep_mass(pep_seq)
        deltaCn = 0.0
        if( xcorr_rank != 1 ):
            deltaCn = (prev_xcorr - xcorr)/prev_xcorr
        prev_xcorr = xcorr
        f_out.write("M\t%d\t%d\t%.3f\t%.4f\t%.4f\t%.2f\t%d\t%d\tX.%s.X\tU\n"%\
            (xcorr_rank,sp_rank,calc_mass,deltaCn,xcorr,sp,matched_ions,expected_ions,pep_seq))
        #print sp_id,xcorr_rank,sp_rank,deltaCn,xcorr,sp,matched_ions,expected_ions,pep_seq,calc_mass
        for tmp_prot in pep2prot[ psm_map[pep_seq]['pep_id'] ]:
            f_out.write("L\t%s\n"%tmp_prot)
f_out.close()
sys.stderr.write("Done\n")
