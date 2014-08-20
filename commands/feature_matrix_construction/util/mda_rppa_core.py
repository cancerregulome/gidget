'''
Created on Jun 20, 2012

@author: michael
'''
from gidget_util import gidgetConfigVars
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
                featureName = self.dType + ":" + fType + ":" + self._cleanString(gene) + ":::::" + tokens[-1]
                names = self.genename2geneinfo.setdefault(tokens[-1], [])
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
            seen_abs = self.gene2ab.setdefault(gene, set())
            if 0 < len(seen_abs) and ab not in seen_abs:
                seen_abs.add(ab)
                raise ValueError("more than one antibody associated with %s: %s" % (gene, seen_abs))
            seen_abs.add(ab)
            
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

class rppa_firehose(technology_type):
    '''
    the firehose parser for RPPA technology type
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.geneAntibodyMap = None

    def getGeneAntibodyMap(self):
    
        geneAntibodyMap = {}
    
        fh = file( gidgetConfigVars['TCGAFMP_BIOINFORMATICS_REFERENCES'] + "/tcga_platform_genelists/MDA_antibody_annotation_2014_03_04.txt" )
        for aLine in fh:
            aLine = aLine.strip()
            tokenList = aLine.split('\t')
            token0 = tokenList[0].strip()
            token1 = tokenList[1].strip()
    
            if (token0 != "Gene Name"):
                geneAntibodyMap[token1] = token0
    
        fh.close()
        return (geneAntibodyMap)

    def getFeatureName(self, aList):
        try:
            geneName = self.geneAntibodyMap[aList[0]]
        except:
            print " ERROR ??? could not get antibody <%s> to gene mapping ??? " % aList[0]
            sys.exit(-1)
        return "N:RPPA:" + geneName + ":::::" + aList[0]
    
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# for the RPPA data we could either grab data form
# gdac.broadinstitute.org_THCA-TP.RPPA_AnnotateWithGene.Level_3.2013071400.0.0
# where the file is called THCA-TP.rppa.txt and has row labels like
# EIF4EBP1|4E-BP1_pT70
# TP53BP1|53BP1
# ARAF|A-Raf_pS299
# ACACA|ACC1
# ACACA ACACB|ACC_pS79

# or
# gdac.broadinstitute.org_THCA-TP.Merge_protein_exp__mda_rppa_core__mdanderson_org__Level_3__protein_normalization__data.Level_3.2013071400.0.0
# where the file is called THCA-TP.protein_exp__mda_rppa_core__mdanderson_org__Level_3__protein_normalization__data.data.txt
# and the row labels are like
# 14-3-3_epsilon
# 4E-BP1
# 4E-BP1_pS65
# 4E-BP1_pT37_T46
# 53BP1
# ACC_pS79
# ACC1
# Akt

# the problem is that in both of these files, apparently it is ok for the barcode
# to end in -TP rather than -01 (at least that is what I am seeing in the THCA run
# from July but not from the SKCM run in October)


    def parseDataFiles(self, config, fName, outdir):
        # --------------------------------------
        # figure out the name of the output file based on the name of the input file
        # SKCM.mirnaseq__illuminahiseq_mirnaseq__bcgsc_ca__Level_3__miR_gene_expression__data.data.txt
        if (fName.find("protein_exp__mda_rppa_core") > 0):
            outFile = outdir + config['zCancer'] + ".mdanderson.org__mda_rppa_core__protein_exp." + \
                config['suffixString'] + ".tsv"
            try:
                print " opening output file : ", outFile
                fhOut = file(outFile, 'w')
                platformName = "MDA_RPPA_Core"
                numCol = 1
                iCol = 1
            except:
                print " ERROR ??? failed to open output file ??? "
                print outFile
                sys.exit(-1)
        else:
            print " new data type ??? "
            print fName
            sys.exit(-1)

        self.geneAntibodyMap = self.getGeneAntibodyMap()
        # --------------------------------------
        # ok, time to parse the input file and write the
        # output file
        print " >>> ready to parse input file and write output file "
        print " >>> %s " % fName
        self.parseFirehoseFile(fName, fhOut, iCol, numCol, platformName, "N:RPPA", "C:SAMP:rppaPlatform", True, config['zCancer'])
        fhOut.close()
