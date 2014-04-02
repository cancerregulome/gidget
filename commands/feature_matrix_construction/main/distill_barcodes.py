'''
Created on Aug 16, 2013

@author: michael
'''
from datetime import datetime
import os
import sys
import traceback

import read_stad_archive
# import read_stad_snapshot

def main(outfileName, archive, config, tumorType, excfilename, incfilename, excludePlatforms):
    print datetime.now(), 'begin reading archive and snapshot: outfile pattern: %s archive: %s config file: %s tumor type: %s \
        exclusion file name: %s override exclusion filename: %s exclude platforms: %s' %\
        (outfileName, archive, config, tumorType, excfilename, incfilename, excludePlatforms)
    
    index = outfileName.rindex('/')
    if -1 < index:
        outfileDir = outfileName[:index]
        if not os.path.exists(outfileDir):
            os.makedirs(outfileDir, 0774)
    
    print '\treading in exclusion file'
    excbarcodes = set()
    with open(excfilename, 'r') as excfile:
        lines = excfile.readlines()
    for line in lines[1:]:
        if not line.strip():
            break
        excbarcodes.add(line.strip().split('\t')[0])
    print 'excluded barcodes: %s' % (','.join(excbarcodes))
    
    print '\treading in inclusion file'
    platform2platforms = {'DNA methylation': ['humanmethylation27', 'humanmethylation450'], \
                          'RNAseq': ['illuminaga_rnaseq', 'illuminahiseq_rnaseq'], \
                          'miRNAseq': ['illuminaga_mirnaseq', 'illuminahiseq_mirnaseq']}
    platforms2platform = {}
    for key, plist in platform2platforms.iteritems():
        for value in plist:
            platforms2platform[value.lower()] = key.lower()
    print 'platforms2platform:\n\t%s' % ('\n\t'.join([str(key) + ': ' + str(value) for key, value in platforms2platform.iteritems()]))

    with open(incfilename, 'r') as incfile:
        lines = incfile.readlines()
    platform2includes = {}
    platform = None
    incaliquots = set()
    for line in lines:
        if not line.strip():
            break
        fields = line.split('\t')
        if fields[0]:
            if platform:
                print 'writing includes for %s: %s' % (platform, ','.join(incaliquots))
                platform2includes[platform.lower()] = incaliquots
            platform = fields[0].strip()
            incaliquots = set()
        if len(fields) > 1:
            incaliquots.add(fields[1].strip())
    if platform:
        print 'writing includes for %s: %s' % (platform, ','.join(incaliquots))
        platform2includes[platform.lower()] = incaliquots
    print 'include aliquots:\n\t%s' % ('\n\t'.join([key + ': ' + ','.join(values) for key, values in platform2includes.iteritems()]))
    
    includeexcludes, platforms2samples, participant2sample2aliquot2ris = read_stad_archive.main(archive, excbarcodes, platform2includes, platforms2platform)
