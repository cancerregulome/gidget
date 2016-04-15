'''
Created on Jun 20, 2012

@author: michael
'''
from env import gidgetConfigVars

import commands
from datetime import datetime
import os

import miscIO
import path
from technology_type import technology_type

class illumina_rnaseq(technology_type):
    '''
    base class for Illumina rnaseq platforms
    '''

    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        technology_type.__init__(self, config, platformID)
        self.configuration.update(config.items('illumina_rnaseq'))

    def _setGenomeRefIndex(self):
        self.genomeRef = None
        self.genomeRefIndex = int(self.configuration['igenomeref'])
    
    def _setGenomeRef(self, tokens):        
        if not self.genomeRef:
            self.genomeRef = tokens[self.genomeRefIndex]
            print 'genome ref set to %s' % (self.genomeRef)
        elif self.genomeRef != tokens[self.genomeRefIndex]:
            raise ValueError('found two different genome references, can\'t handle this')

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _preprocessSDRFFile(self, sdrfFilename):
        fileGenomeRefs = set()
        with open(sdrfFilename, 'r') as sdrfFile:
            skip = True
            for line in sdrfFile:
                if skip:
                    skip = False
                    continue
                fileGenomeRefs.add(line.split('\t')[self.genomeRefIndex])
        
        if self.genomeRef:
            if self.genomeRef not in fileGenomeRefs:
                raise ValueError('did not find a compatible genome reference build for %s in %s, found %s' % (self.genomeRef, sdrfFilename, fileGenomeRefs))
        else:
            genomeRefOrder = dict([(genomeRef, i) for i, genomeRef in enumerate(self.configuration['genomereforder'].split(','))])
            curIndex = -1
            for genomeRef in fileGenomeRefs:
                if genomeRef != '->' and genomeRefOrder[genomeRef] > curIndex:
                    self.genomeRef = genomeRef
                    print 'genome ref set to %s in preprocessing' % (self.genomeRef)

    def _internalReadPatternDesign(self):
        patternDesign = ''
        if self.configuration['platformdesign']:
            root_dir = self.configuration['root_dir']
            print '\troot_dir("%s"): %s' % (self.configuration['root_dir'], root_dir)
            patternDesign = self.configuration['platformdesign'] % (root_dir, self.genomeRef)
        if 0 == len(self.genename2geneinfo) and patternDesign:
            print '\t', datetime.now(), 'reading gene list from %s' % (patternDesign) 
            with open(patternDesign) as patternFile:
                for line in patternFile:
                    tokens = line.strip().split('\t')
                    self._addGeneName(tokens)
            print '\t', datetime.now(), 'finished reading gene list.  found %i genes\n' % len(self.myGeneList)

    def _correctGeneName(self, tokens):
        if ( tokens[0].endswith("_calculated") ):
            tokens[0] = tokens[0][:-11]
        
    ## for the RNASeq data, the gene name unfortunately looks like this: "BRCA1|672"
    ## and sometimes "?|100130426"
    ## --> at first I was just using the first part of the name if it was not "?"
    ## but it turns out that there is one case where that first part is not unique
    ## SLC35E2|728661 and SLC35E2|9906, so I will instead concatenate the two
    ## parts of the name
    def _addGeneNameForRNA(self, tokens):
        self._correctGeneName(tokens)
        ## split up the 'gene' name by the delimiter '|'
        tmpTokens = tokens[0].split('|')
        if (tmpTokens[0] != "?"):
            geneName = tmpTokens[0]
            if (len(tmpTokens) == 1):
                xName = ''
            elif (len(tmpTokens) == 2):
                xName = tmpTokens[1]
            elif (len(tmpTokens) == 3):
                if (tmpTokens[1] != "?"):
                    xName = tmpTokens[1] + "," + tmpTokens[2]
                else:
                    xName = tmpTokens[2]
            else:
                raise ValueError("FATAL ERROR ??? !!! %s\n%s" % (tmpTokens, tokens))
        else:
            if (len(tmpTokens) == 1):
                raise ValueError("FATAL ERROR ???? !!!! %s\n%s" % (tmpTokens, tokens))
            elif (len(tmpTokens) == 2):
                geneName = tmpTokens[1]
                xName = tmpTokens[1]
            elif (len(tmpTokens) == 3):
                geneName = tmpTokens[1]
                if (tmpTokens[1] != "?"):
                    xName = tmpTokens[1] + "," + tmpTokens[2]
                else:
                    xName = tmpTokens[2]
            else:
                raise ValueError("FATAL ERROR ????? !!!!! %s\n%s" % (tmpTokens, tokens))

        ## print " (f) "
        featureName = self._makeFeatureName(self.dType, self.fType, geneName, '', -1, -1, '', xName)
        self.genename2geneinfo[tokens[0]] = featureName
        self.myGeneList += [featureName]
        
    def _internalReadmiRNA_Archive(self, topDir, zPlat):
        print datetime.now(), "\tstarting getFilesFromArchives(): %s" % (topDir)
        dMatch = self.configuration['dirlevel']
        outDir = self.configuration['outDir']

        if (not os.path.exists(topDir)):
            print '     --> <%s> does not exist ' % topDir
            return 0, None, None, []
        
        gotFiles = {}
        d1 = path.path(topDir)
        archivePaths = []
        archiveList = []
        for dirName in d1.dirs():

            print dirName

            if (dirName.find(dMatch) >= 0):
                archivePaths += [dirName]
                print ' '
                print '     found a <%s> directory : <%s> ' % (dMatch, dirName)
                archiveName = dirName[dirName.rfind('/') + 1:]
                archiveList += [archiveName]
                print '     archiveName : ', archiveName

                if (dirName.find(zPlat[:zPlat.rfind('_')]) < 0):
                    raise ValueError(" not a valid platform: %s ??? !!! " % (dirName))

                cmdString = gidgetConfigVars['TCGAFMP_ROOT_DIR'] + "/" + self.configuration['matrix_script']
                cmdString += " -m %s " % self.configuration['matrix_adf']
                cmdString += " -o %s " % outDir
                cmdString += " -p %s " % topDir
                cmdString += " -n %s " % zPlat

                print " "
                print cmdString
                print " "
                (status, output) = commands.getstatusoutput(cmdString)
                print '\nstatus: %s' % (status)
                print 'output: %s\n' % (output)

                normMatFilename = outDir + "/%s_%s.txt" % (self.configuration['matrix_outfile_base'], zPlat)
                self.configuration['normMatFilename'] = normMatFilename
                print " normMatFilename = <%s> " % normMatFilename

                # make sure that we can open this file ...
                try:
                    fh = file(normMatFilename, 'r')
                    gotFiles[normMatFilename] = [normMatFilename]
                    fh.close()
                except:
                    raise ValueError("\nNot able to open expn_matrix_mimat_norm file ???\n")

        print " "
        print " "
        if (len(gotFiles) == 0):
            raise ValueError(" ERROR in Illumina miRNASeq ... no data files found ")
        if (len(gotFiles) > 1):
            raise ValueError(" ERROR ??? we should have only one file at this point ")
            print gotFiles
        print datetime.now(), "\tfinished getFilesFromArchives(): %s" % (topDir)
        return len(gotFiles), gotFiles, archiveList, archivePaths

    # -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _loadNameMap(self, mapFilename):
        metaData = {}
    
        fh = file(mapFilename)
        for aLine in fh:
            aLine = aLine.strip()
            tokenList = aLine.split('\t')
            metaData[tokenList[1]] = tokenList[0]
        fh.close()
    
        return (metaData)

    # -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # hsa-let-7a-2 MIMAT0010195 N:MIRN:hsa-let-7a-2:::::MIMAT0010195
    def _makemiRNAFeatureName(self, tok0, tok1, metaData):
    
        try:
            featName = "%s:%s:" % (self.dType, self.fType) + metaData[tok1] + ":::::" + tok1
            print " all good : ", tok0, tok1, featName
        except:
            featName = "%s:%s:" % (self.dType, self.fType) + tok0 + ":::::" + tok1
            print " BAD ??? ", tok0, tok1, featName
    
        return (featName)

    # -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _internalProcessDirectories(self, topDirs, archiveList, filename2sampleInfo, numSamples):
        print datetime.now(), "processing directories"
        
        fh = file(self.configuration['normMatFilename'], 'r')
        numRow = miscIO.num_lines(fh) - 1
        numCol = miscIO.num_cols(fh, '\t') - 1

        dataMatrix = [0] * numRow
        for iR in range(numRow):
            dataMatrix[iR] = [0] * numCol

        sampleList = fh.readline().strip().split('\t')[1:]
        if (len(sampleList) != numCol):
            raise ValueError(" ERROR #1 ??? ")
        featureList = []
        # we also need to read in the mapping file ...
        metaData = self._loadNameMap("%s" % self.configuration['matrix_mapping_file'])
        NA_VALUE = -999999
        done = 0
        iR = 0
        numNA = 0
        while (not done):
            aLine = fh.readline()
            aLine = aLine.strip()
            tokenList = aLine.split('\t')
            if (len(tokenList) != (numCol + 1)):
                done = 1
            else:
                aLabel = tokenList[0]
                # print " label = <%s> " % aLabel
                labelTokens = aLabel.split('.')
                # print labelTokens
                featName = self._makemiRNAFeatureName(labelTokens[0], labelTokens[1], metaData)
                # print featName
                featureList += [featName]

                for iC in range(numCol):
                    try:
                        fVal = float(tokenList[iC + 1])
                        dataMatrix[iR][iC] = fVal
                    except:
                        dataMatrix[iR][iC] = NA_VALUE
                        numNA += 1
                iR += 1
                print " iR=%d    numNA=%d " % (iR, numNA)
        print datetime.now(), "finished processing directories"
        return dataMatrix, featureList, sampleList

