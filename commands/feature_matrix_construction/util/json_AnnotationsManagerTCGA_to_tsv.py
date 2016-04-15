import csv
import json
import sys


def load_json(filename):
    return json.load(open(filename, 'r'))


def process_notetext(notetext):
    ## NEW ... problems with unicode characters on 12-oct-2014
    notetext = notetext.encode('ascii', 'ignore')
    ## print " in process_notetext ... <%s> " % notetext
    return notetext.replace('\r\n', ';').replace('\n', ';').strip()


def get_header_fields():
    return [
        "ID",
        "Disease",
        "Item Type",
        "Item Barcode",
        "Annotation Classification",
        "Annotation Category",
        "Annotation Notes",
        "Date Created",
        "Created By",
        "Status"
    ]

# ----------------------------------------------------------------------------
# NOTE: used formatter/validator at http://jsonformatter.curiousconcept.com/
#
# {
# u'status':u'Approved',
# u'rescinded':False,
# u'annotationCategory':{
# u'annotationClassification':{
# u'annotationClassificationName':u'CenterNotification',
# u'annotationClassificationId':2
# },
# u'categoryId':29,
# u'categoryName':u'Item flagged DNU'
# },
# u'notes':[
# {
# u'noteText':u"SDRF in broad.mit.edu_STAD.Genome_Wide_SNP_6.mage-tab.1.2008.0 flagged aliquot to be excluded for analysis based on file 'SLITS_p_TCGA_b95_SNP_N_GenomeWideSNP_6_F01_764190.tangent.copynumber.data.txt'.",
# u'dateAdded':         u'2013-10-22T19:49:38-04:00         ', u'         noteId':18085,
# u'addedBy':u'DCC'
# }
# ],
# u'dateCreated':   u'2013-10-22T19:49:38-04:00   ', u'   createdBy':u'DCC',
# u'items':[
# {
# u'id':18058,
# u'item':u'TCGA-CD-5813-01A-11D-1599-01',
# u'itemType':{
# u'itemTypeName':u'Aliquot',
# u'itemTypeId':1
# },
# u'disease':{
# u'diseaseId':9,
# u'abbreviation':u'STAD',
# u'description':u'Stomach adenocarcinoma'
# }
# }
# ],
# u'id':18602,
# u'approved':True
# }
# ----------------------------------------------------------------------------


def build_tsv_row_generator(annotation_list):

    # print "         working on annotation_list ... length=%d " % ( len(annotation_list) )
    # print "         example : ", annotation_list[0]

    for annotation in annotation_list:

        ## print ( json.dumps ( annotation, sort_keys=True, indent=4 ) )

        # id int
        annotation_id = int(annotation['id'])

        # disease name (STAD etc)

        if (len(annotation['items']) != 1):
            print " ERROR ... we are assuming that this is a list of length 1 !!! "
            sys.exit(-1)

        disease_name = annotation['items'][0]['disease']['abbreviation']

        # item type (aliquot etc)
        item_type = annotation['items'][0]['itemType']['itemTypeName']

        # item barcode
        item_barcode = annotation['items'][0]['item']

        # annotation classification name
        classification = annotation['annotationCategory'][
            'annotationClassification']['annotationClassificationName']

        # annotation category name
        category = annotation['annotationCategory']['categoryName']

        # date created
        date_created = annotation['dateCreated']

        # annotator
        annotator = annotation['createdBy']

        # status
        status = annotation['status']

        # Produce one row for every note in the annotation
        annotation_descriptions = []
        if ('notes' in annotation):
            #print(json.dumps(annotation, sort_keys=True, indent=4))
            notes = annotation['notes']

            # If the annotation has only one note, it will be an object
            if type(notes) is dict:
                notetext = process_notetext(notes['noteText'])
                annotation_descriptions.append(notetext)

            # If the annotation has more than one note, there will be an array
            # of objects
            if type(notes) is list:
                for n in notes:
                    notetext = process_notetext(n['noteText'])
                    annotation_descriptions.append(notetext)

        else:
            annotation_descriptions.append("")

        for descr in annotation_descriptions:
            yield [
                annotation_id,
                disease_name,
                item_type,
                item_barcode,
                classification,
                category,
                descr,
                date_created,
                annotator,
                status
            ]


def process_data(data, outfilename):

    # print " "
    # print " in process_data ... "

    # Windows: Opening in binary mode 'wb' will produce '\r\n' line breaks, whereas 'wt' will produce '\r\r\n'
    # Linux: TODO
    csv_file = open(outfilename, 'wt')
    csv_writer = csv.writer(csv_file, delimiter='\t',
                            quotechar='\"', quoting=csv.QUOTE_ALL)

    row_gen = build_tsv_row_generator(data)

    # Write header on first row of output file
    csv_writer.writerow(get_header_fields())

    for row in row_gen:
        csv_writer.writerow(row)

    csv_file.close()


def main():
    infile = sys.argv[1]
    outfile = sys.argv[2]

    print " input file  : <%s> " % infile
    print " output file : <%s> " % outfile

    print " calling load_json ... "
    json_data = load_json(infile)
    print " DONE "

    # NOTE: 13nov13 took this outside of the "try" so that we can see
    # where/why it crashes if it does ...
    print " calling process_data ... "
    process_data(json_data['dccAnnotation'], outfile)

# try:
# print " calling process_data ... "
##        process_data(json_data['dccAnnotation'], outfile)
# print " DONE "
# except:
# print " "
# print " ERROR processing dccAnnotation data "
# print " "


if __name__ == '__main__':
    main()
