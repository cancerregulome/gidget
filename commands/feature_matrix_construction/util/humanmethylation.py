'''
Created on Jun 21, 2012

@author: michael
'''
import traceback

from gidget_util import gidgetConfigVars
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

class methylation_firehose(technology_type):
    '''
    the firehose parser for humanmethylation technology type
    '''
    def getMetaDataInfo(self, metaFilename):
        metaData = {}
        with open(metaFilename) as fh:
            for aLine in fh:
                aLine = aLine.strip()
                tokenList = aLine.split('\t')
                probeID = tokenList[0]
                featName = tokenList[1]
                metaData[probeID] = featName
    
        return metaData

    # -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

    def getFeatureName(self, aList):
        if not aList[0] in self.metaData:
            # print " SKIPPING !!! "
            return None

        return self.metaData[aList[0]]

    def parseDataFiles(self, config, fName, outdir):
        # --------------------------------------
        # figure out the name of the output file based on the name of the input file
        # SKCM.methylation__humanmethylation450__jhu_usc_edu__Level_3__within_bioassay_data_set_function__data.data.txt
        if (fName.find("humanmethylation450") > 0):
            outFile = outdir + config['zCancer'] + ".jhu-usc.edu__humanmethylation450__methylation." + \
                config['suffixString'] + ".tsv"
            try:
                print " opening output file : ", outFile
                fhOut = open(outFile, 'w')
                platformName = "HumanMethylation450"
                numCol = 4
                iCol = 1
            except:
                print " ERROR ??? failed to open output file ??? "
                print outFile
                sys.exit(-1)

        elif (fName.find("humanmethylation27") > 0):
            outFile = config['zCancer'] + ".jhu-usc.edu__humanmethylation27__methylation." + \
                config['suffixString'] + ".tsv"
            try:
                print " opening output file : ", outFile
                fhOut = open(outFile, 'w')
                platformName = "HumanMethylation27"
                numCol = 4
                iCol = 1
            except:
                print " ERROR ??? failed to open output file ??? "
                print outFile
                sys.exit(-1)

        else:
            print " new data type ??? "
            print fName
            sys.exit(-1)

        # --------------------------------------
        # do we need some metadata?
        self.metaData = self.getMetaDataInfo(gidgetConfigVars['TCGAFMP_FIREHOSE_MIRROR'] + "/metadata/meth.probes.15oct13.txt")

        # --------------------------------------
        # ok, time to parse the input file and write the
        # output file
        self.parseFirehoseFile(fName, fhOut, iCol, numCol, platformName, "N:METH", "C:SAMP:methPlatform")

        fhOut.close()