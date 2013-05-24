import sys
from collections import defaultdict
import numpy as np
import utils as ut

def write_prot_counts(f_peplist, only_uniques=True):
    peplist = ut.load_list_of_lists(f_peplist)
    prots, samples, counts, totals = prot_counts(peplist, only_uniques)
    suffix = 'prot_count' + ('_uniqpeps' if only_uniques else '')
    f_counts = open(f_peplist.replace('pep_list',suffix), 'w')
    f_counts.write("#ProtID\tTotalCount\t%s\n"%('\t'.join(samples)))
    for i,prot in enumerate(prots):
        out_str = ['%0.2f' % count for count in counts[i,:]]
        f_counts.write("%s\t%.2f\t%s\n"%(prot, totals[i], '\t'.join(out_str)))
    f_counts.close()

def prot_counts(peplist, only_uniques):
    """
    Exclude_peps: set of peptides to exclude, probably from non_unique_peps.
    """
    prots,samples = [sorted(list(set(lst))) 
            for lst in zip(*[i[:2] for i in peplist])]
    dprots, dsamples = [ut.list_inv_to_dict(lst) for lst in prots, samples]
    exclude_peps = non_unique_peps(peplist) if only_uniques else set([])
    counts = np.zeros((len(prots), len(samples)), dtype='float32')
    for prot, sample, pep, count in peplist:
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
        sys.exit("usage: python protein_counts.py f_peplist only_uniques")
    only_uniques = sys.argv[2] == 'True'
    print 'Counting proteins.  Only uniques:', only_uniques
    write_prot_counts(sys.argv[1], only_uniques)

