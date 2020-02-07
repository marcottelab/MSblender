#!/usr/bin/env python3
import sys

filename_protGroup = sys.argv[1]

f = open(filename_protGroup, 'r')

h_list = f.readline().strip().split('\t')

h_LFQ_list = []
tmp_idx = 0
for tmp_h in h_list:
    if tmp_h.startswith('LFQ'):
        sys.stderr.write('H: %s\n' % tmp_h)
        h_LFQ_list.append(tmp_idx)
    tmp_idx += 1

print("Protein\t%s" % ("\t".join([h_list[x] for x in h_LFQ_list])))
for line in f:
    tokens = line.strip().split("\t")

    prot_id = tokens[1]
    if prot_id.find('CON_') >= 0 or prot_id.find('REV_') >= 0:
        continue

    out_str = [prot_id]
    for tmp_i in h_LFQ_list:
        out_str.append(tokens[tmp_i])
    if out_str.count('0') >= 3:
        continue
    print("%s" % "\t".join(out_str))
f.close()
