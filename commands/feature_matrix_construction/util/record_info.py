'''
Created on Aug 15, 2013
# PARTICIPANT = TCGA-07-0227
# SAMPLE = TCGA-07-0227-20A
# BARCODE = TCGA-07-0227-20A-01D-1129-05
# UUID_ALIQUOT = e498536b-c7bf-4ff1-8efd-3058e928df9c
# DATA_TYPE = DNA
# PLATFORM = Methylation HumanMethylation27
# URL = /tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/stad/cgcc/jhu-usc.edu/humanmethylation27/methylation/jhu-usc.edu_STAD.HumanMethylation27.Level_1.1.2.0/5543207051_C_Grn.idat
# DATA_LEVEL = 1
# ARCHIVE_NAME = jhu-usc.edu_STAD.HumanMethylation27.Level_1.1.2.0
# BATCH = 0
# DATE_ADDED = 27-OCT-12 08.21.52.832000
# ANNOTATION_TYPES = PM Observation:General

@author: michael
'''

class recordInfo():
    ''' simple container for a line from the archive '''
    def __init__(self, line):
        self.participant = line[0]
        self.sample = line[1]
        self.barcode = line[2]
        self.uuid_aliquot = line[3]
        self.data_type = line[4]
        self.platform = line[5]
        self.url = line[6]
        self.data_level = line[7]
        self.archive_name = line[8]
        self.batch = line[9]
        self.date_added = line[10]
        self.annotation_types = line[11]
        
