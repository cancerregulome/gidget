'''
Created on Aug 14, 2013

@author: michael
'''
from datetime import datetime
import sys
import urllib

from record_info import recordInfo

def isExcluded(ri, excludes, value, barcode):
    excl = False
    for exclude in excludes:
        if exclude in ri.annotation_types.lower():
            excl = True
    if None != value and excl != value:
        raise ValueError('mismatched value for %s' % (barcode))
    return excl

def getAnnotation(barcode, cellline, epc, redacted, dnu):
    annotation = ''
    if cellline:
        if epc or redacted or dnu:
            raise ValueError('cell line also marked bad for barcode %s' % (barcode))
        annotation += 'Cell Line, '
    if epc:
        annotation = 'EPC, '
    if redacted:
        annotation = 'Redacted, '
    if dnu:
        annotation = 'DNU, '
    annotation = annotation[:-2]
    return annotation

def setBarcode(barcodes, barcode, override, cellline, epc, redacted, dnu):
    index = [0, 0]
    if (cellline or epc or redacted or dnu) and not override:
        # excluded sample
        index[0] = 1
    if 12 < len(barcode) and 1 <= int(barcode[13]):
        # normal sample
        index[1] = 1
    annotation = getAnnotation(barcode, cellline, epc, redacted, dnu)
    barcodes[index[0]][index[1]].add(barcode + '\t' + annotation)


def override_aliquot(platform, platform2includes, platforms2platform, aliquot):
    override = False
    value = platforms2platform.get(platform.lower(), platform.lower())
    if aliquot in platform2includes.get(value, set()):
        print '\toverriding %s for platform %s' % (aliquot, platform)
        override = True
    return override

def main(latest, excbarcodes, platform2includes, platforms2platform):
    print datetime.now(), 'begin reading archive'
    writeArchive = False
    baseurl = 'https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/other/awg_archives/'
    url = urllib.urlopen(baseurl + latest)
    annotExcludes = set()
    annotIncludes = set()
    participant2sample2aliquot2ris = {}
    platforms = set()
    count = 0
    countNoPlatform = 0
# for STAD datafreeze
#    batches = [0,48,57,95,129,152,165,211,220,242,257,269]
# for ESCA
    batches = []

    if writeArchive:
        archiveFile = open('archives/' +latest, 'w')
        archiveFile.write(url.readline())
    else:
        url.readline()
    for line in url:
        if writeArchive:
            archiveFile.write(line)
        if 0 == count % 8192:
            print '\tread %i lines' % (count)
        count += 1
        
        ri = recordInfo(line.strip('\n').split('\t'))
        if '-' == ri.batch or (0 < len(batches) and int(ri.batch) not in batches):
            continue
        if '0' == ri.batch and ri.barcode[13] != '2':
            # we only expect cell lines in batch 0
            continue
        
        if not ri.platform or '-' in ri.platform:
            countNoPlatform += 1
            continue
        sample2aliquot2ris = participant2sample2aliquot2ris.setdefault(ri.participant, {})
        aliquot2ris = sample2aliquot2ris.setdefault(ri.sample, {})
        ris = aliquot2ris.setdefault(ri.barcode, [])
        ris += [ri]
        platforms.add(ri.platform.strip())
    if writeArchive:
        archiveFile.flush()
        archiveFile.close()
    
    includeexclude = ['\nParticpantBarcode\tUse\tReason\n']
    platforms2samples = {}
    participant_excludes = ['redaction', 'unacceptable']
    sample_excludes = ['dnu']
    print 'include aliquots:\n\t%s' % ('\n\t'.join([key + ': ' + ','.join(values) for key, values in platform2includes.iteritems()]))
    for participant in participant2sample2aliquot2ris:
        cellline = None
        epc = participant in excbarcodes
        redacted = None
        sample2aliquot2ris = participant2sample2aliquot2ris[participant]
        noSamples = True
        pplatforms = set()
        for sample in sample2aliquot2ris:
            if True == cellline and 2 > int(sample[13]):
                raise ValueError('samples were mixed for participant %s' % (participant))
            cellline = True if 2 <= int(sample[13]) else False
            aliquot2ris = sample2aliquot2ris[sample]
            for aliquot in aliquot2ris:
                splatforms = set()
                dnu = None
                ris = aliquot2ris[aliquot]
                for ri in ris:
                    redacted = isExcluded(ri, participant_excludes, redacted, participant)
                    dnu = isExcluded(ri, sample_excludes, dnu, aliquot)
                    pplatforms.add(ri.platform)
                    splatforms.add(ri.platform)
                if not (redacted and dnu):
                    noSamples = False
                for platform in splatforms:
                    override = override_aliquot(platform, platform2includes, platforms2platform, aliquot)
                    setBarcode(platforms2samples.setdefault(platform.lower(), [[set(), set()], [set(), set()]]), sample, override, cellline, epc, redacted, dnu)
        if noSamples:
            raise ValueError('there were no samples for participant %s' % (participant))
        annotation = getAnnotation(participant, cellline, epc, redacted, False)
        include = '\tExclude' if annotation else '\tInclude'
        annotation = '\t' + (annotation if annotation else 'NA')
        includeexclude += [participant + include + annotation + '\t' + ','.join(pplatforms) + '\n']

    includeexclude.sort()
    print 'distinct annotations:\n\tinclude:\n\t\t%s\n\texclude\n\t\t%s' % ('\n\t\t'.join(annotIncludes),'\n\t\t'.join(annotExcludes))
    print datetime.now(), 'done reading archive: %i total lines %i with no platform specified' % (count, countNoPlatform)
    return includeexclude, platforms2samples, participant2sample2aliquot2ris
    
if __name__ == '__main__':
    # ESCA.freeze.2014.83.txt
    main(sys.argv[1])