## the platform illuminaga_rnaseq is in use at both UNC and BCGSC ... although it looks
## like the mage-tab files are the same or nearly so ...

class bcgsc_ca_illuminaga_rnaseq(illumina_rnaseq):
    '''
    the illumina ga platform for ngs for RNA
    '''
    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        illumina_rnaseq.__init__(self, config, platformID)
        self.configuration.update(config.items('bcgsc_ca_illuminaga_rnaseq'))
        self._setGenomeRefIndex()

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def preprocessSDRFFile(self, sdrfFilename):
        self._preprocessSDRFFile(sdrfFilename)

    def includeFile(self, tokens):
        if tokens[self.iOther].lower().find("gene") < 0 or tokens[self.iOther].lower().find("expression") < 0:
            mess = '(e) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iOther, tokens[self.iOther]
            return (None, None, None, None, False, mess)
        elif self.genomeRef != tokens[self.genomeRefIndex]:
            mess = '(f) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.genomeRefIndex, tokens[self.genomeRefIndex]
            return (None, None, None, None, False, mess)
        return illumina_rnaseq.includeFile(self, tokens)
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _readPatternDesign(self):
        illumina_rnaseq._internalReadPatternDesign(self)

    def _addGeneName(self, tokens):
        self._addGeneNameForRNA(tokens)

    def _readGeneDetails(self, tokens, geneList):
        self._correctGeneName(tokens)
        technology_type._readGeneDetails(self, tokens, geneList)

