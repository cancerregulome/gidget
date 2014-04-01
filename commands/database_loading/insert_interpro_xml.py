# Depends on lxml
#    http://pypi.python.org/pypi/lxml/
#    easy_install lxml

import argparse
import gzip
import pymongo
import sys

from lxml import etree


INCLUDE_DATABASES = set(['PFAM', 'SMART', 'PROFILE'])
PROTEIN_MATCH_TAGS = set(['ipr', 'lcn'])


def connect_database(hostname, port):
    connection = pymongo.Connection(hostname, port)
    return connection


def process_protein_flat(element):
    protein_id = element.attrib['id']
    matches = []

    for match_elem in element:
        if ((match_elem.tag != 'match') or (match_elem.attrib['dbname'] not in INCLUDE_DATABASES)):
            continue

        match = dict(match_elem.attrib)
        match['locations'] = []

        for lcn in match_elem:
            if (lcn.tag != 'lcn'):
                continue

            location = dict()
            location['start'] = int(lcn.attrib['start'])
            location['end'] = int(lcn.attrib['end'])
            location['score'] = float(lcn.attrib['score'])

            match['locations'].append(location)

        matches.append(match)

    return({'uniprot_id': protein_id,
        'name': element.attrib['name'],
        'length': int(element.attrib['length']),
        'matches': matches})


def process_protein_hierarchical(element):
    protein_id = element.attrib['id']
    match_dict = {}

    for match_elem in element:
        if ((match_elem.tag != 'match') or (match_elem.attrib['dbname'] not in INCLUDE_DATABASES)):
            continue

        match = None
        if match_elem.attrib['id'] in match_dict:
            match = match_dict[match_elem.attrib['id']]
        else:
            match = dict(match_elem.attrib)
            match_dict[match_elem.attrib['id']] = match_elem

        if 'locations' not in match:
            match['locations'] = []

        for child_elem in match_elem:
            if child_elem.tag not in PROTEIN_MATCH_TAGS:
                continue

            if child_elem.tag == 'ipr':
                if 'ipr' in match:
                    continue
                else:
                    match['ipr'] = dict(child_elem.attrib)

            if (child_elem.tag == 'lcn'):
                location = dict()
                location['start'] = int(child_elem.attrib['start'])
                location['end'] = int(child_elem.attrib['end'])
                location['score'] = float(child_elem.attrib['score'])

                match['locations'].append(location)

        match_dict[match['id']] = match

    return({'uniprot_id': protein_id,
        'name': element.attrib['name'],
        'length': int(element.attrib['length']),
        'matches': match_dict.values()
        })


def main():
    parser = argparse.ArgumentParser(description="InterPro XML to MongoDB import utility")
    parser.add_argument('--interpro-file', required=True, help='XML file containing InterPro entries. File type must be either \'.xml\' or \'.gz\'.')
    parser.add_argument('--host', required=True, help='hostname')
    parser.add_argument('--port', required=True, type=int, help='port')
    parser.add_argument('--db', required=True, help='database name')
    parser.add_argument('--collection', required=True, help='collection name')
    parser.add_argument('--process', default='hierarchical', choices=['hierarchical', 'flat'])

    args = parser.parse_args()

    # Connect to MongoDB
    conn = connect_database(args.host, args.port)
    collection = conn[args.db][args.collection]

    progress_interval = 50000
    counter = 0
    total_count = 0

    filehandle = None
    filetype = args.interpro_file.lower().rsplit('.', 1)[1]

    if (filetype == 'gz'):
        filehandle = gzip.open(args.interpro_file, 'r')
    elif (filetype == 'xml'):
        filehandle = open(args.interpro_file, 'r')

    context = etree.iterparse(filehandle, events=('end',), tag='protein')

    process_fn = None
    if args.process == 'flat':
        process_fn = process_protein_flat
    elif args.process == 'hierarchical':
        process_fn = process_protein_hierarchical
    else:
        print("ERROR: Unknown process")
        sys.exit(1)

    for event, element in context:
        protein_data = process_fn(element)
        collection.insert(protein_data)
        element.clear()

        while element.getprevious() is not None:
            del element.getparent()[0]

        counter = counter + 1
        total_count = total_count + 1

        if counter == progress_interval:
            counter = 0
            print('{0:15d} records'.format(total_count))

    conn.close()
    filehandle.close()
    print("Inserted " + str(total_count) + " records in total.")


if __name__ == '__main__':
    main()
