import xml.sax

class pepxml_parser(xml.sax.ContentHandler):
    element_array = []
    is_spectrum_query = False
    is_search_hit = False
    PSM = dict()
    search_hit = dict()
    spectrum_id = ''
    #print 2

    def startElement(self,name,attr):
        self.element_array.append(name)
        #if( len(self.element_array) == 3 and name == 'spectrum_query' ):
        if( len(self.element_array) == 2 and name == 'spectrum_query' ):
            #print 'query'
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
        #if( len(self.element_array) == 5 and name == 'search_hit' ):
        if( len(self.element_array) == 4 and name == 'search_hit' ):
            #print 'search hit'
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
                if attr['num_missed_cleavages'] <> '':
                    self.search_hit['missed_cleavages'] = int(attr['num_missed_cleavages'])
            self.search_hit['massdiff'] = -1.0
            if( attr.has_key('massdiff') ):
                self.search_hit['massdiff'] = float(attr['massdiff'])
        #if( len(self.element_array) == 6 and name == 'search_score' ):
        if( len(self.element_array) == 5 and name == 'search_score' ):
            #print 'search_score'
            ## SEQUEST
            if(attr.items()[0][0] == 'xcorr'):
                self.search_hit['xcorr'] = float(attr.items()[0][1])
            #if(attr.items()[0][0] == 'spscore'):
            #    self.search_hit['spscore'] = float(attr.items()[0][1])
            if(attr.items()[0][0] == 'deltacn'):
                self.search_hit['deltacn'] = float(attr.items()[0][1])
            ## Crux
            if(attr.items()[0][0] == 'xcorr_score'):
                self.search_hit['xcorr'] = float(attr.items()[0][1])
            if(attr.items()[0][0] == 'delta_cn'):
                self.search_hit['deltacn'] = float(attr.items()[0][1])
            ## X!Tandem
            if(attr.items()[0][0] == 'hyperscore'):
                self.search_hit['hyperscore'] = float(attr.items()[0][1])
            if(attr.items()[0][0] == 'expect'):
                self.search_hit['expect'] = float(attr.items()[0][1])
            ## OMSSA
            if(attr.items()[0][0] == 'pvalue'):
                self.search_hit['pvalue'] = float(attr.items()[0][1])
            if(attr.items()[0][0] == 'expect'):
                self.search_hit['expect'] = float(attr.items()[0][1])
            ## InsPecT
            if(attr.items()[0][0] == 'mqscore'):
                self.search_hit['mqscore'] = float(attr.items()[0][1])
            if(attr.items()[0][0] == 'expect'):
                self.search_hit['expect'] = float(attr.items()[0][1])
            if(attr.items()[0][0] == 'fscore'):
                self.search_hit['fscore'] = float(attr.items()[0][1])
            if(attr.items()[0][0] == 'deltascore'):
                self.search_hit['deltascore'] = float(attr.items()[0][1])
            ## MyriMatch
            if(attr.items()[0][0] == 'mvh'):
                self.search_hit['mvh'] = float(attr.items()[0][1])
            if(attr.items()[0][0] == 'massError'):
                self.search_hit['massError'] = float(attr.items()[0][1])
            if(attr.items()[0][0] == 'mzSSE'):
                self.search_hit['mzSSE'] = float(attr.items()[0][1])
            if(attr.items()[0][0] == 'mzFidelity'):
                self.search_hit['mzFidelity'] = float(attr.items()[0][1])
            if(attr.items()[0][0] == 'newMZFidelity'):
                self.search_hit['newMZFidelity'] = float(attr.items()[0][1])
            if(attr.items()[0][0] == 'mzMAE'):
                self.search_hit['mzMAE'] = float(attr.items()[0][1])
            ## DirecTag-TagRecon
            if(attr.items()[0][0] == 'numPTMs'):
                self.search_hit['numPTMs'] = int(attr.items()[0][1])
        ## PeptideProphet
        if( len(self.element_array) == 6 and name == 'peptideprophet_result' ):
            self.search_hit['TPP_pep_prob'] = float(attr['probability'])

    def endElement(self,name):
        #if( len(self.element_array) == 3 and name == 'spectrum_query' ):
        if( len(self.element_array) == 2 and name == 'spectrum_query' ):
            self.spectrum_id = ''
            self.is_spectrum_query = False
            #print "query end"
        #if( len(self.element_array) == 5 and name == 'search_hit' ):
        if( len(self.element_array) == 4 and name == 'search_hit' ):
            self.PSM[self.spectrum_id]['search_hit'].append(self.search_hit)
            self.search_hit = dict()
            self.is_search_hit = False
            #print "hit end"
        self.element_array.pop()
    
def parse_by_filename(filename_pepxml):
    p = pepxml_parser()
    xml.sax.parse(filename_pepxml,p)
    #print 1
    return p.PSM
