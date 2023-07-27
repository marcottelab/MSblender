from __future__ import division
import sys
from collections import defaultdict
import numpy as np
import utils as ut

def write_prot_counts(f_peplist, only_uniques, f_pep2prots=None):
    if f_peplist.find('pep_count_') > -1:
        peplist = peplist_from_pepcount(f_peplist)
    else:
        peplist = ut.load_list_of_lists(f_peplist)
    if f_pep2prots:
        pep2prots = load_pep2prots(f_pep2prots)
        prots, samples, counts, totals = prot_counts_pep2prots(peplist,
                only_uniques, pep2prots)
    else:
        prots, samples, counts, totals = prot_counts(peplist, only_uniques)
    suffix = 'prot_count' + ('_uniqpeps2' if only_uniques else '')
    fname_out = f_peplist.replace('pep_list',suffix).replace('pep_count',suffix)
    f_counts = open(fname_out, 'w')
    f_counts.write("#ProtID\tTotalCount\t%s\n"%('\t'.join(samples)))
    for i,prot in enumerate(prots):
        out_str = ['%0.2f' % count for count in counts[i,:]]
        f_counts.write("%s\t%.2f\t%s\n"%(prot, totals[i], '\t'.join(out_str)))
    f_counts.close()

def peplist_from_pepcount(f):
    """
    Create list of (blank, sample, peptideseq, count) from table of peptideseqs
    by samples.
    """
    peps, samples, arr = load_pepcount(f)
    peplist = [('-', samples[sample], peps[pep], arr[pep, sample]) 
            for pep,sample in zip(*np.where(arr))]
    return peplist

def load_pepcount(f):
    lol = ut.load_lol(f)
    print "Omitting header:", lol[0]
    lol = lol[1:]
    peps = ut.i0(lol[1:])
    samples = lol[0][2:]
    arr = np.zeros((len(peps), len(samples)))
    for i,row in enumerate(lol[1:]):
        arr[i,:] = row[2:]
    return peps, samples, arr

def load_pep2prots(filename, sep='|'):
    """
    Separator is '|' for most of andrew's files, but '&' for Nv and Xl.
    """
    pep2prots = dict(((line[0], set([p.split()[0] for p in
        line[1].split(sep)])) for line in ut.load_tab_file(filename)))
    print "First 10 peptide mappings:", pep2prots.items()[:10]
    return pep2prots

def prot_counts_pep2prots(peplist, only_uniques, pep2prots):
    """
    - pep2prots: use supplied dict of {peptide: set(proteinids)} instead of the
      protein ids on the lines in the pep_list file, in which case sum up the
      counts for a peptide-spectral combination. 
    """
    assert only_uniques, "Only handles only_uniques=True so far."
    exclude_peps = (set([pep for pep,prots in pep2prots.items() if len(prots)>1])
            if only_uniques else set([]))
    print "%s non-unique peptides to exclude." % len(exclude_peps)
    pep_samp_counts = defaultdict(float)
    for _,sample,pep,count in peplist:
        if pep not in exclude_peps:
            pep_samp_counts[(pep,sample)] += float(count)
    # Currently ignoring peptides without a mapping.
    prots = sorted(list(reduce(set.union, [pep2prots[pep] for (pep,_),_ in
        pep_samp_counts.items() if pep in pep2prots])))
    samples = sorted(list(set(ut.i1(peplist))))
    print "%s unique proteins. %s samples." % (len(prots), len(samples))
    dprots, dsamples = [ut.list_inv_to_dict(lst) for lst in prots, samples]
    counts = np.zeros((len(prots), len(samples)), dtype='float32')
    for (pep,sample),count in pep_samp_counts.items():
        if pep in pep2prots: # Currently ignoring peptides without a mapping.
            assert len(pep2prots[pep])==1, "Non-unique peptide found"
            counts[dprots[list(pep2prots[pep])[0]], dsamples[sample]] += count
    totals = counts.sum(axis=1)
    nonzero = totals > 0
    prots, totals = [list(np.array(lst)[nonzero]) for lst in prots, totals]
    counts = counts[nonzero,:]
    return prots, samples, counts, totals


def prot_counts(peplist, only_uniques):
    """
    Deprecated 20130628. pep_list doesn't seem consistent for protein
    assignments.
    mainly returns the counts array with protein quantations.
    - exclude_peps: set of peptides to exclude, probably from non_unique_peps.
    """
    print "**Deprecated 20130628**"
    exclude_peps = non_unique_peps(peplist) if only_uniques else set([])
    prots,samples = [sorted(list(set(lst))) 
            for lst in zip(*[i[:2] for i in peplist])]
    dprots, dsamples = [ut.list_inv_to_dict(lst) for lst in prots, samples]
    counts = np.zeros((len(prots), len(samples)), dtype='float32')
    for prot_peplist, sample, pep, count in peplist:
        if pep not in exclude_peps:
            counts[dprots[prot],dsamples[sample]] += float(count)
    totals = counts.sum(axis=1)
    nonzero = totals > 0
    prots, totals = [list(np.array(lst)[nonzero]) for lst in prots, totals]
    counts = counts[nonzero,:]
    return prots, samples, counts, totals

def non_unique_peps(peplist):
    """
    Peplist: list-of-lists read in from an msblender pep_list file
    """
    pep2prots = defaultdict(set)
    for prot,sample,pep,count in peplist:
        pep2prots[pep].add(prot)
    non_unique = set([pep for pep,prots in pep2prots.items() if len(prots)>1])
    return non_unique

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit("usage: python protein_counts.py f_peplist/f_pep_count only_uniques [f_pep2prots]")
    only_uniques = sys.argv[2] == 'True'
    f_pep2prots = sys.argv[3] if len(sys.argv)>3 else None
    print 'Counting proteins.  Only uniques:', only_uniques
    print "Peptide to proteins:", f_pep2prots
    write_prot_counts(sys.argv[1], only_uniques, f_pep2prots)



