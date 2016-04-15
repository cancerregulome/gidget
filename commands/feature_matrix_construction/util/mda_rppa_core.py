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
        self.configuration.update(config.items('mdanderson_org_mda_rppa_core'))
        self.fname2row = {}
        self.topRowIndex = 0
        self.gene2ab = {}

    def includeFile(self, tokens):
        barcode = tokens[self.iBarcode]
        if ( miscTCGA.looks_like_uuid(tokens[self.iBarcode]) ):
            barcode = miscTCGA.uuid_to_barcode(tokens[self.iBarcode])
        elif ( not tokens[self.iBarcode].startswith("Control") ):
            print " ERROR in handling RPPA data ??? this field in the SDRF should be a UUID ??? <%s> " % tokens[self.iBarcode]
            mess = '(f) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iOther, tokens[self.iOther]
            return (None, None, None, None, False, mess)

        if not barcode.startswith("TCGA-"):
            mess = '(e) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iOther, tokens[self.iOther]
            return (None, None, None, None, False, mess)
        return technology_type.includeFile(self, tokens)

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def genesMatchup(self):
        return False
           
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _addGeneName(self, tokens):

        ## start out with LOTS of sanity checking of these input values ...
        ## if the first token is actually a list of gene symbols, we will
        ## take only the first one ...
        genes = tokens[0].split()
        fType, fName = self._validateFeatureParts(self.dType, self.fType, genes[0])
        
        if not self.genename2geneinfo.get(tokens[-1]):
            ## the gene names are the first part of the list, create a feature for each one
            for gene in genes:

                ## potentially clean up the tokens[-1] value ...
                antibodyToken = tokens[-1]
                if ( antibodyToken.endswith("-G-C") ): antibodyToken = antibodyToken[:-4]
                if ( antibodyToken.endswith("-G-V") ): antibodyToken = antibodyToken[:-4]
                if ( antibodyToken.endswith("-M-C") ): antibodyToken = antibodyToken[:-4]
                if ( antibodyToken.endswith("-M-E") ): antibodyToken = antibodyToken[:-4]
                if ( antibodyToken.endswith("-M-V") ): antibodyToken = antibodyToken[:-4]
                if ( antibodyToken.endswith("-R-C") ): antibodyToken = antibodyToken[:-4]
                if ( antibodyToken.endswith("-R-E") ): antibodyToken = antibodyToken[:-4]
                if ( antibodyToken.endswith("-R-NA") ): antibodyToken = antibodyToken[:-5]
                if ( antibodyToken.endswith("-R-V") ): antibodyToken = antibodyToken[:-4]

                featureName = self.dType + ":" + fType + ":" + self._cleanString(gene) + ":::::" + antibodyToken
                names = self.genename2geneinfo.setdefault(tokens[-1], [])
                ## names = self.genename2geneinfo.setdefault(antibodyToken, [])
                names += [featureName]

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def postprocess(self, dataMatrix, geneList, sampleList):
        # trim the data matrix to the actual found genes
        print 'total genes: %i mapped genes: %i' % (len(self.genename2geneinfo), len(self.fname2row))
        dataMatrix = dataMatrix[0:self.topRowIndex]
        # fill in NA for where the gene wasn't used
        for row in range(len(dataMatrix)):
            for col in range(len(dataMatrix[row])):
                if '' == dataMatrix[row][col]:
                    dataMatrix[row][col] = self.NA_VALUE
        # and return the genelist with the complete set of genes from all archives
        # in the order that they appeared
        return technology_type.postprocess(self, dataMatrix, self.myGeneList, sampleList)
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def readNullValue(self, tokens, dataMatrix, sampleIndex, e):
        raise NotImplementedError('readNullValue not implemented for this subclass')

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _readDatumDetails(self, info, tokens, dataMatrix, sampleIndex):
        raise NotImplementedError('_readDatumDetails not implemented for this subclass')
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _readGeneDetails(self, tokens, geneList):
        raise NotImplementedError('_readDatumDetails not implemented for this subclass')
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # do not call _readGeneDetails(), _readDatumDetails() or readNullValue(),  
    # have all the necessary details to decide what row to actually write to
    def _readDataDetails(self, info, tokens, geneList, dataMatrix, sampleIndex):
        ab = tokens[self.tokenGeneIndex]
        genes = self.genename2geneinfo[ab]
        for gene in genes:

            # verify the gene is only associated with one antibody
            # does this have to be an error ??? DO NOT CHECK THIS IN BEFORE MORE TESTING !!!
            seen_abs = self.gene2ab.setdefault(gene, set())
            if ab not in seen_abs:
                seen_abs.add(ab)
            if 1 < len(seen_abs):
                #### raise ValueError("more than one antibody associated with %s: %s" % (gene, seen_abs))
                print " WARNING ... more than one antibody associated with a gene ??? %s %s " % ( gene, seen_abs )
            
            # add the gene to the feature matrix if we haven't seen it already
            if not self.fname2row.has_key(gene):
                geneList += [gene]
                self.myGeneList += [gene]
                self.fname2row[gene] = self.topRowIndex
                self.topRowIndex += 1
            row = self.fname2row[gene]
            self.curGeneCount += 1
            try:
                dataMatrix[row][sampleIndex] = float(tokens[self.tokenDatumIndex])
            except Exception as e:
                if (len(tokens) == 1 or tokens[1] == 'null' or tokens[1] == 'NA'):
                    dataMatrix[row][sampleIndex] = self.NA_VALUE
                else:
                    raise ValueError('ERROR converting token to float ??? %s: token length: %i tokens: %s', (str(self), len(tokens), tokens), e)
