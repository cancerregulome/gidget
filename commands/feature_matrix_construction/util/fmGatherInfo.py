'''
Created on Dec 24, 2013

@author: michael
'''
from datetime import datetime
import json
import sys
import traceback

def formatStats(counts, nums, cat, cats):
    stats = '{"valid": %i, "total": %i}\t' % (counts[0], counts[1])
    try:
        minmax = '{"minimum": %i, "maximum": %i, "mean": %.2f}' % (nums[0], nums[1], nums[2] / float(counts[0]))
        stats += minmax
    except:
        pass
    stats += '\t'
    
    try:
        if (20 >= len(cats) and 0 < len(cats)) or cat:
            catcounts = '{'
            for key, count in cats.iteritems():
                try:
                    # BUGBUG: mongo json doesn't like '.' in key names for numbers???
                    key = int(round(float(key)))
                except:
                    key = key.replace('.', '')
                catcounts += '"%s": %i,' % (key, count)
            catcounts = catcounts[:-1]
            catcounts += '}'
            stats += catcounts
    except:
        traceback.print_exc()
        print '!!!EXCEPTION!!!'
        pass
    
    return stats

def getStats(num, cat, values):
    counts = [0, 0]
    nums = [values[0], values[0], 0] if num else None
    cats = {}
    for value in values:
        value = value.strip()
        counts[1] += 1
        if 'NA' == value:
            continue
        counts[0] += 1
        curCount = cats.setdefault(value, 0)
        cats[value] = curCount + 1
        
        if num:
            fvalue = float(value)
            nums[0] = fvalue if fvalue < nums[0] else nums[0]
            nums[1] = fvalue if fvalue > nums[1] else nums[1]
            nums[2] += fvalue

    return formatStats(counts, nums, cat, cats)

#   "id": "<feature_name>",
#   "label": "<feature_name>.split(':')[2]"
#   "name": "<feature_name>.split(':')[2]",
#   "dtype": "<feature_name>.split(':')[0]",
#   "data_type": "<Expanded DType ('B' -> 'Boolean', 'C' -> 'Categorical', 'N' -> 'Numerical')>",
#   "ftype": "<feature_name>.split(':')[1]",
#   "feature_type": "<expanded FType ('CNVR' -> 'Copy Number', 'GEXP' -> 'Gene expression', 'MIRN' -> 'MicroRNA', 'GNAB' -> 'Mutation', 'METH' -> 'Methylation')>",
#   "description": "<from gene database>",
#   "chromosome": "<feature_name>.split(':')[3]",
#   "start postion": "<feature_name>.split(':')[4]",
#   "end position": "<feature_name>.split(':')[5]",
#   "strand": "<feature_name>.split(':')[6]",
#   <note, the meaning of the annotation changes between different platforms so this may be more specialized>
#   "annotation": "<feature_name>.split(':')[7]", 
def annotClinical(config, out, fnfields, values, datatypemap, featuretypemap):
    stats = getStats('N' == fnfields[0], 'C' == fnfields[0], values)
    annot = '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t\t\t\t\t\t%s\n' % (':'.join(fnfields), fnfields[2], fnfields[2], fnfields[0], datatypemap[fnfields[0]], fnfields[1], featuretypemap[fnfields[1]], '', stats)
    out.write(annot)

def annotGenomic(config, out, fnfields, values, datatypemap, featuretypemap):
    stats = getStats('N' == fnfields[0], 'C' == fnfields[0], values)
    annot = '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % \
        (':'.join(fnfields), fnfields[2], fnfields[2], fnfields[0], datatypemap[fnfields[0]], fnfields[1], featuretypemap[fnfields[1]], '', fnfields[3], fnfields[4], fnfields[5], fnfields[6], fnfields[7], stats)
    out.write(annot)

def main(configName, tsvFile, outFile):
    print 'args:\n\tconfigName=%s\n\ttsvFile=%s\n\toutFile=%s' % (configName, tsvFile, outFile)
    config = json.load(open(configName, 'r'))
    print 'parameters:\n%s' % (json.dumps(config, indent=4))
    globalself = __import__(__name__)
    datatypemap = config['datatypemap']
    featuretypemap = config['featuretypemap']
    ftype2method = config['ftype2method']
    
    if not tsvFile:
        tsvFile = config['fmFileName']
    if not outFile:
        outFile = config['outFileName']
    with open(tsvFile, 'r') as fm, open(outFile, 'w') as out:
        fm.readline()
        out.write('\t'.join(config['header']) + '\n')
        count = 0
        for line in fm:
            if 0 == count % 8192:
                sys.stdout.write(".")
                sys.stdout.flush()
            count += 1
            fields = line.split('\t')
            fname = fields[0]
            fnfields = fname.split(':')
            values = fields[1:]
            getattr(globalself, ftype2method[fnfields[1]])(config, out, fnfields, values, datatypemap, featuretypemap)
        print '\nannotated %s lines' % (count)

if __name__ == '__main__':
    print datetime.now(), 'starting annotation of feature matrix'
    tsvFile = None
    if len(sys.argv) > 2:
        tsvFile = sys.argv[2]
    outFile = None
    if len(sys.argv) > 3:
        outFile = sys.argv[3]
    elif tsvFile:
        index = tsvFile.rfind('.')
        outFile = tsvFile[:index] + '.ANNOT' + tsvFile[index:]
    main(sys.argv[1], tsvFile, outFile)
    print datetime.now(), 'finished annotation of feature matrix'
    