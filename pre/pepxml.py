import xml.sax

class pepxml_parser(xml.sax.ContentHandler):
    element_array = []
    is_spectrum_query = False
    is_search_hit = False
    PSM = dict()
    search_hit = dict()
    spectrum_id = ''

    def startElement(self,name,attr):
        self.element_array.append(name)
        if( len(self.element_array) == 3 and name == 'spectrum_query' ):
            self.is_spectrum_query = True
            sp_tokens = attr['spectrum'].split('.')
            self.spectrum_id = '%s.%05d.%05d.%d'%(sp_tokens[0],int(sp_tokens[1]),int(sp_tokens[2]),int(sp_tokens[3]))
            if( not self.PSM.has_key(self.spectrum_id) ):
                self.PSM[self.spectrum_id] = dict()
                self.PSM[self.spectrum_id]['search_hit'] = []
            else:
                print "Duplicate PSM : %s"%self.spectrum_id
            self.PSM[self.spectrum_id]['charge'] = int(attr['assumed_charge'])
            self.PSM[self.spectrum_id]['precursor_mz'] = float(attr['precursor_neutral_mass'])/self.PSM[self.spectrum_id]['charge']
        if( len(self.element_array) == 5 and name == 'search_hit' ):
            self.is_search_hit = True
            self.search_hit = dict()
            self.search_hit['hit_rank'] = int(attr['hit_rank'])
            self.search_hit['peptide'] = attr['peptide']
            self.search_hit['protein'] = attr['protein']
            self.search_hit['protein_descr'] = ''
            if( attr.has_key('protein_descr') ):
                self.search_hit['protein_descr'] = attr['protein_descr']
            self.search_hit['missed_cleavages'] = -1
            if( attr.has_key('num_missed_cleavages') ):
                self.search_hit['missed_cleavages'] = int(attr['num_missed_cleavages'])
            self.search_hit['massdiff'] = -1.0
            if( attr.has_key('massdiff') ):
                self.search_hit['massdiff'] = float(attr['massdiff'])
        if( len(self.element_array) == 6 and name == 'search_score' ):
            ## SEQUEST
            if(attr['name'] == 'xcorr'):
                self.search_hit['xcorr'] = float(attr['value'])
            if(attr['name'] == 'spscore'):
                self.search_hit['spscore'] = float(attr['value'])
            if(attr['name'] == 'deltacn'):
                self.search_hit['deltacn'] = float(attr['value'])
            ## X!Tandem
            if(attr['name'] == 'hyperscore'):
                self.search_hit['hyperscore'] = float(attr['value'])
            if(attr['name'] == 'expect'):
                self.search_hit['expect'] = float(attr['value'])
            ## OMSSA
            if(attr['name'] == 'pvalue'):
                self.search_hit['pvalue'] = float(attr['value'])
            if(attr['name'] == 'expect'):
                self.search_hit['expect'] = float(attr['value'])
            ## InsPecT
            if(attr['name'] == 'mqscore'):
                self.search_hit['mqscore'] = float(attr['value'])
            if(attr['name'] == 'expect'):
                self.search_hit['expect'] = float(attr['value'])
            if(attr['name'] == 'fscore'):
                self.search_hit['fscore'] = float(attr['value'])
            if(attr['name'] == 'deltascore'):
                self.search_hit['deltascore'] = float(attr['value'])
            ## MyriMatch
            if(attr['name'] == 'mvh'):
                self.search_hit['mvh'] = float(attr['value'])
            if(attr['name'] == 'massError'):
                self.search_hit['massError'] = float(attr['value'])
            if(attr['name'] == 'mzSSE'):
                self.search_hit['mzSSE'] = float(attr['value'])
            if(attr['name'] == 'mzFidelity'):
                self.search_hit['mzFidelity'] = float(attr['value'])
            if(attr['name'] == 'newMZFidelity'):
                self.search_hit['newMZFidelity'] = float(attr['value'])
            if(attr['name'] == 'mzMAE'):
                self.search_hit['mzMAE'] = float(attr['value'])
            ## DirecTag-TagRecon
            if(attr['name'] == 'numPTMs'):
                self.search_hit['numPTMs'] = int(attr['value'])
        ## PeptideProphet
        if( len(self.element_array) == 7 and name == 'peptideprophet_result' ):
            self.search_hit['TPP_pep_prob'] = float(attr['probability'])

    def endElement(self,name):
        if( len(self.element_array) == 3 and name == 'spectrum_query' ):
            self.spectrum_id = ''
            self.is_spectrum_query = False
        if( len(self.element_array) == 5 and name == 'search_hit' ):
            self.PSM[self.spectrum_id]['search_hit'].append(self.search_hit)
            self.search_hit = dict()
            self.is_search_hit = False
        self.element_array.pop()
    
def parse_by_filename(filename_pepxml):
    p = pepxml_parser()
    xml.sax.parse(filename_pepxml,p)
    return p.PSM
