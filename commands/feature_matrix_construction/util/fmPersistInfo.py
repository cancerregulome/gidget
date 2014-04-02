'''
Created on Oct 23, 2013

@author: michael

'''
from datetime import datetime
import json
import pymongo
import sys
import traceback

def getCollection(config):
    print '\topening mongo collection'
    host = config['host']
    port = int(config['port'])
    conn = pymongo.Connection(host, port)
    database = config['database']
    dropdb = True
    if 'drop_db' in config:
        dropdb = config['drop_db']
    if dropdb:
        try:
            conn.drop_database(database)
            print '\tdropped database %s' % (database)
        except TypeError:
            pass # if db doesn't exist
        except:
            traceback.print_exc()
            raise ValueError('problem deleting database %s' % (database))
    collection = config['collection']
    collection = conn[database][collection]
    return conn, collection

def processLine(header, line, int_fields, bool_fields, map_fields):
    try:
        copy = header[:]
        fields = line.split('\t')[:len(copy)]
        fields[-1] = fields[-1].strip()
        remove = []
        for index in range(len(fields)):
            if not fields[index]:
                remove += [index]
            elif index in int_fields:
                fields[index] = int(fields[index])
            elif index in bool_fields:
                if fields[index].lower() == 'true':
                    fields[index] = True
                elif fields[index].lower() == 'false':
                    fields[index] = False
                else:
                    ValueError('unexpected value for boolean: %s' % (fields[index]))
            elif index in map_fields:
                fields[index] = json.loads(fields[index])
        
        remove.reverse()
        for index in remove:
            del copy[index]
            del fields[index]
    except:
        traceback.print_exc()
        raise ValueError('problem writing line: %s %i' % (fields, index))
            
    return copy, fields


def validateInsert(config, objectIDs, inserts, collection):
    if len(objectIDs) != len(inserts):
        print 'unexpected number of successful inserts: %s vs. %s' % (len(objectIDs), len(inserts))
    if collection.count() != len(inserts):
        print 'unexpected count of successful inserts: %s vs. %s' % (collection.count(), len(inserts))
    ftypes = config['featuretypemap'].keys()
    results = 0
    for ftype in ftypes:
        results += collection.find({'ftype': ftype}).count()
    if results != len(inserts):
        print 'unexpected query count of successful inserts: %s vs. %s' % (results, len(inserts))

def writeCollection(config, outFile, collection):
    int_fields = config['int_fields']
    bool_fields = config['bool_fields']
    map_fields = config['dict_fields']
    print '\twriting documents from %s' % (outFile)
    with open(outFile, 'r') as ffile:
        header = ffile.readline().strip().split('\t')
        print '\theader: %s' % (header)
        inserts = []
        for line in ffile:
            headers, fields = processLine(header, line, int_fields, bool_fields, map_fields)
            inserts += [dict([(key, value) for (key, value) in zip(headers, fields)])]
        print '\tinserts(%i): %s\n\t\t\t...%s\n' % (len(inserts), '\n\t\t' + '\n\t\t'.join([str(value) for value in inserts[:4]]), '\n\t\t' + '\n\t\t'.join([str(value) for value in inserts[-3:]]))
        objectIDs = []
        count = 0
        for insert in inserts:
            if 0 == count % 8192:
                print '\t\tinserted %i records' % count
            count += 1
            try:
                objectIDs += [collection.insert(insert)]
            except:
                traceback.print_exc()
                raise ValueError('problem with insert(%i): %s' % (count, insert))
#        objectIDs = collection.insert(inserts)
    validateInsert(config, objectIDs, inserts, collection)
    print '\tinserted %i total records' % count
    print '\tdocument: %s' % (collection.find_one())
    return header


def writeIndices(config, collection, header):
    indices = config['reg_indices']
    for index in indices:
        collection.create_index((header[int(index)]))
    
    print '\tindices: %s' % (collection.index_information())

def main(configName, outFile):
    print 'args:\n\tconfigName=%s\n\toutFile=%s' % (configName, outFile)
    config = json.load(open(configName, 'r'))
    print 'parameters:\n%s' % (json.dumps(config, indent=4))
    conn, collection = getCollection(config)
    header = writeCollection(config, outFile, collection)
    writeIndices(config, collection, header)
    conn.close()

    print datetime.now(), 'finished persisting features to mongodb.  inserted %i documents' % (collection.count())

if __name__ == '__main__':
    print datetime.now(), 'starting saving annotation of feature matrix'
    outFile = None
    if len(sys.argv) > 2:
        outFile = sys.argv[2]
    main(sys.argv[1], outFile)
    print datetime.now(), 'finished saving annotation of feature matrix'
