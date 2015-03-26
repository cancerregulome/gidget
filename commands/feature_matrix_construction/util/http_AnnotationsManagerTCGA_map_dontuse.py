'''
Created on Mar 18, 2015

pulls down and reads through the TCGA annotation and returns a map
of patient or sample or aliquot id to [[annotationClassificationName, categoryName],...] 
of failed annotations only

@author: michael

json return layout
{
    "dccAnnotation":[ {
        "id":26882,
        "dateCreated":"2015-03-06T14:42:56-05:00",
        "createdBy":"LeraasK",
        "status":"Approved",
        "annotationCategory": {
            "categoryId":25,
            "categoryName":"Item may not meet study protocol",
            "annotationClassification": {
                "annotationClassificationId":1,
                "annotationClassificationName":"Observation"
            }
        },
        "items":[ {
            "item":"TCGA-HT-7483",
            "uuid":"183dd089-e932-4be2-b252-0e8572e7da4e",
            "itemType": {
                "itemTypeId":3,
                "itemTypeName":"Patient"
            },
            "disease": {
                "diseaseId":21,
                "abbreviation":"LGG",
                "description":"Brain Lower Grade Glioma"
            },
            "id":26338
        } ],
        "notes":[ {
            "noteId":26427,
            "noteText":"TSS confirmed that submitted tumor is a recurrence and patient had 2 prior resections before tumor submitted to BCR. Submitted tumor was in same tumor bed as primary. The patient had no prior chemo/radiation treatment. ",
            "addedBy":"LeraasK",
            "dateAdded":"2015-03-06T14:42:56-05:00"
        } ],
        "approved":true,
        "rescinded":false
    }
    ...
    ]
}

Annotation Classification    Id
Observation    1
CenterNotification    2
Notification    3
Redaction    5

Annotation Category    Id
*Redaction:Tumor tissue origin incorrect    1
*Redaction:Tumor type incorrect    2
*Redaction:Genotype mismatch    3
*Redaction:Subject withdrew consent    4
*Redaction:Subject identity unknown    5
Notification:Prior malignancy    6
Notification:Neoadjuvant therapy    7
Notification:Qualification metrics changed    8
Notification:Pathology outside specification    9
Notification:Molecular analysis outside specification    10
Notification:Duplicate item    11
Notification:Sample compromised    13
Notification:Clinical data insufficient    14
*Notification:Item does not meet study protocol    15
Notification:Item in special subset    17
Notification:Qualified in error    18
Notification:Item is noncanonical    21
Notification:New notification type    22
Observation:Tumor class but appears normal    23
Observation:Normal class but appears diseased    24
Observation:Item may not meet study protocol    25
Observation:New observation type    26
Redaction:Duplicate case    27
CenterNotification:Center QC failed    28
*CenterNotification:Item flagged DNU    29
Observation:General    30
Permanently missing item or object    36
Notification:WGA Failure    181
Normal tissue origin incorrect    35
Redaction:Administrative Compliance    37
*Notification:History of unacceptable prior treatment related to a prior/other malignancy    201
Notification:History of acceptable prior treatment related to a prior/other malignancy    202
Notification:Case submitted is found to be a recurrence after submission    203
Notification:Synchronous malignancy    204

*indicates do not include
'''
from datetime import datetime
import json
import urllib

def main():
    print datetime.now(), 'start parse don\'t use aliquots with reason'
    # get the annotations
    print '\t', datetime.now(), 'start fetch annotations'
    response = urllib.urlopen('https://tcga-data.nci.nih.gov/annotations/resources/searchannotations/json?')
    print '\t', datetime.now(), 'finish fetch annotations'

    print '\t', datetime.now(), 'start read annotations'
    annotations = json.loads(response.read())['dccAnnotation']
    print '\t', datetime.now(), 'finish read annotations'
    exclude_annotation_catagories = [1,2,3,4,5,15,29,201]
    barcode2annotation = {}
    count = 0
    count_bad = 0
    print '\t', datetime.now(), 'start check annotations'
    for annotation in annotations:
        if 0 == count % 2048:
            print '\t\tchecked %s annotations' % (count)
        count += 1
        annotationCategory = annotation['annotationCategory']
        if annotationCategory['categoryId'] in exclude_annotation_catagories:
            if not barcode2annotation.has_key(annotation['items'][0]['item']):
                count_bad += 1
            annotations = barcode2annotation.setdefault(annotation['items'][0]['item'], [])
            annotations += [annotationCategory['annotationClassification']['annotationClassificationName'], annotationCategory['categoryName']]
    print '\t', datetime.now(), 'finish check annotations--total %s, %s don\'t use' % (count, count_bad)

    print datetime.now(), 'finished parse don\'t use aliquots with reason'
    return barcode2annotation

if __name__ == '__main__':
    main()