#    snapshotBarcodes = read_stad_snapshot.main(config, tumorType)

    includeBarcodes = set()
    print datetime.now(), 'writing include/exclude file'
    with open(outfileName + '_include_exclude.txt', 'w') as outfile:
        outfile.write('%s:\n' % ('Include/Exclude'))
        for ie in includeexcludes:
            outfile.write(ie)
            fields = ie.split('\t')
            if 'Include' == fields[1]:
                includeBarcodes.add(fields[0])
        outfile.write('\n')
        
    print datetime.now(), 'writing platform file'
    for platform, platforms in platform2platforms.iteritems():
        platformInfo = [[set(), set()], [set(), set()]]
        platforms2samples[platform] = platformInfo
        for p in platforms:
            if not platforms2samples.has_key(p):
                continue
            info = platforms2samples.pop(p)
            for i in range(len(platformInfo)):
                for j in range(len(platformInfo[0])):
                    if 0 < len(platformInfo[i][j]):
                        if 0 < len(platformInfo[i][j] & info[i][j]):
                            print '\tfound duplicates between platforms for %s: %s' % (platform, ','.join(platformInfo[i][j] & info[i][j]))
                        pparts = set([sample.split('\t')[0][:12] for sample in platformInfo[i][j]])
                        iparts = set([sample.split('\t')[0][:12] for sample in info[i][j]])
                        if 0 < len(pparts & iparts):
                            print '\tfound duplicates between platforms for %s: %s' % (platform, ','.join(pparts & iparts))
                    platformInfo[i][j] |= info[i][j]

    countName = outfileName + '_count_compare'
    with open(outfileName + '_by_platform.txt', 'w') as outfile, open(countName + '_by_platform.txt', 'w') as countfile:
        outfile.write('%s:\n' % ('Participant'))
        countfile.write('%s:\n' % ('Participant'))
        platforms = platforms2samples.keys()
        platforms.sort()
        for platform in platforms:
            samples = platforms2samples[platform]
            participants = [set(), set()]
            participants[0] |= set([sample[:12] for sample in samples[0][0]]) | set([sample[:12] for sample in samples[0][1]])
            participants[1] |= set([sample[:12] for sample in samples[1][0]]) | set([sample[:12] for sample in samples[1][1]])
            
            gminus = set([barcode.split('\t')[0] for barcode in participants[0]]) - includeBarcodes
            if 0 < len(gminus):
                print '%s had excluded barcodes: %s' % (platform, ','.join(gminus))
            gparts = list(participants[0])
            bparts = list(participants[1])
            outfile.write('platform: %s\n\tinclude(%i):\n\t\t%s\n\texclude(%i):\n\t\t%s\n' % (platform, len(gparts),'\n\t\t'.join(gparts), len(bparts),'\n\t\t'.join(bparts)))
            outfile.write('\n')
            countfile.write('platform: %s\n\tinclude(%i)\n\texclude(%i)\n' % (platform, len(gparts), len(bparts)))
            countfile.write('\n')

        outfile.write('%s:\n' % ('Samples'))
        countfile.write('%s:\n' % ('Samples'))
        sampleset = set()
        platforms = platforms2samples.keys()
        platforms.sort()
        for platform in platforms:
            sampleset |= samples[0][0] | samples[0][1]
            samples = platforms2samples[platform]
            gtslen = len(samples[0][0])
            btslen = len(samples[1][0])
            gnslen = len(samples[0][1])
            bnslen = len(samples[1][1])
            gtsamples = list(samples[0][0])
            gtsamples.sort()
            gnsamples = list(samples[0][1])
            gnsamples.sort()
            btsamples = list(samples[1][0])
            btsamples.sort()
            bnsamples = list(samples[1][1])
            bnsamples.sort()
            outfile.write('platform: %s\n\tinclude(%i tumor: %i normal: %i):\n\t\ttumor\n\t\t\t%s\n\t\tnormal\n\t\t\t%s\n\texclude(%i tumor: %i normal: %i):\n\t\ttumor\n\t\t\t%s\n\t\tnormal\n\t\t\t%s\n' % \
                          (platform, gtslen + gnslen, gtslen, gnslen, '\n\t\t\t'.join(gtsamples), '\n\t\t\t'.join(gnsamples), btslen + bnslen, btslen, bnslen, '\n\t\t\t'.join(btsamples), '\n\t\t\t'.join(bnsamples)))
            outfile.write('\n')
            countfile.write('platform: %s\n\tinclude(%i tumor: %i normal: %i)\n\texclude(%i tumor: %i normal: %i)\n' % (platform, gtslen + gnslen, gtslen, gnslen, btslen + bnslen, btslen, bnslen))
            countfile.write('\n')
            
    print datetime.now(), 'writing consolidated sample file'
    with open(outfileName + '_samples.txt', 'w') as outfile:
        outfile.write('%s:\n' % ('SAMPLE_BARCODE'))
        samplelist = list(sampleset)
        samplelist.sort()
        for sample in samplelist:
            if 'DNU' in sample:
                print 'skipping %s' % (sample)
                continue
            outfile.write('%s\n' % (sample[:sample.index('\t')]))
        
    print datetime.now(), 'writing participant file'
    with open(outfileName + '_by_participant.txt', 'w') as outfile:
        outfile.write('%s:\n' % ('Participant info'))
        keys = participant2sample2aliquot2ris.keys()
        keys.sort()
        for participant in keys:
            outfile.write('%s\n' % (participant))
            sample2aliquot2ris = participant2sample2aliquot2ris[participant]
            samples = sample2aliquot2ris.keys()
            samples.sort()
            for sample in samples:
                outfile.write('\t%s\n' % (sample))
                aliquot2ris = sample2aliquot2ris[sample]
                aliquots = aliquot2ris.keys()
                aliquots.sort()
                for aliquot in aliquots:
                    outfile.write('\t\t%s\n' % (aliquot))
                    ris = aliquot2ris[aliquot]
                    for ri in ris:
                        outfile.write('\t\t\t%s\t%s\t%s\n' % (ri.data_level, ri.platform, ri.annotation_types))
    
    archiveset = set()
    excludeNormal = set(['genome_wide_snp_6'])
    header = 'PARTICIPANT	SAMPLE	BARCODE	UUID_ALIQUOT	DATA_TYPE	PLATFORM	URL	DATA_LEVEL	ARCHIVE_NAME	BATCH	DATE_ADDED	ANNOTATION_TYPES'
    print datetime.now(), 'writing full platform files'
    platforms = platforms2samples.keys()
    partMap = {}
    sampleMap = {}
    for platform in platforms:
        usePlatforms = set([platform])
        if platform2platforms.has_key(platform):
            for p in platform2platforms[platform]:
                usePlatforms.add(p)
        with open(outfileName + '_%s.txt' % (platform), 'w') as outfile:
            print 'writing platform %s' % (platform)
            outfile.write('%s\n' % (header))
            samples = platforms2samples[platform]
            for index in range(len(samples[0])):
                if 1 == index and platform in excludeNormal:
                    print 'skipping platform %s for normal samples' % (platform)
                    continue
                for sample in samples[0][index]:
                    sample2aliquot2ris = participant2sample2aliquot2ris[sample[:12]]
                    sample = sample.split('\t')[0]
                    aliquot2ris = sample2aliquot2ris[sample.strip()]
                    for ris in aliquot2ris.itervalues():
                        for ri in ris:
                            if ri.platform.lower() in usePlatforms:
                                platforms = partMap.get(ri.participant, set())
                                platforms.add(ri.data_type)
                                partMap[ri.participant] = platforms
                                platforms = sampleMap.get(ri.sample, set())
                                platforms.add(ri.data_type)
                                sampleMap[ri.sample] = platforms
                                
                                line = '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t\n' % (ri.participant, ri.sample, ri.barcode, ri.uuid_aliquot, ri.data_type, \
                                    ri.platform, ri.url, ri.data_level, ri.archive_name, ri.batch, ri.date_added, ri.annotation_types)
                                outfile.write(line)
                                archiveset.add(line)
        print '\t%s: participants %i, samples %i' % (platform, len(partMap), len(sampleMap))
    with open(outfileName + '_availability_participant.tsv', 'w') as outfile:
        print 'writing data availability for participant'
        platforms = ["Complete Clinical Set", "DNA Methylation", "RNASeq", "miRNASeq", "CNV (SNP Array)", "Somatic Mutations", 
                  "Protected Mutations", "CNV (Low Pass DNASeq)", "Expression-Protein", "Fragment Analysis Results"]
        outfile.write('\t%s\ttotal\n' % ('\t'.join(platforms)))
        colTotals = {}
        keys = partMap.keys()
        keys.sort()
        for key in keys:
            rowTotal = 0
            outfile.write('%s' % key)
            for platform in platforms:
                value = 1 if platform in partMap.get(key) else 0
                rowTotal += value
                colTotals[platform] = colTotals.get(platform, 0) + value
                outfile.write('\t%i' % value)
            outfile.write('\t%i\n' % rowTotal)
        outfile.write('totals')
        for platform in platforms:
            try:
                outfile.write('\t%i' % colTotals[platform])
            except Exception as e:
                traceback.print_exc()
                print 'problem getting column totals for %s: %s' % (platform, e)
        outfile.write('\n')

    with open(outfileName + '_availability_sample.tsv', 'w') as outfile:
        print 'writing data availability for sample'
        platforms = ["Complete Clinical Set", "DNA Methylation", "RNASeq", "miRNASeq", "CNV (SNP Array)", "Somatic Mutations", 
                  "Protected Mutations", "CNV (Low Pass DNASeq)", "Expression-Protein", "Fragment Analysis Results"]
        outfile.write('\t%s\ttotal\n' % ('\t'.join(platforms)))
        colTotals = {}
        keys = sampleMap.keys()
        keys.sort()
        for key in keys:
            rowTotal = 0
            outfile.write('%s' % key)
            for platform in platforms:
                value = 1 if platform in sampleMap.get(key) else 0
                rowTotal += value
                colTotals[platform] = colTotals.get(platform, 0) + value
                outfile.write('\t%i' % value)
            outfile.write('\t%i\n' % rowTotal)
        outfile.write('totals')
        for platform in platforms:
            outfile.write('\t%i' % colTotals[platform])
        outfile.write('\n')

    with open(outfileName + '_archive.txt', 'w') as outfile:
        print 'writing archive'
        outfile.write('%s\n' % (header))
        archivelist = list(archiveset)
        archivelist.sort()
        for archiveline in archivelist:
            if archiveline.split('\t')[5] in excludePlatforms:
                continue
            outfile.write('%s' % (archiveline))

#    print 'archive:\n\t%s \nsnapshot:\n\t%s' % ('\n\t'.join(archiveBarcodes.keys()), '\n\t'.join(snapshotBarcodes.keys()))
    print datetime.now(), 'done reading archive and snapshot and writing file'

# python -u \
#    main/distill_barcodes.py \
#    2014_01_18_stad_counts/barcodes \
#    STAD.freeze.2013.350.txt \
#    config/parse_tcga_count.config \
#    stad \
#    EPCBlacklist_042413.txt \
#    PlatformOverridelist_101613.txt
if __name__ == '__main__':
    excludePlatforms = []
    if 8 == len(sys.argv):
        excludePlatforms = sys.argv[7].split(',')
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], excludePlatforms)
