import xml.sax

class tandem_out_parser(xml.sax.ContentHandler):
    element_array = []
    is_spectrum_query = False
    is_search_hit = False
    PSM = dict()
    search_hit = dict()
    spectrum_id = ''

    def startElement(self,name,attr):
        self.element_array.append(name)

        if( len(self.element_array) == 2 and name == 'group' and attr.has_key('id') ):
            self.is_spectrum_query = True
            self.spectrum_id = int(attr['id'])

            if( not self.PSM.has_key(self.spectrum_id) ):
                self.PSM[self.spectrum_id] = dict()
                self.PSM[self.spectrum_id]['search_hit'] = []
            else:
                sys.stderr.write("Duplicate PSM : %s\n"%self.spectrum_id)
            self.PSM[self.spectrum_id]['charge'] = int(attr['z'])
            self.PSM[self.spectrum_id]['precursor_mass'] = float(attr['mh'])

        if( len(self.element_array) == 3 and name == 'protein' ):
            self.is_search_hit = True
            self.search_hit = dict()
            self.search_hit['protein'] = attr['label']

        if( len(self.element_array) == 5 and name == 'domain' ):
            self.search_hit['expect'] = float(attr['expect'])
            self.search_hit['massdiff'] = float(attr['delta'])
            self.search_hit['missed_cleavages'] = int(attr['missed_cleavages'])
            self.search_hit['peptide'] = attr['seq']
            self.search_hit['hyperscore'] = float(attr['hyperscore'])

    def endElement(self,name):
        if( len(self.element_array) == 2 and name == 'group' ):
            self.spectrum_id = ''
            self.is_spectrum_query = False
        if( len(self.element_array) == 3 and name == 'protein' ):
            self.PSM[self.spectrum_id]['search_hit'].append(self.search_hit)
            self.search_hit = dict()
            self.is_search_hit = False
        self.element_array.pop()
    
def parse_by_filename(filename_tandem_out):
    p = tandem_out_parser()
    xml.sax.parse(filename_tandem_out,p)
    return p.PSM
