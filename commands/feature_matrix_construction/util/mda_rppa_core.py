'''
Created on Jun 20, 2012

@author: michael
'''
import miscTCGA
from technology_type import technology_type

class mdanderson_org_mda_rppa_core(technology_type):
    '''
    base class for MDA RPPA technology
    '''

    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        technology_type.__init__(self, config, platformID)
        self.createGeneList = True
        self.configuration.update(config.items('mdanderson_org_mda_rppa_core'))

    def includeFile(self, tokens):
        if ( miscTCGA.looks_like_uuid(tokens[self.iBarcode]) ):
            tokens[self.iBarcode] = miscTCGA.uuid_to_barcode(tokens[self.iBarcode])
        elif ( not tokens[self.iBarcode].startswith("Control") ):
            print " ERROR in handling RPPA data ??? this field in the SDRF should be a UUID ??? <%s> " % tokens[self.iBarcode]
            mess = '(f) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iOther, tokens[self.iOther]
            return (None, None, None, None, False, mess)

        if not tokens[self.iBarcode].startswith("TCGA-"):
            mess = '(e) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iOther, tokens[self.iOther]
            return (None, None, None, None, False, mess)
        return technology_type.includeFile(self, tokens)

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def genesMatchup(self):
        return False
           
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _addGeneName(self, tokens):
        ## start out with LOTS of sanity checking of these input values ...
        fType, fName = self._validateFeatureParts(self.dType, self.fType, tokens[0])
    
        ## create the feature name
        if not self.genename2geneinfo.get(tokens[1]):
            featureName = self.dType + ":" + fType + ":" + fName + ":::::" + tokens[1]
            self.genename2geneinfo[tokens[1]] = featureName

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def postprocess(self, dataMatrix, geneList, sampleList):
        # trim the data matrix to the actual found genes
        dataMatrix = dataMatrix[0:len(geneList)]
        return technology_type.postprocess(self, dataMatrix, geneList, sampleList)
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _readDataDetails(self, info, tokens, geneList, dataMatrix, sampleIndex):
        if self.createGeneList:
            gene = self.genename2geneinfo[tokens[self.tokenGeneIndex]]
            geneList += [gene]
            self.myGeneList += [gene]
            try:
                self._readDatumDetails(info, tokens, dataMatrix, sampleIndex)
            except Exception as e:
                self.readNullValue(tokens, dataMatrix, sampleIndex, e)
            self.curGeneCount += 1
        else:
            if self.genename2geneinfo.get(tokens[self.tokenGeneIndex]):
                technology_type._readDataDetails(self, info, tokens, geneList, dataMatrix, sampleIndex)
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def postReadFile(self):
        self.createGeneList = False
