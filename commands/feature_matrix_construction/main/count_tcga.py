'''
Created on Jun 14, 2013

class to iterate through the TCGA directories and report on counts per cancer per platform

@author: michael
'''
from datetime import datetime
import sys

import parse_tcga
from technology_type_factory import technology_type_factory

sampleheader = ['cnv', 'rna', 'meth', 'mirna', 'total']
participantheader = ['clinical', 'cnv', 'mutations', 'rna', 'meth', 'mirna', 'total']
platform2header = {'bcgsc.ca/illuminaga_rnaseq/rnaseq/': 'rna',
	'bcgsc.ca/illuminaga_mirnaseq/mirnaseq/': 'mirna',
	'bcgsc.ca/illuminahiseq_rnaseq/rnaseq/': 'rna',
	'bcgsc.ca/illuminahiseq_mirnaseq/mirnaseq/': 'mirna',
	'broad.mit.edu/genome_wide_snp_6/snp/': 'cnv',
	'genome.wustl.edu/genome_wide_snp_6/snp/': 'cnv',
	'broad.mit.edu/ht_hg-u133a/transcriptome/': 'rna',
	'jhu-usc.edu/humanmethylation27/methylation/': 'meth',
	'jhu-usc.edu/humanmethylation450/methylation/': 'meth',
	'mdanderson.org/mda_rppa_core/protein_exp/': 'protein',
	'nationwidechildrens.org/microsat_i/fragment_analysis/': 'microsat',
	'unc.edu/agilentg4502a_07_1/transcriptome/': 'rna',
	'unc.edu/agilentg4502a_07_2/transcriptome/': 'rna',
	'unc.edu/agilentg4502a_07_3/transcriptome/': 'rna',
	'unc.edu/illuminaga_rnaseq/rnaseq/': 'rna',
	'unc.edu/illuminahiseq_rnaseq/rnaseq/': 'rna',
	'unc.edu/illuminahiseq_rnaseqv2/rnaseqv2/': 'rna',
	'unc.edu/h-mirna_8x15k/mirna/': 'mirna',
	'clinical/': 'clinical'}

def addone(platform2count, header):
    platform2count.setdefault(header, 0)
    platform2count[header] += 1

def run(argv):
    print datetime.now(), "starting... (%s)" % (argv)
    _, tumorTypes, _ = parse_tcga.initialize(argv)
    config = parse_tcga.config
    if ['all'] == tumorTypes:
        tumorTypes = config.get('main', 'cancerDirNames').split(',')
    techTypeFactory = technology_type_factory(config)
    platforms = techTypeFactory.getTechnologyTypes()
    tumor2platforms2barcodes = {}
    for tumor in tumorTypes:
        platforms2barcodes = tumor2platforms2barcodes.setdefault(tumor, {})
        for platform in platforms:
            techType = techTypeFactory.getTechnologyType(config, platform)
            numSamples, filename2sampleInfo, _, _ = parse_tcga.parseFileInfo(techType, tumor)
            if 0 == numSamples:
                print 'did not find any samples for %s' % tumor
                continue
            platforms2barcodes[platform] = set([info[0][0] for info in filename2sampleInfo.itervalues()])
    # put together the return values
    platform2tumors = {}
    tumor2patient2header2counts = {}
    tumor2sample2header2counts = {}
    for tumor, platforms2barcodes in tumor2platforms2barcodes.iteritems():
        for platform, barcodes in platforms2barcodes.iteritems():
            platform2tumors.setdefault(platform, set()).add(tumor)
            header = platform2header[platform]
            if not header:
                raise ValueError('%s was not mapped to a header' % (platform))
            [addone(tumor2patient2header2counts.setdefault(tumor, {}).setdefault(barcode[:12], {}), header) for barcode in barcodes]
            [addone(tumor2sample2header2counts.setdefault(tumor, {}).setdefault(barcode[:16], {}), header) for barcode in barcodes if 15 < len(barcode)]
    
    print '%s' % '\n'.join([(platform + ': ' + str(tumors)) for (platform, tumors) in platform2tumors.iteritems()])
    print datetime.now(), "finished"
    return platform2tumors, tumor2patient2header2counts, tumor2sample2header2counts

if __name__ == '__main__':
    run(sys.argv)
    sys.exit(0)
