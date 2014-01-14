'''
Created on Jun 21, 2012

@author: michael
'''

from technology_type import technology_type

class h_mirna_8x15k(technology_type):
    '''
    base class for the H-miRNA_8x15k technology types
    '''
    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        technology_type.__init__(self, config, platformID)
        self.configuration.update(config.items('h-mirna_8x15k'))

class unc_edu_h_mirna_8x15k(h_mirna_8x15k):
    '''
    the agilent microarray H-miRNA_8x15k technology type
    '''

    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        h_mirna_8x15k.__init__(self, config, platformID)
        self.configuration.update(config.items('unc_edu_h-mirna_8x15k'))