## the platform illuminaga_rnaseq is in use at both UNC and BCGSC ... although it looks
## like the mage-tab files are the same or nearly so ...

class bcgsc_ca_illuminahiseq_rnaseq(illumina_rnaseq):
    '''
    the illumina ga platform for ngs for RNA
    '''
    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        illumina_rnaseq.__init__(self, config, platformID)
        self.configuration.update(config.items('bcgsc_ca_illuminahiseq_rnaseq'))
        self._setGenomeRefIndex()

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def preprocessSDRFFile(self, sdrfFilename):
        # this is to take care of an inconsistency with how bcgsc handles hg18 and hg19 pattern designs
        # it will likely need to be removed once all hg19 files use the updated pattern design.  currently
        # ga mirna and other tumor types for hiseg mirna do use the updated pattern design if genome ref is 
        # for hg19
        self._preprocessSDRFFile(sdrfFilename)

    def includeFile(self, tokens):
        if tokens[self.iOther].lower().find("gene") < 0 or tokens[self.iOther].lower().find("expression") < 0:
            mess = '(e) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iOther, tokens[self.iOther]
            return (None, None, None, None, False, mess)
        elif self.genomeRef != tokens[self.genomeRefIndex]:
            mess = '(f) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.genomeRefIndex, tokens[self.genomeRefIndex]
            return (None, None, None, None, False, mess)
        return illumina_rnaseq.includeFile(self, tokens)
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def _readPatternDesign(self):
        illumina_rnaseq._internalReadPatternDesign(self)

    def _addGeneName(self, tokens):
        self._addGeneNameForRNA(tokens)

    def _readGeneDetails(self, tokens, geneList):
        self._correctGeneName(tokens)
        technology_type._readGeneDetails(self, tokens, geneList)

