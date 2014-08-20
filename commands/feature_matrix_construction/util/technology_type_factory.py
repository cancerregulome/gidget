'''
Created on Jun 18, 2012

@author: m.miller
'''
import traceback

from agilentg4502a_07 import unc_edu_agilentg4502a_07_1
from agilentg4502a_07 import unc_edu_agilentg4502a_07_2
from agilentg4502a_07 import unc_edu_agilentg4502a_07_3
from illumina_rnaseq import bcgsc_ca_illuminaga_rnaseq
from illumina_rnaseq import bcgsc_ca_illuminaga_mirnaseq
from illumina_rnaseq import bcgsc_ca_illuminahiseq_rnaseq
from illumina_rnaseq import bcgsc_ca_illuminahiseq_mirnaseq
from illumina_rnaseq import unc_edu_illuminaga_rnaseq
from illumina_rnaseq import unc_edu_illuminaga_rnaseqv2
from illumina_rnaseq import unc_edu_illuminahiseq_rnaseq
from illumina_rnaseq import unc_edu_illuminahiseq_rnaseqv2
from illumina_rnaseq import mrna_firehose
from illumina_rnaseq import mirna_firehose
from illumina_rnaseq import mature_mirna_firehose
from microsat_i import nationwidechildrens_org_microsat_i
from mda_rppa_core import mdanderson_org_mda_rppa_core
from mda_rppa_core import rppa_firehose
from genome_wide_snp_6 import broad_mit_edu_genome_wide_snp_6
from genome_wide_snp_6 import snp_firehose
from genome_wide_snp_6 import genome_wustl_edu_genome_wide_snp_6
from ht_hg_u133a import broad_mit_edu_ht_hg_u133a
from humanmethylation import jhu_usc_edu_humanmethylation27
from humanmethylation import jhu_usc_edu_humanmethylation450
from humanmethylation import methylation_firehose
from h_mirna_8x15k import unc_edu_h_mirna_8x15k
from clinical import clinical
from clinical import clinical_firehose

class technology_type_factory(object):
    '''
    factory class to return the appropriate technology subclass
    '''
    name2instance = {'unc_edu_agilentg4502a_07_1': unc_edu_agilentg4502a_07_1, 
                  'unc_edu_agilentg4502a_07_2': unc_edu_agilentg4502a_07_2, 
                  'bcgsc_ca_illuminaga_mirnaseq': bcgsc_ca_illuminaga_mirnaseq, 
                  'unc_edu_agilentg4502a_07_3': unc_edu_agilentg4502a_07_3, 
                  'bcgsc_ca_illuminaga_rnaseq': bcgsc_ca_illuminaga_rnaseq, 
                  'bcgsc_ca_illuminaga_mirnaseq': bcgsc_ca_illuminaga_mirnaseq, 
                  'bcgsc_ca_illuminahiseq_rnaseq': bcgsc_ca_illuminahiseq_rnaseq, 
                  'bcgsc_ca_illuminahiseq_mirnaseq': bcgsc_ca_illuminahiseq_mirnaseq, 
                  'unc_edu_illuminaga_rnaseq': unc_edu_illuminaga_rnaseq, 
                  'unc_edu_illuminaga_rnaseqv2': unc_edu_illuminaga_rnaseqv2, 
                  'unc_edu_illuminahiseq_rnaseq': unc_edu_illuminahiseq_rnaseq, 
                  'unc_edu_illuminahiseq_rnaseqv2': unc_edu_illuminahiseq_rnaseqv2, 
                  'mrna_firehose': mrna_firehose,
                  'mirna_firehose': mirna_firehose,
                  'mature_mirna_firehose': mature_mirna_firehose,
                  'mdanderson_org_mda_rppa_core': mdanderson_org_mda_rppa_core, 
                  'rppa_firehose': rppa_firehose, 
                  'nationwidechildrens_org_microsat_i': nationwidechildrens_org_microsat_i, 
                  'broad_mit_edu_genome_wide_snp_6': broad_mit_edu_genome_wide_snp_6,
                  'genome_wustl_edu_genome_wide_snp_6': genome_wustl_edu_genome_wide_snp_6,
                  'snp_firehose': snp_firehose,
                  'broad_mit_edu_ht_hg-u133a': broad_mit_edu_ht_hg_u133a, 
                  'jhu-usc_edu_humanmethylation27': jhu_usc_edu_humanmethylation27, 
                  'jhu-usc_edu_humanmethylation450': jhu_usc_edu_humanmethylation450, 
                  'methylation_firehose': methylation_firehose, 
                  'unc_edu_h-mirna_8x15k': unc_edu_h_mirna_8x15k, 
                  'clinical': clinical, 
                  'clinical_firehose': clinical_firehose } 
    platformID2class = {}
    
    def __init__(self, config):
        '''
        Constructor
        '''
        for item in config.items("technology_type_factory"):
            try:
                self.platformID2class[item[0]] = self.name2instance[item[1]]
            except Exception as e:
                print e, type(e)
                raise ValueError("problem initializing class map", e)

    def getTechnologyTypes(self):
        return self.platformID2class.keys()
            
    def getTechnologyType(self, config, platformID):
        try:
            return self.platformID2class[platformID](config, platformID)
        except Exception as e:
            traceback.print_exc(10)
            raise ValueError("problem looking up the class. platformID: %s" % (platformID), e)
    
    @classmethod
    def getFirehoseTechnologyType(cls, platformID):
        try:
            return cls.name2instance[platformID]()
        except Exception as e:
            traceback.print_exc(10)
            raise ValueError("problem looking up the class. platformID: %s" % (platformID), e)
