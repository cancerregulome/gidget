'''
Created on Jun 18, 2012

@author: m.miller
'''
from datetime import datetime
import os

import miscTCGA
import path
import tsvIO

class technology_type(object):
    '''
    base class for technology subclasses to specialize
    '''
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    NA_VALUE = -999999

    iLevel1 = -1
    iLevel3 = -1
    iBarcode = -1
    iFilename = -1
    iArchive = -1
    iYes = -1
    iOther = -1
    
    tokenGeneIndex = -1
    tokenDatumIndex = -1
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        self.configuration = dict(config.items('technology_type'))
        self.platformID = platformID
        self.genename2geneinfo = {}
        self.myGeneList = []
        
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

    def _setColumnIndices(self, hdrTokens):
        iLevel1 = None
        if self.configuration.get('ilevel1'):
            iLevel1 = [int(index) for index in self.configuration['ilevel1'].split(',')]
        iLevel3 = [int(index) for index in self.configuration['ilevel3'].split(',')]
        iBarcode = [int(index) for index in self.configuration['ibarcode'].split(',')]
        iFilename = [int(index) for index in self.configuration['ifilename'].split(',')]
        iArchive = [int(index) for index in self.configuration['iarchive'].split(',')]
        iYes = [int(index) for index in self.configuration['iyes'].split(',')]
        iOther = [int(index) for index in self.configuration['iother'].split(',')]
        
        index = 0
        columnCount2index = dict([(int(count), i) for i, count in enumerate(self.configuration['token_index_column_count'].split(','))])
        for count, i in columnCount2index.iteritems():
            if 0 == i and -1 == count:
                # the default case
                continue
            if len(hdrTokens) == count:
                index = i
                break
        print '_setColumnIndices(): length of headers %i.  index set to %i' % (len(hdrTokens), index)
        if iLevel1:
            self.iLevel1 = iLevel1[index]
        self.iLevel3 = iLevel3[index]
        self.iBarcode = iBarcode[index]
        self.iFilename = iFilename[index]
        self.iArchive = iArchive[index]
        self.iYes = iYes[index]
        self.iOther = iOther[index]
        print '_setColumnIndices(): iLevel3 %i, iBarcode %i, iFilename %i, iArchive %i, iYes %i, iOther %i' % \
            (iLevel3[index], iBarcode[index], iFilename[index], iArchive[index], iYes[index], iOther[index])

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def setMiscConfig(self):
        self.tokenGeneIndex = int(self.configuration['token_gene_index'])
        self.tokenDatumIndex = int(self.configuration['token_datum_index'])
        self.dType = self.configuration['fm_data_type']
        self.fType = self.configuration['fm_feature_type']

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    jhu_usc_edu_humanmethylation27 (humanmethylation.py)
    #    jhu_usc_edu_humanmethylation450 (humanmethylation.py)
    def setConfiguration(self, hdrTokens):
        self._setColumnIndices(hdrTokens)
        self.setMiscConfig()
        
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    clinical (clinical.py)
    def getTopDirectory(self, tumorType):
        return self.configuration["topdir"] % (self.configuration['snapshot'], self.configuration['basedirectorybranch'], tumorType, self.platformID)
        
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def hasSDRFFile(self):
        if 'true' == self.configuration["hassdrf"]:
            return True
        return False
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def isBioAssayDataMatrix(self):
        if 'true' == self.configuration["matrix"]:
            return True
        return False
        
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # allows subclasses to look at the SDRFFile if additional info is needed before it is parsed
    # overridden by:
    #    bcgsc_ca_illuminaga_rnaseq (illumina_rnaseq.py)
    #    bcgsc_ca_illuminaga_mirnaseq (illumina_rnaseq.py)
    #    bcgsc_ca_illuminahiseq_mirnaseq (illumina_rnaseq.py)
    def preprocessSDRFFile(self, sdrfFilename):
        return

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    unc_edu_agilentg4502a_07 (agilentg4502a_07.py)
    def _checkForUUID(self, tokens):
        barcode = tokens[self.iBarcode]
        # typical full barcode looks like this:
        #      TCGA-A1-A0SE-01A-11R-A085-13
        # need 12 characters to identify patient
        #      16 characters to identify sample
        #      20 characters to identify aliquot
        #      25 characters to include plate id
        #      28 characters to include cgcc id
        # added some functionality to miscTCGA and this step here on 21jun2012 ...
        # and a typical UUID looks like this:
        #    6d41d8c9-f2bf-4440-8b8d-907e3b2682f5
        if (miscTCGA.looks_like_uuid(barcode)):
            barcode = miscTCGA.uuid_to_barcode(barcode)
            mess = ''
        else:
            found = False
            for i, token in enumerate(tokens):
                if miscTCGA.looks_like_uuid(token):
                    found = True
                    print 'found UUID column(%i): %s' % (i, token)
                    break
            mess = '(g) NOT including this file, not UUID ... ', found, self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iYes, tokens[self.iYes] # we want to always use the uuid now --mm 2014-01-29
    # if this fails to map the UUID to a barcode it will return "NA"
    # which will fail the next trap ...
        return mess, barcode

    def _checkBarcode(self, tokens):
        if (tokens[self.iYes].lower() == "yes"):
            mess, barcode = self._checkForUUID(tokens)
            if mess:
                return (tokens[self.iBarcode], None, None, None, False, mess)

            # adding this trap 03May2012 ...
            if (not barcode.startswith("TCGA-")):
                mess = '(a) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iYes, tokens[self.iYes]
                return (tokens[self.iBarcode], None, None, None, False, mess)

            if (len(barcode) > 28): 
                barcode = barcode[:28]
            filename = tokens[self.iFilename]
            if (self.iArchive >= 0):
                archive = tokens[self.iArchive]
            else:
                archive = "unknown"
            otherInfo = tokens[self.iOther]
            return (barcode, filename, archive, otherInfo, True, None)
        else:
            mess = '(b) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iYes, tokens[self.iYes]
            return (None, None, None, None, False, mess)
        
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    nationwidechildrens_org_microsat_i (microsat_i)
    def _checkLevel(self, tokens):
        if (tokens[self.iLevel3].lower() != "level 3"):
            mess = '(b) NOT including this file ...', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iLevel3, tokens[self.iLevel3]
            if (tokens[self.iLevel3] != "->"):
                mess = '(c) bad token ??? should say Level 3 ??? ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iLevel3, tokens[self.iLevel3]
            if (tokens[self.iFilename] != "->"):
                mess = '(d) bad token ??? should say Level 3 ??? ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iLevel3, tokens[self.iLevel3]
            return (False, mess)
        return (True, '')
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    bcgsc_ca_illuminaga_rnaseq (illumina_rnaseq.py)
    #    bcgsc_ca_illuminaga_mirnaseq (illumina_rnaseq.py)
    #    bcgsc_ca_illuminahiseq_mirnaseq (illumina_rnaseq.py)
    #    broad_mit_edu_genome_wide_snp_6 (genome_wide_snp_6.py)
    #    clinical (clinical.py)
    #    humanmethylation (humanmethylation.py)
    #    unc_edu_illuminaga_rnaseq (illumina_rnaseq.py)
    #    unc_edu_illuminaga_rnaseqv2 (illumina_rnaseq.py)
    #    unc_edu_illuminahiseq_rnaseq (illumina_rnaseq.py)
    #    unc_edu_illuminahiseq_rnaseqv2 (illumina_rnaseq.py)
    #    mdanderson_org_mda_rppa_core (mda_rppa_core.py)
    def includeFile(self, tokens):
        (includeFlag, message) = self._checkLevel(tokens)
        if not includeFlag:
            return (None, None, None, None, includeFlag, message)
        return self._checkBarcode(tokens)
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def getDirectoryLevel(self):
        return self.configuration.get('dirlevel')

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    bcgsc_ca_illuminaga_rnaseq (illumina_rnaseq.py)
    #    unc_edu_agilentg4502a_07 (agilentg4502a_07.py)
    #    humanmethylation (humanmethylation.py)
    #    unc_edu_illuminaga_rnaseq (illumina_rnaseq.py)
    #    unc_edu_illuminaga_rnaseqv2 (illumina_rnaseq.py)
    #    unc_edu_illuminahiseq_rnaseq (illumina_rnaseq.py)
    #    unc_edu_illuminahiseq_rnaseqv2 (illumina_rnaseq.py)
    #    mdanderson_org_mda_rppa_core (mda_rppa_core.py)
    def _addGeneName(self, tokens):
        featureName = self._makeFeatureName(self.dType, self.fType, tokens[0])
        self.genename2geneinfo[tokens[0]] = featureName
        self.myGeneList += [featureName]
        
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    bcgsc_ca_illuminaga_rnaseq (illumina_rnaseq.py)
    def _readPatternDesign(self):
        platformDesign = ''
        if self.configuration['platformdesign']:
            platformDesign = self.configuration['platformdesign']
            if '%s' in platformDesign:
                root_dir = self.configuration['root_dir']
                platformDesign = platformDesign % (root_dir)
        if 0 == len(self.genename2geneinfo) and platformDesign:
            print '\t', datetime.now(), 'reading gene list from %s' % platformDesign 
            with open(platformDesign) as patternFile:
                for line in patternFile:
                    tokens = line.strip().split('\t')
                    self._addGeneName(tokens)
            print '\t', datetime.now(), 'finished reading gene list.  found %i genes\n' % len(self.myGeneList)

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # allow subclasses to override 
    def switchingTopDir(self):
        pass 

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    mdanderson_org_mda_rppa_core (mda_rppa_core.py)
    #    humanmethylation (humanmethylation.py)
    def genesMatchup(self):
        return True
           
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    broad_mit_edu_genome_wide_snp_6 (genome_wide_snp_6.py)
    #    nationwidechildrens_org_microsat_i (microsat_i)
    def getNumGenes(self):
        self._readPatternDesign()
        return len(self.genename2geneinfo)
           
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def getNumSamples(self, filename2sampleInfo):
        return len(filename2sampleInfo)
            
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _cleanString_OLD(self, string):
        quoteIndex = string.find("'")
        if (quoteIndex >= 0):
            temp = string[:quoteIndex] + string[quoteIndex + 1:]
            # print " in _cleanString : <%s> <%s> " % ( string, temp )
            string = temp
    
        quoteIndex = string.find('"')
        if (quoteIndex >= 0):
            temp = string[:quoteIndex] + string[quoteIndex + 1:]
            # print " in _cleanString : <%s> <%s> " % ( string, temp )
            string = temp
    
        return string

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    
    def _removeParentheticalStuff(self, aString):
    
        # print " in removeParentheticalStuff ... ", aString
    
        i1 = aString.find('(')
        if (i1 >= 0):
            i2 = aString.find(')', i1)
            if (i2 >= 0):
                aString = aString[:i1] + aString[i2 + 1:]
                aString = self._removeParentheticalStuff(aString)
    
        # print " returning from removeParentheticalStuff ... ", aString
        return (aString)
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    
    def _cleanString(self, aString):
    
        # print " in cleanString <%s> " % aString
        tString = self._removeParentheticalStuff(aString)
        if (len(tString) > 1):
            aString = tString
    
        skipChars = ["(", ")", "'", "@", '"']
        spaceChars = [" ", ".", "/", ":"]
        okChars = ["-", "_", ","]
    
        bString = ''
        for ii in range(len(aString)):
            if (aString[ii] in skipChars):
                pass
            elif (aString[ii] in spaceChars):
                if (bString[-1] != "_"):
                    bString += "_"
            elif (aString[ii] in okChars):
                bString += aString[ii]
            else:
                iChar = ord(aString[ii])
                if ((iChar < ord('0')) or (iChar > ord('z'))):
                    # print " what character is this ??? ", iChar
                    pass
                elif ((iChar > ord('9')) and (iChar < ord('A'))):
                    # print " what character is this ??? ", iChar
                    pass
                elif ((iChar > ord('Z')) and (iChar < ord('a'))):
                    # print " what character is this ??? ", iChar
                    pass
                else:
                    bString += aString[ii]
    
        # somewhat of a hack ;-)
        if (bString == "stage_0"):
            # print " Transforming <STAGE 0> to <TIS> "
            bString = "tis"
    
        if (bString.startswith("stage_")):
            bString = bString[6:]
        if (bString.startswith("grade_")):
            bString = bString[6:]
    
        try:
            while (bString[-1] == "_"):
                bString = bString[:-1]
        except:
            pass
    
        # print "     returning bString <%s> " % bString
        return (bString)

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _validateFeatureParts(self, dType, fType, fName, chrom='', strand=''):
        if (dType != 'N' and dType != 'C' and dType != 'B'):
            raise ValueError("ERROR in makeFeatureName ... dType should be B or C or N %s" % dType)
        if (fType.find(":") > 0):
            raise ValueError("ERROR in makeFeatureName ... fType contains colon ???!!! %s" % fType)
        if (0):
            if ( fName.find(":") > 0 ):
                print " WARNING in makeFeatureName ... fName contains colon ???!!! ", fName
                ii = fName.find(":")
                fName = fName[:ii] + fName[ii+1:]
        
        fType = self._cleanString(fType)
        fName = self._cleanString(fName)

        if (chrom != ''):
            iChr = int(chrom)
            aChr = chrom.upper()
            if (iChr < 0 or iChr > 22 or aChr != 'X' or aChr != 'Y' or aChr != 'M'):
                raise ValueError("ERROR in makeFeatureName ... invalid chromosome ??? %s" % chrom)
    
        if (strand != '+' and strand != '-' and strand != ''):
            raise ValueError("ERROR in makeFeatureName ... invalid strand ??? %s" % strand)
    
        return fType, fName

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # the feature name is to be of the form:
    #      DTYPE:FTYPE:FNAME:CHR:START:STOP:STRAND:EXTRA
    # for example:
    #      N:GEXP:BRCA2:chr13:31787617:31871809:+:U133A
    def _makeFeatureName(self, dType, fType, fName, chrom='', start= -1, stop= -1, strand='', xName=''):
        # start out with LOTS of sanity checking of these input values ...
        fType, fName = self._validateFeatureParts(dType, fType, fName)
    
        # paste the first few pieces of information together ...
        tmpName = dType + ":" + fType + ":" + fName + ":"
    
        # add chromosome string
        if (chrom != ''): 
            tmpName += "chr" + chrom
        tmpName += ":"
    
        # add (start) position
        if (start >= 0): 
            tmpName += "%d" % start
        tmpName += ":"
    
        # add stop position
        if (stop >= 0): 
            tmpName += "%d" % stop
        tmpName += ":"
    
        if (strand != ''): 
            tmpName += "%s" % strand
        tmpName += ":"
    
        if (xName != ''): 
            tmpName += "%s" % xName
    
        # print " --> feature name <%s> " % tmpName

        # double-check that there are no question marks ...
        while (tmpName.find("?") >= 0):
            ii = tmpName.find("?")
            tmpName = tmpName[:ii] + tmpName[ii + 1:]

        return tmpName

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    broad_mit_edu_genome_wide_snp_6 (genome_wide_snp_6.py)
    #    clinical (clinical.py)
    #    humanmethylation (humanmethylation.py)
    #    mdanderson_org_mda_rppa_core (mda_rppa_core.py)
    def postprocess(self, dataMatrix, geneList, sampleList):
        dataD = {}
        dataD['rowLabels'] = geneList
        dataD['colLabels'] = sampleList
        dataD['dataMatrix'] = dataMatrix
        dataD['dataType'] = "%s:%s" % (self.dType, self.fType)
        dataD['sortRowFlag'] = int(self.configuration['sort_row_flag'])
        dataD['sortColFlag'] = int(self.configuration['sort_col_flag'])
        return dataD

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    mdanderson_org_mda_rppa_core (mda_rppa_core.py)
    def readNullValue(self, tokens, dataMatrix, sampleIndex, e):
        if (len(tokens) == 1 or tokens[1] == 'null' or tokens[1] == 'NA'):
            dataMatrix[self.curGeneCount][sampleIndex] = self.NA_VALUE
        else:
            raise ValueError('ERROR converting token to float ??? %s: token length: %i tokens: %s', (str(self), len(tokens), tokens), e)

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    broad_mit_edu_genome_wide_snp_6 (genome_wide_snp_6.py)
    #    humanmethylation (humanmethylation.py)
    #    mdanderson_org_mda_rppa_core (mda_rppa_core.py)
    def _readDatumDetails(self, info, tokens, dataMatrix, sampleIndex):
        dataMatrix[self.curGeneCount][sampleIndex] = float(tokens[self.tokenDatumIndex])
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    broad_mit_edu_genome_wide_snp_6 (genome_wide_snp_6.py)
    #    bcgsc_ca_illuminaga_rnaseq (illumina_rnaseq.py)
    #    unc_edu_illuminaga_rnaseq (illumina_rnaseq.py)
    #    unc_edu_illuminaga_rnaseqv2 (illumina_rnaseq.py)
    #    unc_edu_illuminahiseq_rnaseq (illumina_rnaseq.py)
    #    unc_edu_illuminahiseq_rnaseqv2 (illumina_rnaseq.py)
    #    mdanderson_org_mda_rppa_core (mda_rppa_core.py)
    def _readGeneDetails(self, tokens, geneList):
        geneList += [self.genename2geneinfo[tokens[self.tokenGeneIndex]]]
        # verify order of genes stays the same for all files
        if self.myGeneList[self.curGeneCount] != geneList[self.curGeneCount]:
            raise ValueError("genes did not match at %i\tprevious: %s\tcurrent: %s" % (self.curGeneCount, self.myGeneList[self.curGeneCount], geneList[self.curGeneCount]))
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    humanmethylation (humanmethylation.py)
    #    mdanderson_org_mda_rppa_core (mda_rppa_core.py)
    #    nationwidechildrens_org_microsat_i (microsat_i)
    def _readDataDetails(self, info, tokens, geneList, dataMatrix, sampleIndex):
        self._readGeneDetails(tokens, geneList)
        try:
            self._readDatumDetails(info, tokens, dataMatrix, sampleIndex)
        except Exception as e:
            self.readNullValue(tokens, dataMatrix, sampleIndex, e)
        self.curGeneCount += 1
        return False
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _readDataLine(self, info, dataFile, geneList, dataMatrix, sampleIndex):
        tokens = dataFile.readline().strip().split('\t')
        if (not tokens or 0 == len(tokens) or 1 > len(tokens[0])):
            return True
        return self._readDataDetails(info, tokens, geneList, dataMatrix, sampleIndex)
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    humanmethylation (humanmethylation.py)
    def postReadFile(self):
        # base class does nothing
        pass
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overridden by:
    #    clinical (clinical.py)
    def readDataFile(self, dataMatrix, fullPathName, fileName, filename2sampleInfo, sampleIndex):
        print "\t\t", datetime.now(), "reading data for %s" % str(self)
        try:
            self._readPatternDesign()
        except Exception as e:
            raise ValueError('Failed to read the design file %s' % self.configuration['platformdesign'], e)

        (barcode, info, _) = filename2sampleInfo[fileName][0]
        print '\t\tbarcode: %s info: %s' % (barcode, info)
        # for the Agilent level-3 data, there are two header rows that look like this:
        # Hybridization REF       TCGA-13-0888-01A-01R-0406-07
        # Composite Element REF   log2 lowess normalized (cy5/cy3) collapsed by gene symbol

        # for the Affy U133A data, there are also two header rows that look like this:
        # Hybridization REF       5500024056197041909864.A11
        # Composite Element REF   Signal
    
        # for the Illumina HumanMethylation27 data, there are also two header rows, but
        # a few more columns:
        # Hybridization REF       TCGA-04-1655-01A-01D-0563-05    TCGA-04-1655-01A-01D-0563-05    TCGA-04-1655-01A-01D-0563-05    TCGA-04-1655-01A-01D-0563-05
        # Composite Element REF   Beta_Value      Gene_Symbol     Chromosome      Genomic_Coordinate
    
        # for the IlluminaGA RNASeq data, there is one header row and a total of 4 columns:
        # gene     raw_counts      median_length_normalized        RPKM
    
        # for the Genome Wide SNP 6 chip, the level-3 data consists of segments, with a
        # single header row like this:
        # ID                                                  chrom       loc.start         loc.end num.mark   seg.mean
        # SONGS_p_TCGAb36_SNP_N_GenomeWideSNP_6_G04_585364        1       150822330       150853218       35      1.594
        # the big difference in this case is that each sample will have it's own segmentation
        # which we will need to store for later re-segmentation ...
        try:
            dataFile = open(fullPathName, 'r')
        except Exception as e:
            raise ValueError('Failed to read the data file %s' % fullPathName, e)
        
        lineCount = int(self.configuration['data_header_lines'])
        for _ in range(lineCount):
            dataFile.readline()
        
        geneList = []
        self.curGeneCount = 0
        done = False
        while not done:
            lineCount += 1
            done = self._readDataLine(info, dataFile, geneList, dataMatrix, sampleIndex)
        self.postReadFile()
        
        if 2 < self.curGeneCount and 4 < len(dataMatrix):
            print "\t\tfirst data entries: %s first feature entries: %s" % (str([dataMatrix[0][sampleIndex], dataMatrix[1][sampleIndex], dataMatrix[2][sampleIndex]]), str(geneList[:3]))
            print "\t\tlast data entries: %s last feature entries: %s" % (str([dataMatrix[-3][sampleIndex], dataMatrix[-2][sampleIndex], dataMatrix[-1][sampleIndex]]), str(geneList[len(geneList) - 3:]))
        print "\t\t", datetime.now(), "finished reading %i lines of data for barcode %s.  found %i genes" % (lineCount, barcode, self.curGeneCount)
        return (geneList, [barcode])

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def getFileNameFromPath(self, filePath):
        # --mm modified to run test on windows
        filePath = filePath.replace('\\', '/')
        index = filePath.rfind('/')
        return filePath[index+1:]
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def processFile(self, fullPathName, dataMatrix, filename2sampleInfo, geneList, sampleList):
        fileName = self.getFileNameFromPath(fullPathName)
        print '\t\t', datetime.now(), 'in processFile() for %s' % fileName
    
        (geneList, barcodes) = self.readDataFile(dataMatrix, fullPathName, fileName, filename2sampleInfo, len(sampleList))
        sampleList += barcodes
        print '\t\t', datetime.now(), 'finished processFile() for %s\n' % fileName
        return geneList
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def processDirectory(self, dataMatrix, directory, filename2sampleInfo, numGenes, geneList, sampleList, gotFiles):
        print '\tlooking for txt files in list of length %d ' % len(directory.files())
        fileList = filename2sampleInfo.keys()
        numProc = 0
        for fullPathName in directory.files():
            if (fullPathName.endswith(".txt") >= 0):
                fileName = self.getFileNameFromPath(fullPathName)
                ## similarly, we only read files that are in our file list ...
                if ( fileName not in fileList ):
                    print '\t\tSKIP: this file is not in our list (%s) ' % ( fileName )
                    continue
    
                if ( fileName in gotFiles ):
                    print '\t\tSKIP: already read this file (%s) ' % ( fileName )
                    continue
    
                if ( filename2sampleInfo[fileName] in sampleList ):
                    print '\t\tSKIP: already read this barcode (%s) ' % ( filename2sampleInfo[fileName] )
                    continue
    
                print "\t\tprocessing file : sampleIndex=%d %s " % ( len(sampleList), fileName )
                gotFiles += [ fileName ]
                numProc += 1
                (geneList) = self.processFile(fullPathName, dataMatrix, filename2sampleInfo, geneList, sampleList)
                if ( self.genesMatchup() and geneList and numGenes != len(geneList) ):
                    raise ValueError("ERROR ??? the number of genes doesn't match the length of the gene list: %i %i for %s" % (numGenes, len(geneList), fileName))
    
        print "\t--> got %d files processed \n" % numProc
        return (geneList, sampleList)
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overidden by: 
    #    bcgsc_ca_illuminahiseq_mirnaseq (illumina_rnaseq.py) 
    #    bcgsc_ca_illuminaga_mirnaseq (illumina_rnaseq.py) 
    def processDirectories(self, topDirs, archiveList, filename2sampleInfo, numSamples):
        print datetime.now(), "processing directories"
        numGenes = self.getNumGenes()
        dataMatrix = [['' for _ in range(self.getNumSamples(filename2sampleInfo))] for _ in range(numGenes)]
        print " --> allocating dataMatrix ... %d x %d " % ( numGenes, numSamples )
        geneList = []
        sampleList = []
        gotFiles = []
    
        dirMatch = self.getDirectoryLevel()
        for topDir in topDirs:
            directories = path.path(topDir)
            for dirName in directories.dirs():
                print '\t', self.getFileNameFromPath(dirName)
                if ( dirName.find(dirMatch) >= 0 ):
                    archiveName = self.getFileNameFromPath(dirName)
                    print '\tnext directory:', archiveName
         
                    ## we only look into archives that are in our archive list ... this
                    ## should take care of the problem of grabbing old data ...
                    ## (assuming that we *have* an archive list!)
                    if (archiveList[0] != 'unknown' and archiveName not in archiveList):
                        continue
        
                    directory = path.path ( dirName )
                    (geneList, sampleList) = self.processDirectory(dataMatrix, directory, filename2sampleInfo, numGenes, geneList, sampleList, gotFiles)
        if ( numSamples != len(sampleList) ):
            raise ValueError("ERROR ??? the number of samples doesn't match the length of the sample list: %i %i " % (numSamples, len(sampleList)))
        print datetime.now(), "done processing directories\n"
        return (dataMatrix, geneList, sampleList)

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # overidden by: 
    #    clinical (clinical.py) 
    def writeMatrix(self, matrixParams, outFilename):
        print datetime.now(), 'writing out data matrix to %s' % outFilename
        newFeatureName = "C:SAMP:" + self.configuration['fm_feature_type'].lower() + "Platform:::::" + self.configuration['fm_platform_type']
        newFeatureValue = self.configuration['techtype']
        tsvIO.addConstFeature (matrixParams, newFeatureName, newFeatureValue)

        tsvIO.writeTSV_dataMatrix (matrixParams, matrixParams['sortRowFlag'], matrixParams['sortColFlag'], outFilename)
        print datetime.now(), 'finished writing out data matrix\n'
        
