#!/usr/bin/env python

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
            cell_tpl = feature_id_extract(feature_id)

            values = row[1:]
            if len(values) != len(ids):
                print('   Skipping feature (' + len(values) + '/' + len(ids) + ')' + feature_id)
                skipped += 1
                continue

            data_by_sample = {}
            if cell_tpl['type'] == 'N':
                data_by_sample = build_value_dict_numerical(ids, values)
            else:
                data_by_sample = build_value_dict_categorical(ids, values)

            for sample_id in data_by_sample:
                value_item  = data_by_sample[sample_id]

                feature_cell = cell_tpl.copy()
                feature_cell["feature_id"] = feature_id
                feature_cell["sample_id"] = sample_id
                feature_cell["value"] = value_item
                count += 1
                yield feature_cell

        print('\t{0:10} samples'.format(len(ids)))
        print('\t{0:10} datapoints'.format(count))
        print('\t{0:10} skipped'.format(skipped))

def main():
    parser = argparse.ArgumentParser(description="TCGA feature matrix to MongoDB import utility")
    parser.add_argument('--fmx', required=True, help='Path to feature matrix file')
    parser.add_argument('--host', required=True, help='Hostname')
    parser.add_argument('--port', required=True, type=int, help='Port')
    parser.add_argument('--db', required=True, help='Database name')
    parser.add_argument('--collection', required=True, help='Collection name')
    args = parser.parse_args()

    conn = pymongo.Connection(args.host, args.port)
    collection = conn[args.db][args.collection]

    print "args.fmx=%s" % args.fmx
    for feature_object in iterate_features({ "path": args.fmx }):
        collection.insert(feature_object)
    conn.close()

if __name__ == "__main__":
    main()
