#!/usr/bin/env python

# this file parses the mutation summary output from binarization/genes_and_mutations_annovar.pl

import argparse
import csv
import os
import pymongo
import sys



def iterate_rows(file_path):
    with open(file_path, 'rb') as csvfile:
        # this file format does not have a header row
        csvreader = csv.reader(csvfile, delimiter='\t')

        parsed_row_count = 0
        skipped_row_count = 0

        for row in csvreader:
            
            # rows may have less columns if no mutatation data (UNIPROT_FAIL condition) 
            num_col_uniprotfail = 8
            num_col_mutationinfo = 11
            if not ((len(row) == num_col_uniprotfail) or (len(row) == num_col_mutationinfo)):
                print "skipping row due to unexpected number of columns ({})".format(len(row))
                skipped_row_count += 1
                continue



            # example data:
            # LGG     RGS21   Missense_Mutation       TCGA-..-....    Q2M5E4  L32I    32      L       I
            # LGG     KDM6B   Silent  TCGA-..-....    O15054  P335P   335     P       P
            # LGG     C3      Nonsense_Mutation      TCGA-..-....    P01024  Q1184X  1184    Q       X
            # LGG     NBL1    Silent  TCGA-..-....    UNIPROT_FAIL    UNIPROT_FAIL

            mutation_summary_row = {
                'description': None, # sometimes tumor_text, sometimes other uses by b2
                'hugo_symbol': None,
                'variant_classification': None,
                'tumor_sample_barcode': None,
                'coordinates': {
                    'chromosome': None,
                    'start_position': None,              
                },
                'reference_allele': None,
                'tumor_seq_allele1': None,
                'uniprot': None,
                'mutation_info': None  # if NOT uniprot fail, this may be present as {
                #     'mutation': None,
                #     'aa_position': None,
                #     'wildtype_aa': None,
                #     'mutated_aa': None
                # }
            }
            mutation_summary_row['description'] = row[0] 
            mutation_summary_row['hugo_symbol'] = row[1]
            mutation_summary_row['variant_classification'] = row[2]
            mutation_summary_row['tumor_sample_barcode'] = row[3]

            coordinate_text = row[4]
            coordinate_info = coordinate_text.split(':')
            mutation_summary_row['coordinates']['chromosome'] = coordinate_info[0]
            mutation_summary_row['coordinates']['start_position'] = coordinate_info[1]

            allele_text = row[5]
            allele_info = allele_text.split("->")
            mutation_summary_row['reference_allele'] = allele_info[0]
            mutation_summary_row['tumor_seq_allele1'] = allele_info[1]

            # mutation, aa_position fields may be both "UNIPROT_FAIL", which means there are no futher columns
            # if so, these will not appear: wildtype_aa, mutated_aa
            column7 = row[6]
            column8 = row[7]

            uniprot_fail = False
            if (column7 == "UNIPROT_FAIL") and (column8 == "UNIPROT_FAIL"):
                uniprot_fail = True
                # we leave both 'uniprot' and 'mutation_info' as None
            else:
                # okay to parse mutation info
                mutation_summary_row['uniprot'] = column7
                mutation_info = {}

                mutation_info['mutation'] = column8
                mutation_info['aa_position'] = row[8]
                mutation_info['wildtype_aa'] = row[9]
                mutation_info['mutated_aa'] = row[10]

                mutation_summary_row['mutation_info'] = mutation_info

            parsed_row_count += 1
            print mutation_summary_row
            yield mutation_summary_row

        info = ' {0:10} rows parsed'.format(parsed_row_count)
        info += ' {0:10} rows skipped'.format(skipped_row_count)
        print('   ' + info)


def connect_database(hostname, port):
    connection = pymongo.Connection(hostname, port)
    return connection


def main():
    parser = argparse.ArgumentParser(description="TCGA mutation summary to MongoDB import utility")
    parser.add_argument('--mut_summary_path', required=True, help='Path to mutation summary file')
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

    for mutation_summary_row in iterate_rows(args.mut_summary_path):
        collection.insert(mutation_summary_row)

    conn.close()


if __name__ == "__main__":
    main()

