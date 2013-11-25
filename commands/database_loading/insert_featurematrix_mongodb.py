import argparse
import csv
import os
import pymongo
import sys


def feature_id_extract(feature):
    feature_parts = feature.split(":")
    source = feature_parts[1].lower()

    if "chr" in feature_parts[3]:
        start = feature_parts[4]
        end = feature_parts[5]
        if not start:
            start = -1
        if not end:
            end = -1

        return {
            "id": feature,
            "type": feature_parts[0],
            "source": source,
            "gene": feature_parts[2].lower(),
            "label": feature_parts[2],
            "chr": feature_parts[3][3:],
            "start": int(start),
            "end": int(end),
            "strand": feature_parts[6],
            "modifier": feature_parts[7]
        }

    return {
        "id": feature,
        "type": feature_parts[0],
        "source": source,
        "label": feature_parts[2],
        "modifier": feature_parts[7]
    }


def iterate_fmx_files(dir_path):
    for filename in os.listdir(dir_path):
        # Suppose that file name format is '<cancer>.<name>.<date>.tsv',
        # for example 'blca.newMerge.05nov.tsv'
        fileparts = filename.strip().lower().split('.')
        if (len(fileparts) != 4):
            continue

        subtype = fileparts[0]
        name = fileparts[1]
        filedate = fileparts[2]
        filetype = fileparts[3]

        if filetype == 'tsv':
            yield {
            'subtype': subtype,
            'name': name,
            "date": filedate,
            'path': os.path.join(dir_path, filename)
            }


def build_value_dict_categorical(ids, values):
    result = {}
    for i, v in zip(ids, values):
            result[i] = v

    return result


def build_value_dict_numerical(ids, values):
    result = {}
    for i, v in zip(ids, values):
        if v == 'NA':
            result[i] = v
        else:
            result[i] = float(v)

    return result


def iterate_features(descriptor):
    file_path = descriptor['path']
    with open(file_path, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='\t')

        ids = csvreader.next()[1:]

        print('Processing ' + file_path)

        count = 0
        skipped = 0

        for row in csvreader:
            feature_id = row[0]
            values = row[1:]

            if len(values) != len(ids):
                print('   Skipping feature (' + len(values) + '/' + len(ids) + ')' + feature_id)
                skipped += 1
                continue

            feature_object = feature_id_extract(feature_id)
            feature_object['cancer'] = descriptor['subtype']

            if feature_object['type'] == 'N':
                feature_object['values'] = build_value_dict_numerical(ids, values)
            else:
                feature_object['values'] = build_value_dict_categorical(ids, values)

            count += 1

            yield feature_object

        info = '{0:10} IDs'.format(len(ids))
        info += ' {0:10} features'.format(count)
        info += ' {0:10} skipped'.format(skipped)
        print('   ' + info)


def connect_database(hostname, port):
    connection = pymongo.Connection(hostname, port)
    return connection


def main():
    parser = argparse.ArgumentParser(description="TCGA feature matrix to MongoDB import utility")
    parser.add_argument('--fmx-dir', required=True, help='Path to directory containing the feature matrices')
    parser.add_argument('--host', required=True, help='Hostname')
    parser.add_argument('--port', required=True, type=int, help='Port')
    parser.add_argument('--db', required=True, help='Database name')
    parser.add_argument('--collection', required=True, help='Collection name')

    args = parser.parse_args()

    # Try open connection first, exit in case of failure
    conn = None
    try:
        conn = connect_database(args.host, args.port)
    except pymongo.errors.ConnectionFailure:
        print("Failed to connect to database at " + args.host + ":" + str(args.port))
        sys.exit(1)

    collection = conn[args.db][args.collection]

    for fmx_descriptor in iterate_fmx_files(args.fmx_dir):
        for feature_object in iterate_features(fmx_descriptor):
            collection.insert(feature_object)

    conn.close()


if __name__ == "__main__":
    main()
