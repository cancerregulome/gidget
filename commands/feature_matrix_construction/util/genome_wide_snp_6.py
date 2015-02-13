'''
Created on Jun 20, 2012

@author: michael
'''
from technology_type import technology_type
from datetime import datetime
import miscTCGA
import resegment

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# from Timo's resegmentation code:

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


## 16-aug: the newest '2003' mage-tab files seem to be different ...
## these exist as of now for brca, cesc and dlbc ... all other tumor types have '2002'
##    #66 should be the file ending in .hg18.seg.txt
##  and #75 should be the file ending in .hg19.seg.txt
##  and #84 should be the file ending in .nocnv_hg18.seg.txt
##  and #93 should be the file ending in .nocnv_hg19.seg.txt

## ( all of these indices used to be 67, 76, etc )
class genome_wide_snp_6(technology_type):
    '''
    classdocs
    '''
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        technology_type.__init__(self, config, platformID)
        self.configuration.update(config.items('genome_wide_snp_6'))
        self.translate = dict([[cn for cn in x.split(':')] for x in self.configuration['chr_translate'].split(',')])
        self.stripPrefixes = self.configuration['chr_strip_prefixes'].split(',')
        self.chr2data = {}
        self.chr2maxcoord = {}
        for index in range(1, 25):
            chrom = self._unifychr(str(index))
            self.chr2data[chrom] = AutoVivification()
            self.chr2maxcoord[chrom] = 0
        resegment.NA_VALUE = int(self.configuration['na_value'])
        resegment.NEAR_ZERO = float(self.configuration['near_zero'])

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def includeFile(self, tokens):
        retVal = technology_type.includeFile(self, tokens)
        ## for the SNP platform, we're only keeping tumor samples ...
        ## (which means they can be 01, 02, 06 ... I think anything that starts with a '0' basically)
        ## (yes, according to https://wiki.nci.nih.gov/display/TCGA/TCGA+barcode#TCGAbarcode-ReadingBarcodes --mm)
        if retVal[4] and  retVal[0][13] != "0":
            retVal = list(retVal)
            retVal[4] = False
            retVal[5] = '(e) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iYes, tokens[self.iYes], tokens[self.iOther]
        return tuple(retVal)
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def getNumGenes(self):
        return 0

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def readGeneList(self):
        self.genename2geneinfo = {}

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    #Unifies the naming convention for X and Y chromosomes, and removes possible 'hs' and 'chr' prefixes
    def _unifychr(self, chromName):
        for prefix in self.stripPrefixes:
            if str(chromName).startswith(prefix):
                chromName = chromName[len(prefix):]
        
        for translate in self.translate:
            if(chromName == translate):
                chromName = self.translate[translate]
        return chromName
    

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # this is Timo's resegmentation code(mostly) with numpy improvements by mm
    def _resegmentCNdata(self, sampleList, dataMatrix, steplength=1000, cutFrac=0.01, golemLabel=None, golemEmail=None):
        ## when we get to this point, we have:
        ## sampleList: list of sample barcodes, eg TCGA-74-6575-01A-11D-1842-01
        ## dataMatrix: will be the final output with the transposed contents of newMatrix
        ## steplength: bin size, eg 1000 bp
        ## cutFrac:    fraction to keep, eg 0.01
        start = datetime.now()
        print start, "in _resegmentCNdata() ... ", len(sampleList), steplength, cutFrac
        if ( 0 ):
            print sampleList[:5], sampleList[-5:]
            print self.chr2data['1'][0].keys()[0],'=',self.chr2data['1'][0][self.chr2data['1'][0].keys()[0]]
            print self.chr2data['1'][0].keys()[-1],'=',self.chr2data['1'][0][self.chr2data['1'][0].keys()[-1]]
            print self.chr2data['10'][0].keys()[0],'=',self.chr2data['10'][0][self.chr2data['10'][0].keys()[0]]
            print self.chr2data['10'][0].keys()[-1],'=',self.chr2data['10'][0][self.chr2data['10'][0].keys()[-1]]
            print self.chr2data['Y'][0].keys()[0],'=',self.chr2data['Y'][0][self.chr2data['Y'][0].keys()[0]]
            print self.chr2data['Y'][0].keys()[-1],'=',self.chr2data['Y'][0][self.chr2data['Y'][0].keys()[-1]]
        
        numSamples = len(sampleList)
        
        chrNames = [self._unifychr(str(x)) for x in range(1, 25)]
        chr2data = dict([pair for pair in self.chr2data.iteritems()])
        self.chr2data = None
        chr2maxcoord = dict([pair for pair in self.chr2maxcoord.iteritems()])
        self.chr2maxcoord = None
        segList, barcodeList, newMatrix = resegment._resegmentChromosomes(chrNames, chr2data, chr2maxcoord, sampleList, \
                                              steplength, cutFrac)
        ## now we flip the 'newMatrix' and return it as the output 'dataMatrix'
        numSeg = len(newMatrix[0])
        dataMatrix = [0] * numSeg
        numNA = 0
        for kS in range(numSeg):
            dataMatrix[kS] = [0] * numSamples
            for jS in range(numSamples):
                dataMatrix[kS][jS] = newMatrix[jS][kS]
                if(abs(dataMatrix[kS][jS]) > abs(resegment.NA_VALUE/2)):
                    ## print kS, jS, dataMatrix[kS][jS]
                    numNA += 1
    
        print "number of NA samples found while flipping : %i\n" % numNA
    
        ## take a look at the barcodes ... tumor only? mix?
        miscTCGA.lookAtBarcodes(barcodeList)
        end = datetime.now()
        print end, end - start, "RETURNING from resegmentCNdata() ...\n"
        return([seg for seg in segList], barcodeList, dataMatrix)

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _readDatumDetails(self, info, tokens, dataMatrix, sampleIndex):

        ## print " in _readDatumDetails ... ", tokens

        aChr = self._unifychr(tokens[1])
        ## print " aChr : ", aChr
        try:
            iStart = int(tokens[2])
            ## print " (a) iStart : ", iStart
        except:
            try:
                iStart = int(float(tokens[2]))
                ## print " (b) iStart : ", iStart
            except Exception as e:
                raise ValueError("FATAL ERROR: failed to parse segment stop position from <%s> " % tokens[3], e)
        try:
            iStop = int(tokens[3])
            ## print " (c) iStop : ", iStop
        except:
            try:
                iStop = int(float(tokens[3]))
                ## print " (d) iStop : ", iStop
            except Exception as e:
                raise ValueError("FATAL ERROR: failed to parse segment stop position from <%s> " % tokens[3], e)

        self.chr2data[aChr][sampleIndex][iStart] = (iStop, float(tokens[self.tokenDatumIndex]))
        maxchrcoord = self.chr2maxcoord[aChr]
        steplength = int(self.configuration['steplength'])
        self.chr2maxcoord[aChr] = max(maxchrcoord, int(int(iStop)/steplength))
    
    def _readGeneDetails(self, tokens, geneList):
        pass
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def postprocess(self, dataMatrix, geneList, sampleList):
        (segList, sampleList, dataMatrix) = self._resegmentCNdata(sampleList, dataMatrix, int(self.configuration.get('steplength')), \
                                    float(self.configuration.get('cutfrac')), self.configuration.get('golemlabel'), self.configuration.get('golememail'))
        dataD = {}
        dataD['rowLabels'] = segList
        dataD['colLabels'] = sampleList
        dataD['dataMatrix'] = dataMatrix
        dataD['dataType'] = "%s:%s" % (self.dType, self.fType)
        dataD['sortRowFlag'] = int(self.configuration['sort_row_flag'])
        dataD['sortColFlag'] = int(self.configuration['sort_col_flag'])
        print 'postprocess(): dataType: %s:%s sortRow: %s sortCol %s \nsegList %s %s \nsample list %s %s' \
            % (self.dType, self.fType, self.configuration['sort_row_flag'], self.configuration['sort_col_flag'], str(segList[:4]), str(segList[-4:]), str(sampleList[:4]), str(sampleList[-4:]))
        return dataD
    
## 16-aug: the newest '2003' mage-tab files seem to be different ...
## these exist as of now for brca, cesc and dlbc ... all other tumor types have '2002'
##    #66 should be the file ending in .hg18.seg.txt
##  and #75 should be the file ending in .hg19.seg.txt
##  and #84 should be the file ending in .nocnv_hg18.seg.txt
##  and #93 should be the file ending in .nocnv_hg19.seg.txt

## ( all of these indices used to be 67, 76, etc )
class broad_mit_edu_genome_wide_snp_6(genome_wide_snp_6):
    '''
    classdocs
    '''
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        genome_wide_snp_6.__init__(self, config, platformID)
        self.configuration.update(config.items('broad_mit_edu_genome_wide_snp_6'))

class genome_wustl_edu_genome_wide_snp_6(genome_wide_snp_6):
    '''
    classdocs
    '''
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        genome_wide_snp_6.__init__(self, config, platformID)
        self.configuration.update(config.items('genome_wustl_edu_genome_wide_snp_6'))
