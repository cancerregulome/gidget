'''
Created on Jun 21, 2012

@author: michael
'''
import traceback

from technology_type import technology_type

class humanmethylation(technology_type):
    '''
    classdocs
    '''
    createGeneList = True
    
    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        technology_type.__init__(self, config, platformID)
        self.configuration.update(config.items('humanmethylation'))

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def genesMatchup(self):
        return False
           
    def _addGeneName(self, tokens):
        try:
            fields = tokens[0].split(':')
            geneName = fields[2]
            chrName = fields[3][3:]
            chrPos = fields[4]
            lastToken = fields[7]
            lastSplit = lastToken.split('_')
            probeID = lastSplit[0]
            featureName = self._makeFeatureName(self.dType, self.fType, geneName, chrName, int(chrPos), xName = lastToken)
            self.genename2geneinfo[probeID] = featureName
        except:
            print 'problem setting gene name: %s' % tokens[0]

    def _readDatumDetails(self, info, tokens, dataMatrix, sampleIndex):
        if ( len(tokens) != 3 and len(tokens) != 5):
            mess = "ERROR in parsing Methylation data: unknown token count: %i tokens: %s ??? " (len(tokens), str(tokens))
            raise ValueError(mess)
        technology_type._readDatumDetails(self, info, tokens, dataMatrix, sampleIndex)

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def postprocess(self, dataMatrix, geneList, sampleList):
        # trim the data matrix to the actual found genes
        dataMatrix = dataMatrix[0:len(geneList)]
        return technology_type.postprocess(self, dataMatrix, geneList, sampleList)
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _readDataDetails(self, info, tokens, geneList, dataMatrix, sampleIndex):
        if self.createGeneList:
            try:
                # TODO: see if using get rather than exception is faster
                gene = self.genename2geneinfo[tokens[self.tokenGeneIndex]]
                geneList += [gene]
                self.myGeneList += [gene]
                try:
                    self._readDatumDetails(info, tokens, dataMatrix, sampleIndex)
                except Exception as e:
                    self.readNullValue(tokens, dataMatrix, sampleIndex, e)
                self.curGeneCount += 1
            except:
                # current gene not on list
                return
        else:
            if self.genename2geneinfo.get(tokens[self.tokenGeneIndex]):
                technology_type._readDataDetails(self, info, tokens, geneList, dataMatrix, sampleIndex)
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def postReadFile(self):
        self.createGeneList = False
    
class jhu_usc_edu_humanmethylation27(humanmethylation):
    '''
    the humanmethylation27 technology type
    '''

    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        humanmethylation.__init__(self, config, platformID)
        self.configuration.update(config.items('jhu_usc_edu_humanmethylation27'))

    def setConfiguration(self, hdrTokens):
        print 'jhu_usc_edu_humanmethylation27.setConfiguration(): %s' % hdrTokens
        numTokens = len(hdrTokens)
        if int(self.configuration['tokenindex0']) == numTokens:
            index = 0
        elif int(self.configuration['tokenindices12']) == numTokens:
            ## looks like the new data has 33 tokens, and the indices should be 30, 1, 27, 28, 31, 29
            ## whereas before that there were also 33 tokens, but the indices are: 29, 0, 28, 32, 31, 30
            if ('Protocol REF' in hdrTokens[1]):
                index = 1
            elif ('TCGA Barcode' in hdrTokens[1]):
                index = 2
            else:
                raise ValueError("ERROR parsing tokens for <%s> ??? " % self)
        elif int(self.configuration['tokenindex3']) == numTokens:
            if (hdrTokens[1].startswith("TCGA-")):
                index = 3
            else:
                raise ValueError("ERROR parsing tokens for <%s> ??? " % self)
        elif int(self.configuration['tokenindex4']) == numTokens:
            index = 4
        else:
            raise ValueError("unexpected number of tokens for jhu_usc_edu_humanmethylation27: " + str(numTokens))
        self.iLevel3 = int(self.configuration['ilevel3'].split(',')[index])
        self.iBarcode = int(self.configuration['ibarcode'].split(',')[index])
        self.iFilename = int(self.configuration['ifilename'].split(',')[index])
        self.iArchive = int(self.configuration['iarchive'].split(',')[index])
        self.iYes = int(self.configuration['iyes'].split(',')[index])
        self.iOther = int(self.configuration['iother'].split(',')[index])
        self.tokenGeneIndex = int(self.configuration['token_gene_index'])
        self.tokenDatumIndex = int(self.configuration['token_datum_index'])
        humanmethylation.setMiscConfig(self)

class jhu_usc_edu_humanmethylation450(humanmethylation):
    '''
    the humanmethylation450 technology type
    '''

    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        humanmethylation.__init__(self, config, platformID)
        self.configuration.update(config.items('jhu_usc_edu_humanmethylation450'))

    def setConfiguration(self, hdrTokens):
        numTokens = len(hdrTokens)
        if int(self.configuration['needed_num_tokens']) < numTokens:
            humanmethylation.setConfiguration(self, hdrTokens)
        else:
            raise ValueError("unexpected number of tokens for jhu_usc_edu_humanmethylation450: " + str(numTokens))