class bcgsc_ca_illuminaga_mirnaseq(illumina_rnaseq):
    '''
    the illumina ga platform for ngs for miRNA
    '''

    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        illumina_rnaseq.__init__(self, config, platformID)
        self.configuration.update(config.items('bcgsc_ca_illuminaga_mirnaseq'))
        if self.configuration.has_key('matrix_script'):
            self.setMiscConfig()
        self.configuration['outDir'] = config.get('main', 'out_directory')

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def getFilesFromArchives(self, topDir):
        return self._internalReadmiRNA_Archive(topDir, self.configuration['techtype'])

    def processDirectories(self, topDirs, archiveList, filename2sampleInfo, numSamples):
        return self._internalProcessDirectories(topDirs, archiveList, filename2sampleInfo, numSamples)

class bcgsc_ca_illuminahiseq_mirnaseq(illumina_rnaseq):
    '''
    the illumina hiseq platform for ngs for miRNA
    '''

    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        illumina_rnaseq.__init__(self, config, platformID)
        self.configuration.update(config.items('bcgsc_ca_illuminahiseq_mirnaseq'))
        if self.configuration.has_key('matrix_script'):
            self.setMiscConfig()
        self.configuration['outDir'] = config.get('main', 'out_directory')

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def getFilesFromArchives(self, topDir):
        return self._internalReadmiRNA_Archive(topDir, self.configuration['techtype'])

    def processDirectories(self, topDirs, archiveList, filename2sampleInfo, numSamples):
        print datetime.now(), "processing directories"
        return self._internalProcessDirectories(topDirs, archiveList, filename2sampleInfo, numSamples)


class unc_edu_illuminaga_rnaseq(illumina_rnaseq):
    '''
    the illumina ga platform for ngs for mRNA
    '''

    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        illumina_rnaseq.__init__(self, config, platformID)
        self.configuration.update(config.items('unc_edu_illuminaga_rnaseq'))

    def includeFile(self, tokens):
        if tokens[self.iOther].lower().find("gene") < 0 or tokens[self.iOther].lower().find("expression") < 0:
            mess = '(e) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iOther, tokens[self.iOther]
            return (None, None, None, None, False, mess)
        return illumina_rnaseq.includeFile(self, tokens)

    def _addGeneName(self, tokens):
        self._addGeneNameForRNA(tokens)

class unc_edu_illuminaga_rnaseqv2(illumina_rnaseq):
    '''
    the illumina ga v2 platform for ngs for mRNA
    '''
    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        illumina_rnaseq.__init__(self, config, platformID)
        self.configuration.update(config.items('unc_edu_illuminaga_rnaseqv2'))

    def includeFile(self, tokens):
        if tokens[self.iOther] != "RSEM_genes_normalized":
            mess = '(e) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iOther, tokens[self.iOther]
            return (None, None, None, None, False, mess)
        return illumina_rnaseq.includeFile(self, tokens)

    def _addGeneName(self, tokens):
        self._addGeneNameForRNA(tokens)

class unc_edu_illuminahiseq_rnaseq(illumina_rnaseq):
    '''
    the illumina hiseq platform for ngs for mRNA
    '''
    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        illumina_rnaseq.__init__(self, config, platformID)
        self.configuration.update(config.items('unc_edu_illuminahiseq_rnaseq'))

    def includeFile(self, tokens):
        if tokens[self.iOther].find("gene_expression") < 0:
            mess = '(e) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iOther, tokens[self.iOther]
            return (None, None, None, None, False, mess)
        return illumina_rnaseq.includeFile(self, tokens)

    def _addGeneName(self, tokens):
        self._addGeneNameForRNA(tokens)

class unc_edu_illuminahiseq_rnaseqv2(illumina_rnaseq):
    '''
    the illumina hiseq v2 platform for ngs for mRNA
    '''
    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        illumina_rnaseq.__init__(self, config, platformID)
        self.configuration.update(config.items('unc_edu_illuminahiseq_rnaseqv2'))

    def includeFile(self, tokens):
        if tokens[self.iOther] != "RSEM_genes_normalized":
            mess = '(e) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iOther, tokens[self.iOther]
            return (None, None, None, None, False, mess)
        return illumina_rnaseq.includeFile(self, tokens)

    def _addGeneName(self, tokens):
        self._addGeneNameForRNA(tokens)

