'''
Created on Jun 20, 2012

@author: michael
'''
from technology_type import technology_type

class nationwidechildrens_org_microsat_i(technology_type):
    '''
    the micro satellite technology type
    '''

    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        technology_type.__init__(self, config, platformID)
        self.configuration.update(config.items('nationwidechildrens_org_microsat_i'))
        self.tokenFeature2Index = int(self.configuration['token_feature_2_index'])

    def _checkLevel(self,tokens):
        if ( tokens[self.iLevel1].lower() != "level 1" ):
            if ( tokens[self.iLevel1] != "->" ):
                mess =  '(c) bad token ??? should say Level 1 ??? ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iLevel3, tokens[self.iLevel3]
            if ( tokens[self.iFilename] != "->" ):
                mess = '(d) bad token ??? should say Level 1 ??? ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iLevel3, tokens[self.iLevel3]
            return (False, mess)
        return (True, '')
    
    def getNumGenes(self):
        return 1
           
    def _readDataDetails(self, info, tokens, geneList, dataMatrix, sampleIndex):
        featName = self.dType + ':' + self.fType + ':' + tokens[self.tokenFeature2Index] + ':::::'
        geneList += [featName]
        dataMatrix[self.curGeneCount][sampleIndex] = tokens[self.tokenDatumIndex]
        self.curGeneCount += 1
        return True
    

