'''
Created on Jun 18, 2012

@author: m.miller
'''
import miscTCGA
from technology_type import technology_type

class unc_edu_agilentg4502a_07(technology_type):
    '''
    base class for the agilent microarray technology types
    '''
    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        technology_type.__init__(self, config, platformID)
        self.configuration.update(config.items('unc_edu_agilentg4502a_07'))
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # this older platform doesn't always have UUID's
    def _checkForUUID(self, tokens):
        barcode = tokens[self.iBarcode]
        if (miscTCGA.looks_like_uuid(barcode)):
            barcode = miscTCGA.uuid_to_barcode(barcode)
        # assume this is the barcode, it will be validated on return
        return '', barcode

    def includeFile(self, tokens):
        retVal = technology_type.includeFile(self, tokens)
        if retVal[4] and  retVal[3] != "cy5":
            retVal = list(retVal)
            retVal[4] = False
            retVal[5] = '(e) NOT including this file ... ', self.iFilename, tokens[self.iFilename], self.iBarcode, tokens[self.iBarcode], self.iOther, tokens[self.iOther]
        return tuple(retVal)

class unc_edu_agilentg4502a_07_1(unc_edu_agilentg4502a_07):
    '''
    the agilent microarray g4502a_07_1 technology type
    '''

    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        unc_edu_agilentg4502a_07.__init__(self, config, platformID)
        self.configuration.update(config.items('unc_edu_agilentg4502a_07_1'))

class unc_edu_agilentg4502a_07_2(unc_edu_agilentg4502a_07):
    '''
    the agilent microarray g4502a_07_2unc_edu_agilentg4502a_07_2.py technology type
    '''

    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        unc_edu_agilentg4502a_07.__init__(self, config, platformID)
        self.configuration.update(config.items('unc_edu_agilentg4502a_07_2'))

class unc_edu_agilentg4502a_07_3(unc_edu_agilentg4502a_07):
    '''
    the agilent microarray g4502a_07_2unc_edu_agilentg4502a_07_3.py technology type
    '''

    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        unc_edu_agilentg4502a_07.__init__(self, config, platformID)
        self.configuration.update(config.items('unc_edu_agilentg4502a_07_3'))
