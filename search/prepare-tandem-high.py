#!/usr/bin/env python3
import os
import sys
import re
import stat

usage_mesg = 'Usage: %s <mzXML directory> <fasta_pro file>' % (__file__)

mzXML_dir = sys.argv[1]
filename_fasta_pro = sys.argv[2]

db_name = re.sub('.pro$', '', os.path.basename(filename_fasta_pro))
db_name = re.sub('.fasta$', '', db_name)
db_name = re.sub('.fa$', '', db_name)

abs_path_script = os.path.abspath(__file__)
MSTB_HOME = os.path.abspath(os.path.join(abs_path_script, '..', '..'))

filename_taxon_xml = 'tandem-taxonomy.xml'
filename_taxon_tmpl = os.path.join(MSTB_HOME, 'search',
                                   'tmpl', filename_taxon_xml)

filename_tandem_xml = 'tandem.high.xml'
filename_in_tmpl = os.path.join(MSTB_HOME, 'search',
                                'tmpl', filename_tandem_xml)

filename_sh = 'run-tandem.sh'
filename_tandem_exe = os.path.join(MSTB_HOME, 'extern', 'tandem.linux.exe')
filename_default_xml = os.path.join(MSTB_HOME, 'search',
                                    'isb_default_input_native.xml')

f_taxon_tmpl = open(filename_taxon_tmpl, 'r')
taxon_tmpl = ''.join(f_taxon_tmpl.readlines())
f_taxon_tmpl.close()

sys.stderr.write('Write %s.\n' % filename_taxon_xml)
f_taxon = open(filename_taxon_xml, 'w')
f_taxon.write(taxon_tmpl.format(DB_FASTAPRO=filename_fasta_pro,
                                DB_NAME=db_name))
f_taxon.close()

f_in_tmpl = open(filename_in_tmpl, 'r')
in_tmpl = ''.join(f_in_tmpl.readlines())
f_in_tmpl.close()

f_sh = open(filename_sh, 'w')

f_sh.write('#!/bin/bash\n')
for filename in os.listdir(mzXML_dir):
    if not filename.upper().endswith('.MZXML'):
        continue
    filename_base = '.'.join(filename.split('.')[:-1])
    filename_in = '%s.%s.tandem.xml' % (filename_base, db_name)

    in_params = dict()
    in_params['DB_NAME'] = db_name
    in_params['TANDEM_DEFAULT_PARAM'] = filename_default_xml
    in_params['FILENAME_TAXON'] = filename_taxon_xml
    in_params['FILENAME_MZXML'] = os.path.abspath(os.path.join(mzXML_dir,
                                                               filename))

    filename_out = '%s.%s.tandem.out' % (filename_base, db_name)
    in_params['FILENAME_OUT'] = filename_out
    in_params['FILENAME_LOG'] = '%s.%s.tandemK.log' % (filename_base, db_name)

    sys.stderr.write('Write %s.\n' % filename_in)
    f_in = open(filename_in, 'w')
    f_in.write(in_tmpl.format(**in_params))
    f_in.close()

    f_sh.write("%s %s\n" % (filename_tandem_exe, filename_in))
f_sh.close()

os.chmod(filename_sh, stat.S_IRWXU)
sys.stderr.write('\nTandem is ready. Run %s.\n\n' % (filename_sh))
