'''
Created on Jun 21, 2012

@author: michael
'''

from technology_type import technology_type

class broad_mit_edu_ht_hg_u133a(technology_type):
    '''
    classdocs
    '''

    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        technology_type.__init__(self, config, platformID)
        self.configuration.update(config.items('broad_mit_edu_ht_hg-u133a'))

