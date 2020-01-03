#!/usr/bin/env python3
import sys

filename_mzXML = sys.argv[1]

scan_id = 0
scan_info = dict()

f_mzXML = open(filename_mzXML, 'r')
for line in f_mzXML:
    line = line.strip().rstrip('>')

    if line.startswith('<scan '):
        scan_id = int(line.replace('"', '').split('=')[1])
        if scan_id not in scan_info:
            scan_info[scan_id] = {'ms2_count': 0}

    if line.startswith('msLevel='):
        tmp_msLevel = int(line.replace('"', '').split('=')[1])
        scan_info[scan_id]['msLevel'] = tmp_msLevel

    if line.startswith('retentionTime='):
        tmp_retTime = line.replace('"', '').split('=')[1]
        tmp_retTime = tmp_retTime.lstrip('PT').rstrip('S')
        scan_info[scan_id]['ret_time'] = float(tmp_retTime)

    if line.startswith('totIonCurrent='):
        tmp_totIon = line.replace('"', '').split('=')[1]
        scan_info[scan_id]['tot_ion'] = float(tmp_totIon)

    if line.startswith('<precursorMz'):
        for tmp in line.split()[1:]:
            tmp = tmp.split('>')[0]
            if tmp.startswith('precursorScanNum'):
                tmp_precursor_id = int(tmp.replace('"', '').split('=')[1])
                scan_info[scan_id]['precursor_id'] = tmp_precursor_id
                scan_info[tmp_precursor_id]['ms2_count'] += 1

            if tmp.startswith('precursorCharge'):
                tmp_charge = tmp.replace('"', '').split('=')[1]
                scan_info[scan_id]['precursor_charge'] = int(tmp_charge)

        tmp_mz = line.split('>')[1].split('<')[0]
        scan_info[scan_id]['precursor_mz'] = float(tmp_mz)
f_mzXML.close()

# Some mzXML do not have precirsorScanNum
ms1_id = 0
for tmp_scan_id in sorted(scan_info.keys()):
    if scan_info[tmp_scan_id]['msLevel'] == 1:
        ms1_id = tmp_scan_id

    else:
        scan_info[ms1_id]['ms2_count'] += 1
        scan_info[tmp_scan_id]['precursor_id'] = ms1_id


def get_param(args, keyword):
    if keyword in args:
        return args[keyword]
    return 0.0


f_ms1 = open('%s.ms1_info' % filename_mzXML, 'w')
f_ms2 = open('%s.ms2_info' % filename_mzXML, 'w')
tmp_h1 = '#ScanID\tRetTime\tCountMS2\tTotIon'
f_ms1.write(tmp_h1 + '\n')
tmp_h2 = '#ScanID\tRetTime\tPrecursorID\tPrecursorCharge\tPrecursorMz\tTotIon'
f_ms2.write(tmp_h2 + '\n')

for tmp_scan_id in sorted(scan_info.keys()):
    tmp = scan_info[tmp_scan_id]

    if tmp['msLevel'] == 1:
        f_ms1.write('%05d\t%.4f\t%d\t%d\n' %
                    (tmp_scan_id, tmp['ret_time'],
                     tmp['ms2_count'], tmp['tot_ion']))

    if tmp['msLevel'] == 2:
        tmp_ret_time = get_param(tmp, 'ret_time')
        tmp_precursor_charge = get_param(tmp, 'precursor_charge')
        tmp_precursor_id = get_param(tmp, 'precursor_id')
        tmp_precursor_mz = get_param(tmp, 'precursor_mz')
        tmp_tot_ion = get_param(tmp, 'tot_ion')
        f_ms2.write('%05d\t%.4f\t%05d\t%d\t%.5f\t%.2f\n' %
                    (tmp_scan_id, tmp_ret_time, tmp_precursor_id,
                     tmp_precursor_charge, tmp_precursor_mz, tmp_tot_ion))
f_ms1.close()
f_ms2.close()
