#!/usr/bin/env python
import os
import sys
import re
import stat

usage_mesg = 'Usage: prepare-tandemK-high.py <mzXML file> <fasta_pro file> <tandem dir>'

mzXML = sys.argv[1]
filename_fasta_pro = sys.argv[2]
db_name = re.sub('.pro$','', os.path.basename(filename_fasta_pro))
db_name = re.sub('.fasta$','',db_name)
db_name = re.sub('.fa$','',db_name)

tandem_dir = sys.argv[3]


abs_path_script = os.path.abspath(__file__)
MSTB_HOME = os.path.abspath( os.path.join(abs_path_script, '..', '..') )

filename_taxon_xml = 'tandem-taxonomy.xml'
 #need to see if this is added into the config xml
filename_taxon_xml_path = tandem_dir + "/" + filename_taxon_xml
filename_taxon_tmpl = os.path.join(MSTB_HOME,'search','tmpl',filename_taxon_xml)

filename_tandem_xml = 'tandemK.high.xml'
filename_in_tmpl = os.path.join(MSTB_HOME,'search','tmpl',filename_tandem_xml)

filename_sh = 'run-tandemK.sh'
#filename_tandem_exe = os.path.join(MSTB_HOME,'extern','tandem.linux.exe') 
filename_tandem_exe=sys.argv[4]
filename_default_xml = os.path.join(MSTB_HOME,'search','isb_default_input_kscore.xml')

f_taxon_tmpl = open(filename_taxon_tmpl,'r')
taxon_tmpl = ''.join( f_taxon_tmpl.readlines() )
f_taxon_tmpl.close()

sys.stderr.write('Write %s.\n'%filename_taxon_xml)

filename_taxon_xml_path = tandem_dir + "/" + filename_taxon_xml 
f_taxon = open(filename_taxon_xml_path,'w')
f_taxon.write( taxon_tmpl.format(DB_FASTAPRO=filename_fasta_pro, DB_NAME=db_name) )
f_taxon.close()

f_in_tmpl = open(filename_in_tmpl,'r')
in_tmpl = ''.join( f_in_tmpl.readlines() )
f_in_tmpl.close()

filename_sh_path = tandem_dir + "/" + filename_sh
print "%s is the tandemk.sh script path"%(filename_sh_path)

f_sh = open(filename_sh_path,'w')
f_sh.write('#!/bin/bash\n')
#for filename in os.listdir(mzXML):
filename=mzXML
if(filename.upper().endswith('.MZXML')):
    print filename
    filename_base = '.'.join(filename.split('.')[:-1])
    filename_base = filename_base.split("/")[-1]
    print(filename_base)
    #print "that was the filename_base"
    filename_in = '%s.%s.tandemK.xml'%(filename_base,db_name)

    in_params = dict()
    in_params['DB_NAME'] = db_name
    in_params['TANDEMK_DEFAULT_PARAM'] = filename_default_xml
    in_params['FILENAME_TAXON'] = filename_taxon_xml_path
    in_params['FILENAME_MZXML'] = os.path.abspath(mzXML)
    filename_out = '%s.%s.tandemK.out'%(filename_base,db_name)
    filename_out_path = tandem_dir + "/" + filename_out
    in_params['FILENAME_OUT'] = filename_out_path
    in_params['FILENAME_LOG'] = '%s.%s.tandemK.log'%(filename_base,db_name)

    sys.stderr.write('Write %s.\n'%filename_in)

    filename_in_path = tandem_dir + "/" + filename_in
    f_in = open(filename_in_path,'w')
    f_in.write( in_tmpl.format(**in_params) )
    f_in.close()
    
    f_sh.write("%s %s\n"%(filename_tandem_exe, filename_in_path))
f_sh.close()

os.chmod(filename_sh_path,stat.S_IRWXU)
sys.stderr.write('\nTandemK is ready. Run %s.\n\n'%(filename_sh_path))
