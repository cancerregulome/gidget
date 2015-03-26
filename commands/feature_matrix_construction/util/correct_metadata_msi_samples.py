'''
Created on Mar 17, 2015

@author: michael
'''
from datetime import datetime
import sys
import http_AnnotationsManagerTCGA_map_dontuse

def use_barcode(barcode, barcode2annotation):
    if barcode in barcode2annotation or barcode[:16] in barcode2annotation or barcode[:15] in barcode2annotation or barcode[:12] in barcode2annotation:
        return False
    return True

def main(metadata_filename):
    print datetime.now(), 'start processing metadata to correct MSI samples'

    barcode2annotation = http_AnnotationsManagerTCGA_map_dontuse.main()
    
    sample2lines = {}
    sample2vials ={}
    with open(metadata_filename, 'r') as md:
        count = 0
        count_msi_not_default = 0
        count_msi_not_primary = 0
        msi_samples = set()
        print '\t', datetime.now(), 'begin reading %s' % (metadata_filename)
        header = md.readline()
        for line in md:
            if 0 == count % 16384:
                print '\t\tread %s lines' % (count)
            count += 1
            fields = line.split('\t')
            lines = sample2lines.setdefault(fields[1][:16], [])
            lines += [fields]
            vials_tumortype = sample2vials.setdefault(fields[1][:15], [set(), None])
            vials_tumortype[0].add(fields[6])
            if vials_tumortype[1] and vials_tumortype[1] != fields[3]:
                raise ValueError('tumor mismatch for %s: %s != %s' % (fields[1][:15], vials_tumortype[1], fields[3]))
            else:
                vials_tumortype[1] = fields[3]
            if fields[1].endswith('01A-01D-YYYY-23') or 'microsat_i' == fields[15]:
                if 'microsat_i' == fields[15] and not fields[1].endswith('01A-01D-YYYY-23'):
                    count_msi_not_default += 1
                if '01' != fields[1][13:15]:
                    count_msi_not_primary += 1
                msi_samples.add(fields[1][:16])
        print '\t', datetime.now(), 'read %s total lines' % (count)
        if 0 < count_msi_not_default:
            print '\tWARNING: %s out of %s of microsat_i samples didn\'t have expected ending of barcode' % (count_msi_not_default, len(msi_samples))
        if 0 < count_msi_not_primary:
            print '\tWARNING: %s out of %s of microsat_i samples weren\'t primary tumory' % (count_msi_not_primary, len(msi_samples))
    
    # verify that either sample count to vial == 1 or one is only an MSI sample to correct
    count_multivials = [0, 0, 0, 0]
    tumor2samples2vials2platforms = {}
    for sample, vials_tumortype in sample2vials.iteritems():
        if len(vials_tumortype[0]) > 1:
            # collect the information for each of the vials
            vial2platforms = {}
            for vial in vials_tumortype[0]:
                platforms_datatypes = []
                lines = sample2lines[sample + vial]
                for line in lines:
                    if line[15] and use_barcode(line[1], barcode2annotation):
                        platforms_datatypes += ["(" + str(line[15]) + "|" + str(line[16]) + ")"]
                if 0 < len(platforms_datatypes):
                    vial2platforms[vial] = platforms_datatypes
            if 1 < len(vial2platforms):
                # see if one of the vials represents the hard-coded MSI platform by itself and correct it, if so
                msi_vial = None
                msi_platform = None
                for vial, platforms in vial2platforms.iteritems():
                    if 1 == len(platforms) and 'microsat_i' in platforms[0]:
                        msi_vial = vial
                if msi_vial:
                    # add msi_vial info to one of the other vials after correcting the msi_vial letter in the barcode and vial columns
                    for vial in vials_tumortype[0]:
                        if vial != msi_vial:
                            use_vial = vial
                            break
                    print '=========converting %s for MSI to different vial %s=========' % (sample + msi_vial, sample + use_vial)
                    lines = []
                    for fields in sample2lines[sample + msi_vial]:
                        if not fields[1].endswith('01A-01D-YYYY-23'):
                            print 'found unexpected aliquot pattern for MSI conversion: %s' % (fields[1])
                        fields[1] = fields[1][:15] + use_vial + fields[1][16:]
                        fields[6] = use_vial
                        lines += [fields]
                        print 'converted %s from %s to %s' % (':'.join(fields), msi_vial, use_vial)
                    sample2lines[sample + msi_vial] = lines
                
                samples2vials2platforms = tumor2samples2vials2platforms.setdefault(line[3], {})
                samples2vials2platforms[sample] = vial2platforms
                index = len(vials_tumortype[0]) - 2 if 5 > len(vials_tumortype[0]) else 2
                count_multivials[index] += 1
                
    for tumor in tumor2samples2vials2platforms:
        print '\t%s:' % (tumor)
        for sample in tumor2samples2vials2platforms[tumor]:
            print '\t\t%s' % (sample)
            for vial in tumor2samples2vials2platforms[tumor][sample]:
                print '\t\t\t%s: %s' % (vial, tumor2samples2vials2platforms[tumor][sample][vial])
    mess = '['
    for index, count in enumerate(count_multivials):
        mess += '%s (%s), ' % (count, index + 2)
    mess = mess[:-2] + ']'
    print '\tWARNING: %s samples had more than one vial' % (mess)
        

    with open(metadata_filename, 'w') as md:
        count = 0
        print '\t', datetime.now(), 'begin writing %s' % (metadata_filename)
        md.write(header)
        for lines in sample2lines.itervalues():
            for fields in lines:
                if 0 == count % 16384:
                    print '\t\twrote %s lines' % (count)
                count += 1
                md.write('\t'.join(fields))
        print '\t', datetime.now(), 'wrote %s total lines' % (count)
    print datetime.now(), 'finished processing metadata to correct MSI samples'
            
if __name__ == '__main__':
    main(sys.argv[1])

# [119, 107, 25]
# [101, 93, 25] empty use removed
# [94, 91, 22] removed don't use annotation
# [89 (2), 91 (3), 22 (4)] fixed MSI sample vial