# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscClin
import tsvIO

import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

remapDict = {}

DAYS_PER_YEAR = 365.2425

# ------------------------------------------------------------------------- ##
# DEPENDING ON WHICH TUMOR TYPE IS BEING PROCESSED, THESE SWITCHES MAY
# NEED TO BE CHANGED ...

remapDict["anatomic_organ_subdivision"] = {}

if (1):
    remapDict["anatomic_organ_subdivision"]["na"] = "NA"
    remapDict["anatomic_organ_subdivision"]["rectum"] = 0
    remapDict["anatomic_organ_subdivision"]["rectosigmoid_junction"] = 1
    remapDict["anatomic_organ_subdivision"]["sigmoid_colon"] = 2
    remapDict["anatomic_organ_subdivision"]["descending_colon"] = 3
    remapDict["anatomic_organ_subdivision"]["splenic_flexure"] = 4
    remapDict["anatomic_organ_subdivision"]["transverse_colon"] = 5
    remapDict["anatomic_organ_subdivision"]["hepatic_flexure"] = 6
    remapDict["anatomic_organ_subdivision"]["ascending_colon"] = 7
    remapDict["anatomic_organ_subdivision"]["cecum"] = 8

if (0):
    remapDict["anatomic_organ_subdivision"]["na"] = "NA"
    remapDict["anatomic_organ_subdivision"]["bilateral"] = "bilateral"
    remapDict["anatomic_organ_subdivision"]["left"] = "left"
    remapDict["anatomic_organ_subdivision"]["right"] = "right"

if (0):
    remapDict["anatomic_organ_subdivision"][""] = "NA"
    remapDict["anatomic_organ_subdivision"]["na"] = "NA"
    remapDict["anatomic_organ_subdivision"]["brain"] = "brain"

remapDict["histological_type"] = {}

if (0):
    remapDict["histological_type"]["na"] = "NA"
    remapDict["histological_type"]["colon_adenocarcinoma"] = 0
    remapDict["histological_type"]["rectal_adenocarcinoma"] = 0
    remapDict["histological_type"]["colon_mucinous_adenocarcinoma"] = 1
    remapDict["histological_type"]["rectal_mucinous_adenocarcinoma"] = 1

if (0):
    remapDict["histological_type"]["na"] = "NA"
    remapDict["histological_type"][
        "untreated_primary_(de_novo)_gbm"] = "de_novo"
    remapDict["histological_type"]["treated_primary_gbm"] = "primary"

remapDict["ethnicity"] = {}
remapDict["ethnicity"]["hispanic_or_latino"] = "hispanic"
remapDict["ethnicity"]["not_hispanic_or_latino"] = "not_hispanic"

# ------------------------------------------------------------------------- ##

remapDict["tumor_grade"] = {}
remapDict["tumor_grade"]["na"] = "NA"
remapDict["tumor_grade"]["gx"] = "NA"
remapDict["tumor_grade"]["gb"] = "NA"
remapDict["tumor_grade"]["g1"] = 1
remapDict["tumor_grade"]["g2"] = 2
remapDict["tumor_grade"]["g3"] = 3
remapDict["tumor_grade"]["g4"] = 4
remapDict["tumor_grade"]["high grade"] = 3  # ???
remapDict["tumor_grade"]["high_grade"] = 3  # ???

if (0):
    remapDict["tumor_stage"] = {}
    remapDict["tumor_stage"]["na"] = "NA"
    remapDict["tumor_stage"]["i"] = 1
    remapDict["tumor_stage"]["ia"] = 1.2
    remapDict["tumor_stage"]["ib"] = 1.4
    remapDict["tumor_stage"]["ic"] = 1.6
    remapDict["tumor_stage"]["ii"] = 2
    remapDict["tumor_stage"]["iia"] = 2.2
    remapDict["tumor_stage"]["iib"] = 2.4
    remapDict["tumor_stage"]["iic"] = 2.6
    remapDict["tumor_stage"]["iii"] = 3
    remapDict["tumor_stage"]["iiia"] = 3.2
    remapDict["tumor_stage"]["iiib"] = 3.4
    remapDict["tumor_stage"]["iiic"] = 3.6
    remapDict["tumor_stage"]["iv"] = 4
    remapDict["tumor_stage"]["iva"] = 4.2
    remapDict["tumor_stage"]["ivb"] = 4.4
    remapDict["tumor_stage"]["ivc"] = 4.6

remapDict["breast_tumor_pathologic_grouping_stage"] = {}
remapDict["breast_tumor_pathologic_grouping_stage"]["na"] = "NA"
remapDict["breast_tumor_pathologic_grouping_stage"]["x"] = "NA"
remapDict["breast_tumor_pathologic_grouping_stage"]["tis"] = 0.5
remapDict["breast_tumor_pathologic_grouping_stage"]["i"] = 1
remapDict["breast_tumor_pathologic_grouping_stage"]["ia"] = 1.2
remapDict["breast_tumor_pathologic_grouping_stage"]["ib"] = 1.4
remapDict["breast_tumor_pathologic_grouping_stage"]["ii"] = 2
remapDict["breast_tumor_pathologic_grouping_stage"]["iia"] = 2.2
remapDict["breast_tumor_pathologic_grouping_stage"]["iib"] = 2.4
remapDict["breast_tumor_pathologic_grouping_stage"]["iic"] = 2.6
remapDict["breast_tumor_pathologic_grouping_stage"]["iii"] = 3
remapDict["breast_tumor_pathologic_grouping_stage"]["iiia"] = 3.2
remapDict["breast_tumor_pathologic_grouping_stage"]["iiib"] = 3.4
remapDict["breast_tumor_pathologic_grouping_stage"]["iiic"] = 3.6
remapDict["breast_tumor_pathologic_grouping_stage"]["iv"] = 4

remapDict["primary_tumor_pathologic_spread"] = {}
remapDict["primary_tumor_pathologic_spread"]["na"] = "NA"
remapDict["primary_tumor_pathologic_spread"]["tx"] = "NA"
remapDict["primary_tumor_pathologic_spread"]["t0"] = 0
remapDict["primary_tumor_pathologic_spread"]["tis"] = 0.5
remapDict["primary_tumor_pathologic_spread"]["t1"] = 1
remapDict["primary_tumor_pathologic_spread"]["t1a"] = 1.2
remapDict["primary_tumor_pathologic_spread"]["t1b"] = 1.4
remapDict["primary_tumor_pathologic_spread"]["t2"] = 2
remapDict["primary_tumor_pathologic_spread"]["t2a"] = 2.2
remapDict["primary_tumor_pathologic_spread"]["t2b"] = 2.4
remapDict["primary_tumor_pathologic_spread"]["t3"] = 3
remapDict["primary_tumor_pathologic_spread"]["t3a"] = 3.2
remapDict["primary_tumor_pathologic_spread"]["t3b"] = 3.4
remapDict["primary_tumor_pathologic_spread"]["t3c"] = 3.6
remapDict["primary_tumor_pathologic_spread"]["t4"] = 4
remapDict["primary_tumor_pathologic_spread"]["t4a"] = 4.2
remapDict["primary_tumor_pathologic_spread"]["t4b"] = 4.4

remapDict["breast_tumor_pathologic_t_stage"] = {}
remapDict["breast_tumor_pathologic_t_stage"]["na"] = "NA"
remapDict["breast_tumor_pathologic_t_stage"]["tx"] = "NA"
remapDict["breast_tumor_pathologic_t_stage"]["t1"] = 1
remapDict["breast_tumor_pathologic_t_stage"]["t1a"] = 1.2
remapDict["breast_tumor_pathologic_t_stage"]["t1b"] = 1.4
remapDict["breast_tumor_pathologic_t_stage"]["t1c"] = 1.6
remapDict["breast_tumor_pathologic_t_stage"]["t2"] = 2
remapDict["breast_tumor_pathologic_t_stage"]["t2a"] = 2.2
remapDict["breast_tumor_pathologic_t_stage"]["t2b"] = 2.4
remapDict["breast_tumor_pathologic_t_stage"]["t2c"] = 2.6
remapDict["breast_tumor_pathologic_t_stage"]["t3"] = 3
remapDict["breast_tumor_pathologic_t_stage"]["t3a"] = 3.4
remapDict["breast_tumor_pathologic_t_stage"]["t3b"] = 3.4
remapDict["breast_tumor_pathologic_t_stage"]["t3c"] = 3.6
remapDict["breast_tumor_pathologic_t_stage"]["t4"] = 4
remapDict["breast_tumor_pathologic_t_stage"]["t4a"] = 4.2
remapDict["breast_tumor_pathologic_t_stage"]["t4b"] = 4.4
remapDict["breast_tumor_pathologic_t_stage"]["t4c"] = 4.6
remapDict["breast_tumor_pathologic_t_stage"]["t4d"] = 4.8

remapDict["breast_carcinoma_estrogen_receptor_status"] = {}
remapDict["breast_carcinoma_estrogen_receptor_status"]["na"] = "NA"
remapDict["breast_carcinoma_estrogen_receptor_status"]["not_performed"] = "NA"
remapDict["breast_carcinoma_estrogen_receptor_status"][
    "performed_but_not_available"] = "NA"
remapDict["breast_carcinoma_estrogen_receptor_status"][
    "indeterminate"] = "indeterminate"
remapDict["breast_carcinoma_estrogen_receptor_status"]["positive"] = "positive"
remapDict["breast_carcinoma_estrogen_receptor_status"]["negative"] = "negative"

remapDict["lymphnode_pathologic_spread"] = {}
remapDict["lymphnode_pathologic_spread"]["na"] = "NA"
remapDict["lymphnode_pathologic_spread"]["nx"] = "NA"
remapDict["lymphnode_pathologic_spread"]["n0"] = 0
remapDict["lymphnode_pathologic_spread"]["n1"] = 1
remapDict["lymphnode_pathologic_spread"]["n1a"] = 1.2
remapDict["lymphnode_pathologic_spread"]["n1b"] = 1.4
remapDict["lymphnode_pathologic_spread"]["n1c"] = 1.6
remapDict["lymphnode_pathologic_spread"]["n2"] = 2
remapDict["lymphnode_pathologic_spread"]["n2a"] = 2.2
remapDict["lymphnode_pathologic_spread"]["n2b"] = 2.4
remapDict["lymphnode_pathologic_spread"]["n2c"] = 2.6
remapDict["lymphnode_pathologic_spread"]["n3"] = 3
remapDict["lymphnode_pathologic_spread"]["n3a"] = 3.2

remapDict["breast_tumor_pathologic_n_stage"] = {}
remapDict["breast_tumor_pathologic_n_stage"]["na"] = "NA"
remapDict["breast_tumor_pathologic_n_stage"]["pnx"] = "NA"
remapDict["breast_tumor_pathologic_n_stage"]["pn0"] = 0
remapDict["breast_tumor_pathologic_n_stage"]["pn0(i-)"] = 0.2
remapDict["breast_tumor_pathologic_n_stage"]["pn0(i+)"] = 0.4
remapDict["breast_tumor_pathologic_n_stage"]["pn1"] = 1
remapDict["breast_tumor_pathologic_n_stage"]["pn1mi"] = 1.1
remapDict["breast_tumor_pathologic_n_stage"]["pn1a"] = 1.2
remapDict["breast_tumor_pathologic_n_stage"]["pn1b"] = 1.4
remapDict["breast_tumor_pathologic_n_stage"]["pn1c"] = 1.6
remapDict["breast_tumor_pathologic_n_stage"]["pn2"] = 2
remapDict["breast_tumor_pathologic_n_stage"]["pn2a"] = 2.2
remapDict["breast_tumor_pathologic_n_stage"]["pn2b"] = 2.4
remapDict["breast_tumor_pathologic_n_stage"]["pn3"] = 3
remapDict["breast_tumor_pathologic_n_stage"]["pn3a"] = 3.2
remapDict["breast_tumor_pathologic_n_stage"]["pn3b"] = 3.4
remapDict["breast_tumor_pathologic_n_stage"]["pn3c"] = 3.6

remapDict["breast_tumor_pathologic_n_stage"] = {}
remapDict["breast_tumor_pathologic_n_stage"]["na"] = "NA"
remapDict["breast_tumor_pathologic_n_stage"]["nx"] = "NA"
remapDict["breast_tumor_pathologic_n_stage"]["n0"] = 0
remapDict["breast_tumor_pathologic_n_stage"]["n0(i-)"] = 0.2
remapDict["breast_tumor_pathologic_n_stage"]["n0_(i-)"] = 0.2
remapDict["breast_tumor_pathologic_n_stage"]["n0(i+)"] = 0.4
remapDict["breast_tumor_pathologic_n_stage"]["n0_(i+)"] = 0.4
remapDict["breast_tumor_pathologic_n_stage"]["n0_(mol+)"] = 0.3
remapDict["breast_tumor_pathologic_n_stage"]["n1"] = 1
remapDict["breast_tumor_pathologic_n_stage"]["n1mi"] = 1.1
remapDict["breast_tumor_pathologic_n_stage"]["n1a"] = 1.2
remapDict["breast_tumor_pathologic_n_stage"]["n1b"] = 1.4
remapDict["breast_tumor_pathologic_n_stage"]["n1c"] = 1.6
remapDict["breast_tumor_pathologic_n_stage"]["n2"] = 2
remapDict["breast_tumor_pathologic_n_stage"]["n2a"] = 2.2
remapDict["breast_tumor_pathologic_n_stage"]["n2b"] = 2.4
remapDict["breast_tumor_pathologic_n_stage"]["n3"] = 3
remapDict["breast_tumor_pathologic_n_stage"]["n3a"] = 3.2
remapDict["breast_tumor_pathologic_n_stage"]["n3b"] = 3.4
remapDict["breast_tumor_pathologic_n_stage"]["n3c"] = 3.6

remapDict["distant_metastasis_pathologic_spread"] = {}
remapDict["distant_metastasis_pathologic_spread"]["na"] = "NA"
remapDict["distant_metastasis_pathologic_spread"]["mx"] = "NA"
remapDict["distant_metastasis_pathologic_spread"]["m0"] = 0
remapDict["distant_metastasis_pathologic_spread"]["m1"] = 1
remapDict["distant_metastasis_pathologic_spread"]["m1a"] = 1.2
remapDict["distant_metastasis_pathologic_spread"]["m1b"] = 1.4

remapDict["breast_tumor_clinical_m_stage"] = {}
remapDict["breast_tumor_clinical_m_stage"]["na"] = "NA"
remapDict["breast_tumor_clinical_m_stage"]["mx"] = "NA"
remapDict["breast_tumor_clinical_m_stage"]["cm0_(i+)"] = "NA"
remapDict["breast_tumor_clinical_m_stage"]["m0"] = 0
remapDict["breast_tumor_clinical_m_stage"]["m1"] = 1
remapDict["breast_tumor_clinical_m_stage"]["m1a"] = 1.2
remapDict["breast_tumor_clinical_m_stage"]["m1b"] = 1.4

remapDict["residual_tumor"] = {}
remapDict["residual_tumor"]["na"] = "NA"
remapDict["residual_tumor"]["rx"] = "NA"
remapDict["residual_tumor"]["r0"] = 0
remapDict["residual_tumor"]["r1"] = 1
remapDict["residual_tumor"]["r2"] = 2

remapDict["her2_immunohistochemistry_level_result"] = {}
remapDict["her2_immunohistochemistry_level_result"]["na"] = "NA"
remapDict["her2_immunohistochemistry_level_result"]["0"] = 0
remapDict["her2_immunohistochemistry_level_result"]["1+"] = 1
remapDict["her2_immunohistochemistry_level_result"]["2+"] = 2
remapDict["her2_immunohistochemistry_level_result"]["3+"] = 3

remapDict["breast_carcinoma_immunohistochemistry_pos_cell_score"] = {}
remapDict["breast_carcinoma_immunohistochemistry_pos_cell_score"]["na"] = "NA"
remapDict["breast_carcinoma_immunohistochemistry_pos_cell_score"]["0"] = 0
remapDict["breast_carcinoma_immunohistochemistry_pos_cell_score"]["1+"] = 1
remapDict["breast_carcinoma_immunohistochemistry_pos_cell_score"]["2+"] = 2
remapDict["breast_carcinoma_immunohistochemistry_pos_cell_score"]["3+"] = 3
remapDict["breast_carcinoma_immunohistochemistry_pos_cell_score"]["4+"] = 4

remapDict["immunohistochemistry_positive_cell_score"] = {}
remapDict["immunohistochemistry_positive_cell_score"]["na"] = "NA"
remapDict["immunohistochemistry_positive_cell_score"]["0"] = 0
remapDict["immunohistochemistry_positive_cell_score"]["1+"] = 1
remapDict["immunohistochemistry_positive_cell_score"]["2+"] = 2
remapDict["immunohistochemistry_positive_cell_score"]["3+"] = 3
remapDict["immunohistochemistry_positive_cell_score"]["4+"] = 4

remapDict["progesterone_receptor_level_cell_percent_category"] = {}
remapDict["progesterone_receptor_level_cell_percent_category"]["na"] = "NA"
remapDict["progesterone_receptor_level_cell_percent_category"]["<10%"] = 0
remapDict["progesterone_receptor_level_cell_percent_category"]["10-19%"] = 1
remapDict["progesterone_receptor_level_cell_percent_category"]["20-29%"] = 2
remapDict["progesterone_receptor_level_cell_percent_category"]["30-39%"] = 3
remapDict["progesterone_receptor_level_cell_percent_category"]["40-49%"] = 4
remapDict["progesterone_receptor_level_cell_percent_category"]["50-59%"] = 5
remapDict["progesterone_receptor_level_cell_percent_category"]["60-69%"] = 6
remapDict["progesterone_receptor_level_cell_percent_category"]["70-79%"] = 7
remapDict["progesterone_receptor_level_cell_percent_category"]["80-89%"] = 8
remapDict["progesterone_receptor_level_cell_percent_category"]["90-99%"] = 9

remapDict["er_level_cell_percentage_category"] = {}
remapDict["er_level_cell_percentage_category"]["na"] = "NA"
remapDict["er_level_cell_percentage_category"]["<10%"] = 0
remapDict["er_level_cell_percentage_category"]["10-19%"] = 1
remapDict["er_level_cell_percentage_category"]["20-29%"] = 2
remapDict["er_level_cell_percentage_category"]["30-39%"] = 3
remapDict["er_level_cell_percentage_category"]["40-49%"] = 4
remapDict["er_level_cell_percentage_category"]["50-59%"] = 5
remapDict["er_level_cell_percentage_category"]["60-69%"] = 6
remapDict["er_level_cell_percentage_category"]["70-79%"] = 7
remapDict["er_level_cell_percentage_category"]["80-89%"] = 8
remapDict["er_level_cell_percentage_category"]["90-99%"] = 9

remapDict["her2_erbb_pos_finding_cell_percent_category"] = {}
remapDict["her2_erbb_pos_finding_cell_percent_category"]["na"] = "NA"
remapDict["her2_erbb_pos_finding_cell_percent_category"]["<10%"] = 0
remapDict["her2_erbb_pos_finding_cell_percent_category"]["10-19%"] = 1
remapDict["her2_erbb_pos_finding_cell_percent_category"]["20-29%"] = 2
remapDict["her2_erbb_pos_finding_cell_percent_category"]["30-39%"] = 3
remapDict["her2_erbb_pos_finding_cell_percent_category"]["40-49%"] = 4
remapDict["her2_erbb_pos_finding_cell_percent_category"]["50-59%"] = 5
remapDict["her2_erbb_pos_finding_cell_percent_category"]["60-69%"] = 6
remapDict["her2_erbb_pos_finding_cell_percent_category"]["70-79%"] = 7
remapDict["her2_erbb_pos_finding_cell_percent_category"]["80-89%"] = 8
remapDict["her2_erbb_pos_finding_cell_percent_category"]["90-99%"] = 9

remapDict["axillary_lymph_node_stage_method_type"] = {}
remapDict["axillary_lymph_node_stage_method_type"]["na"] = "NA"
remapDict["axillary_lymph_node_stage_method_type"]["OTHER_(SPECIFY)"] = "NA"
remapDict["axillary_lymph_node_stage_method_type"]["other_(specify)"] = "NA"

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def stringInList_CaseInsens ( aString, aList ):

    for s in aList:
        u = s.upper()
        if ( aString.upper() == u ): return ( 1 )

    return ( 0 )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def remapCategoricalFeatures(allClinDict):

    print " "
    print " in remapCategoricalFeatures "

    keyList = allClinDict.keys()
    keyList.sort()
    for aKey in keyList:

        aKey2 = aKey.lower()
        if (aKey2 in remapDict.keys()):

            numRemap = 0

            print " "
            print " looking at <%s> " % aKey2
            tmpV = allClinDict[aKey]
            # print " part of original vector : ", tmpV[:10]

            newV = [0] * len(tmpV)
            for kk in range(len(tmpV)):
                bKey2 = tmpV[kk].lower()
                if (bKey2.startswith("stage_")):
                    bKey2 = bKey2[6:]
                if (bKey2.startswith("stage ")):
                    bKey2 = bKey2[6:]
                try:
                    newV[kk] = remapDict[aKey2][bKey2]
                    if (newV[kk] != "NA" and newV[kk] != "na"):
                        if (newV[kk].lower() != bKey2):
                            # print "     remapping ... ", aKey, aKey2, kk,
                            # bKey2, remapDict[aKey2][bKey2]
                            numRemap += 1
                except:
                    if (0):
                        print " WARNING in remapCategoricalFeatures ... nothing to remap to ??? "
                        print " <%s>  <%s>  %d  <%s> " % (aKey, aKey2, kk, bKey2)
                        print " <%s> " % remapDict[aKey2]
                        # sys.exit(-1)
                    newV[kk] = bKey2

            if (numRemap > 0):
                print " --> using remapped values for <%s> " % aKey
                print " mapping dictionary : ", remapDict[aKey2]
                print " part of original vector : ", tmpV[:10]
                print " part of new vector      : ", newV[:10]
                allClinDict[aKey] = newV

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getNumPatients(allClinDict):

    aKey = allClinDict.keys()[0]
    return ( len(allClinDict[aKey]) )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def findProperKey(allClinDict, aString):

    keyList = allClinDict.keys()
    foundList = []

    for aKey in keyList:
        if ( aKey.lower().find(aString.lower()) >=0 ):
            foundList += [ aKey ]

    if ( len(foundList) == 0 ):
        return ( "NO KEY" )
    elif ( len(foundList) == 1 ):
        return ( foundList[0] )
    else:

        ## look for a perfect match ...
        for mString in foundList:
            mTokens = mString.split(':')
            if ( len(mTokens) == 1 ):
                if ( mTokens[0].lower() == aString.lower() ):
                    return ( mString )
            elif ( len(mTokens) > 2 ):
                try:
                    if ( mTokens[2].lower() == aString.lower() ):
                        return ( mString )
                except:
                    print " findProperKey: ERROR in try ??? ", mString
                    print foundList

        print " "
        print " ERROR in findProperKey ??? multiple matches "
        print " but none of them are perfect matches ... "
        print aString
        print foundList
        print " "
        sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def computeLymphnodesFraction(allClinDict):

    aKey = findProperKey ( allClinDict, "number_of_lymphnodes_positive_by_he" )
    bKey = findProperKey ( allClinDict, "number_of_lymphnodes_examined" )

    if (aKey not in allClinDict.keys()):
        print " "
        print " skipping computeLymphnodesFraction "
        return (allClinDict)
    if (bKey not in allClinDict.keys()):
        print " "
        print " skipping computeLymphnodesFraction "
        return (allClinDict)

    print " "
    print " in computeLymphnodesFraction ... "

    numClin = getNumPatients(allClinDict)
    newV = [0] * numClin
    for kk in range(numClin):
        if (allClinDict[bKey][kk] == "NA"):
            newV[kk] = "NA"
        elif (allClinDict[aKey][kk] == "NA"):
            newV[kk] = "NA"
        elif (int(allClinDict[bKey][kk]) == 0):
            newV[kk] = "NA"
        else:
            newV[kk] = float(allClinDict[aKey][kk]) / \
                float(allClinDict[bKey][kk])
    allClinDict["N:SAMP:fraction_lymphnodes_positive_by_he:::::"] = newV

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def addTag2Key ( aKey, aTag ):

    aTokens = aKey.split(':')

    if ( len(aTokens) >= 7 ):
        newKey = aTokens[0] + ':' + aTokens[1] + ':' + aTokens[2]
        if ( aTag[0] == "_" ):
            newKey += aTag
        else:
            newKey += "_" + aTag
        for ii in range(3,len(aTokens)):
            newKey += ":" + aTokens[ii]

    else:
        newKey = aKey
        if ( aTag[0] == "_" ):
            newKey += aTag
        else:
            newKey += "_" + aTag
        
    return ( newKey )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def checkBarcodes(allClinDict):
    zKey = findProperKey (allClinDict, "bcr_patient_barcode" )
    numClin = getNumPatients(allClinDict)
    for ii in range(numClin):
        if ( allClinDict[zKey][ii].find("_") >= 0 ):
            print " BAD barcode !!! ", ii, allClinDict[zKey][ii]
            sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# fields of interest:
# days_to_birth
# days_to_initial_pathologic_diagnosis	<-- this is always 0
# days_to_submitted_specimen_dx
# days_to_last_followup
# days_to_last_known_alive
# days_to_death
# also:
# new_tumor_event_after_initial_treatment
# days_to_new_tumor_event_after_initial_treatment


def addFollowupInfo(allClinDict):

    print " "
    print " in addFollowupInfo ... "

    # ------------------------------------------------------------------------
    # FIRST: if there is a days_to_last_known_alive, then check that it is
    # used consistently, otherwise create it

    zKey = findProperKey (allClinDict, "bcr_patient_barcode")
    aKey = findProperKey (allClinDict, "days_to_last_known_alive")
    bKey = findProperKey (allClinDict, "days_to_last_followup")
    cKey = findProperKey (allClinDict, "days_to_death")

    haveA = (aKey in allClinDict.keys())
    haveB = (bKey in allClinDict.keys())
    haveC = (cKey in allClinDict.keys())

    print " "
    print " STEP #1 "
    print " have flags A, B, and C : ", haveA, haveB, haveC

    ## print " allClinDict.keys() : "
    ## print allClinDict.keys()

    if (haveA):

        # if we have the "days_to_last_known_alive" field, check that it
        # is consistent with the other two fields ...
        numClin = getNumPatients(allClinDict)
        numNotNA = 0
        for kk in range(numClin):

            ## if we have a 'days_to_death' field and it is not NA, then set 'days_to_last_known_alive' to that value
            if (haveC):
                if (str(allClinDict[cKey][kk]).upper() != "NA"):
                    allClinDict[aKey][kk] = allClinDict[cKey][kk]

            ## if we have a 'days_to_last_followup' field and it is not NA, then ...
            if (haveB):
                if (str(allClinDict[bKey][kk]).upper() != "NA"):
                    if (str(allClinDict[aKey][kk]).upper() == "NA"):
                        allClinDict[aKey][kk] = allClinDict[bKey][kk]

            if (str(allClinDict[aKey][kk]).upper() != "NA"):
                numNotNA += 1

        print " UPDATED days_to_last_known_alive (%d) : " % numNotNA
        print allClinDict[aKey]

    else:

        # create it ...
        if ( aKey == "NO KEY" ): aKey = "N:CLIN:days_to_last_known_alive:::::"
        numClin = getNumPatients(allClinDict)

        newVec = [0] * numClin
        numNotNA = 0

        for kk in range(numClin):
            newVec[kk] = "NA"

            if (haveC):
                if (str(allClinDict[cKey][kk]).upper() != "NA"):
                    newVec[kk] = allClinDict[cKey][kk]

            if (haveB):
                if (str(allClinDict[bKey][kk]).upper() != "NA"):
                    if (str(newVec[kk]).upper() == "NA"):
                        newVec[kk] = allClinDict[bKey][kk]

            if (str(newVec[kk]).upper() != "NA"):
                numNotNA += 1

        print " NEW days_to_last_known_alive (%d) : " % numNotNA
        ## print newVec
        allClinDict[aKey] = newVec

    # ------------------------------------------------------------------------
    # SECOND: if there is a "days_to_submitted_specimen_dx", then create
    # a set of "days_to_" features that instead of being relative
    # to "initial_pathologic_diagnosis" are relative to "submitted_specimen"

    print " "
    print " STEP #2 "
    aKey = findProperKey (allClinDict, "days_to_submitted_specimen_dx")
    tKey = findProperKey (allClinDict, "days_to_initial_pathologic_diagnosis")

    if (aKey in allClinDict.keys()):
        haveA = 1
    else:
        print " do not have [days_to_submitted_specimen_dx] in allClinDict " 
        haveA = 0

    if (tKey in allClinDict.keys()):
        haveT = 1
    else:
        print " do not have [days_to_initial_pathologic_diagnosis] in allClinDict "
        haveT = 0

    try:
        numClin = getNumPatients(allClinDict)
        for bKey in allClinDict.keys():
            if (haveA == 0): continue
            if (bKey == aKey): continue

            if (bKey.find("days_to_") >= 0):
                newKey = addTag2Key ( bKey, "relSS" )
                print " --> making newKey <%s> from bKey <%s> [%d] " % (newKey, bKey, numClin)
                newVec = [0] * numClin
                numNotNA = 0
                for kk in range(numClin):

                    ## initialize to NA
                    newVec[kk] = "NA"

                    ## skip if an important value is NA
                    if (str(allClinDict[aKey][kk]).upper() == "NA"): continue
                    if (str(allClinDict[bKey][kk]).upper() == "NA"): continue
                    if (haveT):
                        if (str(allClinDict[tKey][kk]).upper() == "NA"): continue

                    ## deltaDays is either (days_to_submitted_specimen_dx) - (days_to_initial_pathologic_diagnosis)
                    ##             or just (days_to_submitted_specimen_dx)
                    if (haveT): 
                        deltaDays = allClinDict[aKey][kk] - allClinDict[tKey][kk]
                    else:
                        deltaDays = allClinDict[aKey][kk]

                    ## and then we subtract 'delta days' from the original key to make the new relative key
                    newVec[kk] = allClinDict[bKey][kk] - deltaDays

                    print " STEP2a ", kk, allClinDict[zKey][kk], allClinDict[bKey][kk], allClinDict[aKey][kk], deltaDays, newVec[kk]

                    numNotNA += 1

                if ( numNotNA > 30 ):
                    print " adding new key (%d) : " % numNotNA, newKey
                    ## print newVec[:5]
                    ## print newVec[-5:]
                    allClinDict[newKey] = newVec
                else:
                    print " NOT adding new key (%d) : ", numNotNA, newKey

            if (bKey.find("age_at_") >= 0):
                ## make sure that this is not a "stage_at_" feature !!!
                if ( bKey.find("stage_at_") >= 0 ): continue

                newKey = addTag2Key ( bKey, "relSS" )
                print " --> making newKey <%s> from bKey <%s> [%d] " % (newKey, bKey, numClin)
                newVec = [0] * numClin
                numNotNA = 0
                for kk in range(numClin):

                    ## initialize to NA
                    newVec[kk] = "NA"

                    ## skip if an important value is NA
                    if (str(allClinDict[aKey][kk]).upper() == "NA"): continue
                    if (str(allClinDict[bKey][kk]).upper() == "NA"): continue
                    if (haveT):
                        if (str(allClinDict[tKey][kk]).upper() == "NA"): continue

                    ## deltaDays is either (days_to_submitted_specimen_dx) - (days_to_initial_pathologic_diagnosis)
                    ##             or just (days_to_submitted_specimen_dx)
                    if (haveT): 
                        deltaDays = allClinDict[aKey][kk] - allClinDict[tKey][kk]
                    else:
                        deltaDays = allClinDict[aKey][kk]

                    ## and then we subtract 'delta days' from the original key to make the new relative key
                    ## 04mar14 : actually we need to ADD here because "age" should go UP with deltaDays ...
                    newVec[kk] = allClinDict[bKey][kk] + ( float(deltaDays) / DAYS_PER_YEAR )

                    print " STEP2b ", kk, allClinDict[zKey][kk], allClinDict[bKey][kk], allClinDict[aKey][kk], deltaDays, newVec[kk]

                    numNotNA += 1

                if ( numNotNA > 30 ):
                    print " adding new key (%d) : " % numNotNA, newKey
                    ## print newVec[:5]
                    ## print newVec[-5:]
                    allClinDict[newKey] = newVec
                else:
                    print " NOT adding new key (%d) : ", numNotNA, newKey

    except:
        print " --> failed in this try (x) "
        doNothing = 1

    # ------------------------------------------------------------------------
    # THIRD: if there is a "days_to_sample_procurement", then create
    # a set of "days_to_" features that instead of being relative
    # to "initial_pathologic_diagnosis" are relative to "sample_procurement

    print " "
    print " STEP #3 "
    aKey = findProperKey (allClinDict, "days_to_sample_procurement")
    tKey = findProperKey (allClinDict, "days_to_initial_pathologic_diagnosis")

    if (aKey in allClinDict.keys()):
        haveA = 1
    else:
        print " do not have [days_to_sample_procurement] in allClinDict " 
        haveA = 0

    if (tKey in allClinDict.keys()):
        haveT = 1
    else:
        haveT = 0
        print " do not have a [days_to_initial_pathologic_diagnosis] key "

    try:
        numClin = getNumPatients(allClinDict)
        for bKey in allClinDict.keys():
            if (haveA == 0): continue
            if (bKey == aKey): continue

            if (bKey.find("days_to_") >= 0):
                ## make sure that this is not one of the relSS features just added !!!
                if ( bKey.find("relSS") >= 0 ): continue

                newKey = addTag2Key ( bKey, "relSP" )
                print " --> making newKey <%s> from bKey <%s> [%d] " % (newKey, bKey, numClin)
                newVec = [0] * numClin
                numNotNA = 0
                for kk in range(numClin):

                    ## initialize to NA
                    newVec[kk] = "NA"

                    ## skip if an important value is NA
                    if (str(allClinDict[aKey][kk]).upper() == "NA"): continue
                    if (str(allClinDict[bKey][kk]).upper() == "NA"): continue
                    if (haveT):
                        if (str(allClinDict[tKey][kk]).upper() == "NA"): continue

                    ## deltaDays is either (days_to_sample_procurement) - (days_to_initial_pathologic_diagnosis)
                    ##             or just (days_to_sample_procurement)
                    if (haveT): 
                        deltaDays = allClinDict[aKey][kk] - allClinDict[tKey][kk]
                    else:
                        deltaDays = allClinDict[aKey][kk]

                    ## and then we subtract 'delta days' from the original key to make the new relative key
                    newVec[kk] = allClinDict[bKey][kk] - deltaDays

                    print " STEP3a ", kk, allClinDict[zKey][kk], allClinDict[bKey][kk], allClinDict[aKey][kk], deltaDays, newVec[kk]

                    numNotNA += 1

                if ( numNotNA > 30 ):
                    print " adding new key (%d) : " % numNotNA, newKey
                    ## print newVec[:5]
                    ## print newVec[-5:]
                    allClinDict[newKey] = newVec
                else:
                    print " NOT adding new key (%d) : ", numNotNA, newKey

            if (bKey.find("age_at_") >= 0):
                ## make sure that this is not one of the relSS features just added !!!
                if ( bKey.find("relSS") >= 0 ): continue
                ## make sure that this is not a "stage_at_" feature !!!
                if ( bKey.find("stage_at_") >= 0 ): continue

                newKey = addTag2Key ( bKey, "relSP" )
                print " --> making newKey <%s> from bKey <%s> [%d] " % (newKey, bKey, numClin)
                newVec = [0] * numClin
                numNotNA = 0
                for kk in range(numClin):

                    ## initialize to NA
                    newVec[kk] = "NA"

                    ## skip if an important value is NA
                    print " checking for important information ... ", aKey, bKey, tKey
                    print allClinDict[aKey][kk]
                    print allClinDict[bKey][kk]
                    if (str(allClinDict[aKey][kk]).upper() == "NA"): continue
                    if (str(allClinDict[bKey][kk]).upper() == "NA"): continue
                    if (haveT): 
                        print allClinDict[tKey][kk]
                        if (str(allClinDict[tKey][kk]).upper() == "NA"): continue

                    ## deltaDays is either (days_to_sample_procurement) - (days_to_initial_pathologic_diagnosis)
                    ##             or just (days_to_sample_procurement)
                    if (haveT): 
                        deltaDays = allClinDict[aKey][kk] - allClinDict[tKey][kk]
                    else:
                        deltaDays = allClinDict[aKey][kk]
                    print " computed deltaDays : ", deltaDays

                    ## and then we subtract 'delta days', scaled to years ...
                    ## 03mar14 : actually we need to ADD here ...
                    newVec[kk] = allClinDict[bKey][kk] + ( float(deltaDays) / DAYS_PER_YEAR )

                    print " STEP3b ", kk, allClinDict[zKey][kk], allClinDict[bKey][kk], allClinDict[aKey][kk], deltaDays, newVec[kk]

                    numNotNA += 1

                if ( numNotNA > 30 ):
                    print " adding new key (%d) : " % numNotNA, newKey
                    ## print newVec[:5]
                    ## print newVec[-5:]
                    allClinDict[newKey] = newVec
                else:
                    print " NOT adding new key (%d) : ", numNotNA, newKey

    except:
        print " --> failed in this try (y) "
        doNothing = 1


    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# fields of interest:
# days_to_birth
# days_to_initial_pathologic_diagnosis	<-- this is always 0
# days_to_submitted_specimen_dx
# days_to_last_followup
# days_to_last_known_alive
# days_to_death
# also:
# new_tumor_event_after_initial_treatment
# days_to_new_tumor_event_after_initial_treatment


def checkFollowupInfo(allClinDict):

    print " "
    print " in checkFollowupInfo ... "

    # FIRST: if there is a days_to_last_known_alive, then check that it is
    # used consistently, otherwise create it

    zKey = findProperKey (allClinDict, "bcr_patient_barcode")
    aKey = findProperKey (allClinDict, "days_to_last_known_alive")
    bKey = findProperKey (allClinDict, "days_to_last_followup")
    cKey = findProperKey (allClinDict, "days_to_death")
    dKey = findProperKey (allClinDict, "vital_status")

    haveA = (aKey in allClinDict.keys())
    haveB = (bKey in allClinDict.keys())
    haveC = (cKey in allClinDict.keys())
    haveD = (dKey in allClinDict.keys())

    print " have flags A, B, C and D : ", haveA, haveB, haveC, haveD

    if ( not haveD ):
        print " skipping this function ... requires vital_status "
        return (allClinDict)

    ## print " allClinDict.keys() : "
    ## print allClinDict.keys()

    numClin = getNumPatients(allClinDict)

    # range of days_to_last_known_alive is typically something like [0,3196]
    for kk in range(numClin):
        if (str(allClinDict[dKey][kk]).upper() == "DEAD"):
            if (str(allClinDict[cKey][kk]).upper() == "NA"):
                print " ERROR !!! need to know when this person died !!! ", allClinDict[zKey][kk]
                print kk
                print aKey, allClinDict[aKey][kk]
                print bKey, allClinDict[bKey][kk]
                print cKey, allClinDict[cKey][kk]
                print dKey, allClinDict[dKey][kk]
                print " UPDATING vital_status to Alive ... "
                print " "
                ## because we do not have a days_to_death value, we are going to call this person "Alive"
                allClinDict[dKey][kk] = "Alive"

        if (str(allClinDict[dKey][kk]).upper() == "ALIVE"):
            if (str(allClinDict[aKey][kk]).upper() == "NA"):
                if (str(allClinDict[bKey][kk]).upper() == "NA"):
                    print " ERROR !!! no information about follow-up ??? ", allClinDict[zKey][kk]
                    print kk
                    print aKey, allClinDict[aKey][kk]
                    print bKey, allClinDict[bKey][kk]
                    print cKey, allClinDict[cKey][kk]
                    print dKey, allClinDict[dKey][kk]
                    print " UPDATING days_to_last_known_alive and days_to_last_followup to 0 "
                    print " "
                    allClinDict[aKey][kk] = 0
                    allClinDict[bKey][kk] = 0
                else:
                    print " ERROR in checkFollowupInfo ... how did we get here ??? "
                    sys.exit(-1)
        

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# derive the preferred stage tumor stage from the comparison of the
# reported one with the derived one

def PreferredStage(reported, computed):
    t = testTumorStage(reported, computed)
    if (t == "AGREE"):
        return(reported)
    if (t == "Stage cannot be derived from TNM"):
        return(reported)
    if (t == "Derived stage is more specific"):
        return(repStage(computed))  # For SupTab1 use return(computed)
    if (t == "Stage can be derived from TNM"):
        return(repStage(computed))  # For SupTab1 use return(computed)
    if (t == "Stage more specific than TNM"):
        return(reported)
    if (t == "DISAGREE"):
        return(reported)  # assuming the reported one to be valid!
    return("Error: Lack a preferred stage")

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# Return first element of a vector, or if input is string, the string itself


def repStage(substage):
    if (type(substage) is str):
        return(substage)
    if (type(substage) is list):
        return(substage[0])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# Characterize the difference between reported and inferred tumor stage


def testTumorStage(reported, computed):
    # Agreement includes "in" relationship and NA equivalence
    if (type(computed) is list):
        if (reported in computed):
            return("AGREE")
    if (type(computed) is str):
        if (reported == computed):
            return("AGREE")
    if (((reported == "STAGE IVA") | (reported == "STAGE IVB")) & (computed == "STAGE IV")):
        return("Stage more specific than TNM")
    if ((reported == "NA") & (computed != "NA")):
        return("Stage can be derived from TNM")
    if ((reported != "NA") & (computed == "NA")):
        return("Stage cannot be derived from TNM")
    if (repStage(computed).startswith(reported)):
        return("Derived stage is more specific")
    return("DISAGREE")

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# Derive Tumor Stage from TNM and AJCC table, 7th edition
# sometimes if we get something like "M1" when it should actually be "M1A"
# or "M1B", we will pick the first/lowest thing that it could be ...


def getTumorStage(T, N, M):

    print " WARNING ... this function should NOT be called ... "
    sys.exit(-1)

    T = T.upper()
    N = N.upper()
    M = M.upper()

    if (M == "M1"):
        # Seems to be TCGA choice if IVA, IVB not specified
        return ("STAGE IV")
    if (M == "M1A"):
        return ("STAGE IVA")
    if (M == "M1B"):
        return ("STAGE IVB")

    if (T == "TX"):
        T = "NA"
    if (N == "NX"):
        N = "NA"
    if (M == "MX"):
        M = "NA"

    if (T == "NA" or N == "NA" or M == "NA"):
        return ("NA")

    if (T == "T0" and N == "N0" and M == "M0"):
        return ("STAGE 0")
    if (T == "Tis" and N == "N0" and M == "M0"):
        return ("STAGE 0")

    if (T == "T1" and N == "N0" and M == "M0"):
        return ("STAGE I")
    if (T == "T1A" and N == "N0" and M == "M0"):
        return ("STAGE I")
    if (T == "T1B" and N == "N0" and M == "M0"):
        return ("STAGE I")
    if (T == "T2" and N == "N0" and M == "M0"):
        return ("STAGE I")
    if (T == "T2A" and N == "N0" and M == "M0"):
        return ("STAGE I")
    if (T == "T2B" and N == "N0" and M == "M0"):
        return ("STAGE I")

    if (T == "T3" and N == "N0" and M == "M0"):
        return ("STAGE IIA")
    if (T == "T3A" and N == "N0" and M == "M0"):
        return ("STAGE IIA")
    if (T == "T3B" and N == "N0" and M == "M0"):
        return ("STAGE IIB")
    if (T == "T3C" and N == "N0" and M == "M0"):
        return ("STAGE IIB")
    if (T == "T4A" and N == "N0" and M == "M0"):
        return ("STAGE IIB")
    if (T == "T4B" and N == "N0" and M == "M0"):
        return ("STAGE IIC")
    if (T == "T4" and N == "N0" and M == "M0"):
        return (["STAGE IIB", "STAGE IIC"])

    if (T == "T1" and N == "N1" and M == "M0"):
        return ("STAGE IIIA")
    if (T == "T1A" and N == "N1" and M == "M0"):
        return ("STAGE IIIA")
    if (T == "T1B" and N == "N1" and M == "M0"):
        return ("STAGE IIIA")
    if (T == "T1" and N == "N1A" and M == "M0"):
        return ("STAGE IIIA")
    if (T == "T1" and N == "N1B" and M == "M0"):
        return ("STAGE IIIA")
    if (T == "T1" and N == "N1C" and M == "M0"):
        return ("STAGE IIIA")

    if (T == "T1" and N == "N2" and M == "M0"):
        return (["STAGE IIIA", "STAGE IIIB"])  # CHOICE IIIA, IIIB
    if (T == "T1B" and N == "N2" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T1" and N == "N2A" and M == "M0"):
        return ("STAGE IIIA")
    if (T == "T1" and N == "N3" and M == "M0"):
        return ("STAGE IIIA")
    if (T == "T2" and N == "N1" and M == "M0"):
        return ("STAGE IIIA")
    if (T == "T2A" and N == "N1" and M == "M0"):
        return ("STAGE IIIA")
    if (T == "T2B" and N == "N1" and M == "M0"):
        return ("STAGE IIIA")
    if (T == "T2" and N == "N1A" and M == "M0"):
        return ("STAGE IIIA")
    if (T == "T2" and N == "N1B" and M == "M0"):
        return ("STAGE IIIA")
    if (T == "T2" and N == "N1C" and M == "M0"):
        return ("STAGE IIIA")

    if (T == "T3" and N == "N1" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T3A" and N == "N1" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T3B" and N == "N1" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T3" and N == "N1A" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T3" and N == "N1B" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T3" and N == "N1C" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T4A" and N == "N1" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T4A" and N == "N1A" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T4A" and N == "N1B" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T4A" and N == "N1C" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T4" and N == "N1" and M == "M0"):
        return (["STAGE IIIB", "STAGE IIIC"])
    if (T == "T2" and N == "N2" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T2A" and N == "N2" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T2B" and N == "N2" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T2" and N == "N2A" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T2" and N == "N2B" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T2" and N == "N2C" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T2" and N == "N3" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T2B" and N == "N3" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T3" and N == "N2" and M == "M0"):
        return (["STAGE IIIB", "STAGE IIIC"])  # CHOICE IIIB, IIIC
    if (T == "T3" and N == "N2A" and M == "M0"):
        return ("STAGE IIIB")
    if (T == "T3" and N == "N2C" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T1" and N == "N2B" and M == "M0"):
        return ("STAGE IIIB")

    if (T == "T3" and N == "N2B" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T3" and N == "N3" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4" and N == "N2" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4A" and N == "N2" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4A" and N == "N2A" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4A" and N == "N2B" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4A" and N == "N2C" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4" and N == "N3" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4" and N == "N3A" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4A" and N == "N3" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4B" and N == "N1" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4B" and N == "N2" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4B" and N == "N1A" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4B" and N == "N1B" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4B" and N == "N1C" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4B" and N == "N2C" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4B" and N == "N2A" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4B" and N == "N2B" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4B" and N == "N2B" and M == "M0"):
        return ("STAGE IIIC")
    if (T == "T4B" and N == "N3A" and M == "M0"):
        return ("STAGE IIIC")

    # We reach this point if all values are non-NA, but combination is not in
    # AJCC tumor table
    print " ERROR in getTumorStage ??? ", T, N, M
    return ("Not in AJCC Table?")

    sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def checkTumorStage(allClinDict):

    if ("tumor_stage" not in allClinDict.keys()):
        print " skipping checkTumorStage ... "
        return (allClinDict)
    else:
        print " running checkTumorStage ... "

    numClin = getNumPatients(allClinDict)
    print " total number of patients : ", numClin

    if (0):
        stringList = ["tumor", "stage", "spread"]
        for aKey in allClinDict.keys():
            for aString in stringList:
                if (aKey.find(aString) >= 0):
                    print aKey

    reqKeyList = [
        "bcr_patient_barcode", "tumor_stage", "primary_tumor_pathologic_spread",
        "lymphnode_pathologic_spread", "distant_metastasis_pathologic_spread"]
    numNotFound = 0
    for aKey in reqKeyList:
        if (aKey not in allClinDict.keys()):
            numNotFound += 1
    if (numNotFound > 0):
        print " skipping checkTumorStage ... "
        return (allClinDict)

    pKey = getProperKey ( allClinDict, "bcr_patient_barcode" )
    sKey = getProperKey ( allClinDict, "tumor_stage" )
    tKey = getProperKey ( allClinDict, "primary_tumor_pathologic_spread" )
    nKey = getProperKey ( allClinDict, "lymphnode_pathologic_spread" )
    mKey = getProperKey ( allClinDict, "distant_metastasis_pathologic_spread" )

    for ii in range(numClin):

        aCode = allClinDict[pKey][ii]
        curTumorStage = allClinDict[sKey][ii]
        curT = allClinDict[tKey][ii]
        curN = allClinDict[nKey][ii]
        curM = allClinDict[mKey][ii]

        # print " checking tumor stage for <%s> <%s> <%s> <%s> <%s> " % (
        # aCode, curTumorStage, curN, curM, curT )

        ## removing this 15aug2014 ...
        if ( 0 ):
            curTumorStage = curTumorStage.upper()
            curTumorStage = curTumorStage.strip()
            if (curTumorStage != "NA"):
                if (not curTumorStage.startswith("STAGE ")):
                    curTumorStage = "STAGE " + curTumorStage

        # as of 09nov12, NOT attempting to derive tumor stage from T, N, and M
        if (0):

            # get AJCC-derived tumor stage, compare to DCC value, and decide
            # which to use
            ajccStage = getTumorStage(curT, curN, curM)
            newStage = PreferredStage(curTumorStage, ajccStage)
            allClinDict[sKey][ii] = newStage

            # report
            if (type(ajccStage) is list):
                ajccString = ' OR '.join(ajccStage)
            else:
                ajccString = ajccStage

            print aCode.upper() + ', TNM:' + curT.upper() + ' ' + curN.upper() + ' ' + curM.upper() + ', DCC Stage:' \
                                + curTumorStage + ', AJCC Stage:' + ajccString + ', Comparison:' \
                                + \
                testTumorStage(curTumorStage, ajccStage) + \
                ', Will use: ' + newStage

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def checkVitalStatus(allClinDict):

    vsKey = findProperKey ( allClinDict, "vital_status" )
    bcKey = findProperKey ( allClinDict, "bcr_patient_barcode" )

    if ( vsKey == "NO KEY" ):
        print " skipping checkVitalStatus ... "
        return (allClinDict)

    print " running checkVitalStatus ... "

    numClin = getNumPatients(allClinDict)
    print " total number of patients : ", numClin

    numLC = 0
    numDC = 0
    for ii in range(numClin):

        aCode = allClinDict[bcKey][ii]
        curStatus = allClinDict[vsKey][ii]

        doChange = 1
        try:
            newStatus = curStatus

        except:
            try:
                if (curStatus == 0):
                    newStatus = "Alive"
                    numLC += 1
                elif (curStatus == 1):
                    newStatus = "Dead"
                    numDC += 1
            except:
                doChange = 0

        if (doChange):
            allClinDict[vsKey][ii] = newStatus

    if (numLC + numDC > 0):
        print " WARNING: changed some vital status fields ... %d %d " % (numLC, numDC)

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def updateAge(allClinDict):

    pKey = findProperKey ( allClinDict, "bcr_patient_barcode" )
    aKey = findProperKey ( allClinDict, "age_at_initial_pathologic_diagnosis" )
    bKey = findProperKey ( allClinDict, "days_to_birth" )

    print " running updateAge ... "

    numClin = getNumPatients(allClinDict)
    print " total number of patients : ", numClin

    for ii in range(numClin):
        try:
            aCode = allClinDict[pKey][ii]
            curAge = allClinDict[aKey][ii]
            curD2B = allClinDict[bKey][ii]
            newAge = float(0 - int(curD2B)) / DAYS_PER_YEAR
            # now we want to limit the 'precision' to two decimal places
            newAge = float(int((100. * newAge) + 0.49)) / 100.
            if (abs(curAge - int(newAge)) > 0):
                print " ERROR in updateAge ??? ", curAge, curD2B, newAge, aCode
            allClinDict[aKey][ii] = newAge
        except:
            doNothing = 1

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def removeParens(oneKey):

    print " in removeParens ... "

    origUniqList = []
    newUniqList = []

    newKey = []
    for aLabel in oneKey:

        if (aLabel not in origUniqList):
            origUniqList += [aLabel]

        if (aLabel.find("(") >= 0):

            print " --> found open paren ... at %d in <%s> " % (aLabel.find("("), aLabel)

            bLabel = ""
            copyOn = 1
            for ii in range(len(aLabel)):
                if (aLabel[ii] == "("):
                    copyOn = 0
                if (copyOn):
                    bLabel += aLabel[ii]
                if (aLabel[ii] == ")"):
                    copyOn = 1

            if (bLabel.startswith("_")):
                bLabel = bLabel[1:]
            if (bLabel.endswith("_")):
                bLabel = bLabel[:-1]

            newKey += [bLabel]
            if (bLabel not in newUniqList):
                newUniqList += [bLabel]

        else:

            newKey += [aLabel]
            if (aLabel not in newUniqList):
                newUniqList += [aLabel]

    print origUniqList
    print newUniqList

    if (len(newUniqList) == len(origUniqList)):
        print " --> removing parenthetical strings "
        print origUniqList
        print newUniqList
        return (newKey)
    else:
        print " NOT removing parenthetical strings "
        return (oneKey)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def removeSpecialChars(oneKey):

    okExceptions = ['4+']

    # ran into a strange case here where most of the elements were strings
    # like 'grade_1' but some were just integers like 3 :(
    # so ... these next few blocks of code are TOTAL HACKS ...
    numInt = 0
    numNot = 0
    aString = ''
    aInt = 9999
    for ii in range(len(oneKey)):
        aLabel = str(oneKey[ii])
        if (aLabel.upper() == "NA"):
            continue
        if (aLabel.upper() == "UNKNOWN"):
            oneKey[ii] = "NA"
            continue
        try:
            iVal = int(aLabel)
            numInt += 1
            aInt = iVal
        except:
            numNot += 1
            aString = aLabel

    print "         number of integers = %d    number NOT = %d " % (numInt, numNot)

    if (numInt > 0 and numNot > 0):

        # for now, we are just checking for 'grade' strings that are sometimes
        # 'grade_3' and sometimes just '3'
        if (aString.lower().startswith("grade_")):
            for ii in range(len(oneKey)):
                aLabel = str(oneKey[ii])
                if (aLabel.upper() == "NA"):
                    continue
                if (not aLabel.lower().startswith("grade_")):
                    try:
                        iVal = int(aLabel)
                        aString = "Grade_%d" % iVal
                        oneKey[ii] = aString
                    except:
                        print "     FAILED to prepend grade ??? ", aLabel
                        sys.exit(-1)

        # or if there are at least twice as many strings as integers, then we
        # will cast the integers to strings ...
        elif (numInt < (numNot / 2)):
            for ii in range(len(oneKey)):
                aLabel = str(oneKey[ii])
                if (aLabel.upper() == "NA"):
                    continue
                try:
                    iVal = int(aLabel)
                    oneKey[ii] = str(iVal)
                except:
                    doNothing = 1

        elif (aString not in okExceptions):
            if ( 1 ):
                print " WARNING ... something odd about this feature ... ", aInt, aString
                print oneKey
                ## return ([])
                ## sys.exit(-1)

    origUniqList = []
    newUniqList = []

    newKey = []
    for aLabel in oneKey:

        if (aLabel not in origUniqList):
            origUniqList += [aLabel]

        bLabel = ""
        try:
            for ii in range(len(aLabel)):
                if (aLabel[ii] == ' '):
                    bLabel += "_"
                elif (aLabel[ii] == "'"):
                    bLabel += "_"
                elif (aLabel[ii] == '"'):
                    bLabel += "_"
                elif (aLabel[ii] == ':'):
                    bLabel += "_"
                elif (aLabel[ii] == '/'):
                    bLabel += "_"
                # elif ( aLabel[ii] == '-' ):
                ##     bLabel += "_"
                elif (aLabel[ii] == '.'):
                    bLabel += "_"
                elif (aLabel[ii] == ','):
                    bLabel += "_"
                else:
                    bLabel += aLabel[ii]
        except:
            print " ERROR in removeSpecialChars ??? "
            print " oneKey = <%s> " % (oneKey)
            print " aLabel = <%s> " % (aLabel)
            sys.exit(-1)

        ii = bLabel.find("__")
        while (ii >= 0):
            bLabel = bLabel[:ii] + bLabel[ii + 1:]
            ii = bLabel.find("__")

        newKey += [bLabel]
        if (bLabel not in newUniqList):
            newUniqList += [bLabel]

    print origUniqList
    print newUniqList

    if (len(newUniqList) == len(origUniqList)):
        return (newKey)
    else:
        print " NOT removing parenthetical strings "
        return (oneKey)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getCommonPrefix(aLabel, bLabel):

    nn = 0
    while (aLabel[nn].lower() == bLabel[nn].lower()):
        nn += 1
        if (nn >= len(aLabel)):
            return (aLabel[:nn])
        if (nn >= len(bLabel)):
            return (aLabel[:nn])

    return (aLabel[:nn])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getCommonSuffix(aLabel, bLabel):

    nn = -1
    while (aLabel[nn].lower() == bLabel[nn].lower()):
        nn -= 1
        if (-nn > len(aLabel)):
            return (aLabel)
        if (-nn > len(bLabel)):
            return (bLabel)

    if (nn == -1):
        return ("")
    else:
        return (aLabel[nn + 1:])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def removeCommonPrefix(oneKey, labelList):

    print " in removeCommonPrefix : ", labelList
    madeChange = 0

    nLabel = len(labelList)
    for ii in range(nLabel):
        for jj in range(ii + 1, nLabel):
            commonPrefix = getCommonPrefix(labelList[ii], labelList[jj])

            # if the commonPrefix is *ever* the entire string, then
            # we cannot really use this ...
            if (commonPrefix == labelList[ii]):
                continue
            if (commonPrefix == labelList[jj]):
                continue

            if (len(commonPrefix) > 4):
                print ii, jj, commonPrefix

                newKey = []
                for cLabel in oneKey:
                    if (cLabel.lower().startswith(commonPrefix)):
                        dLabel = cLabel[len(commonPrefix):]
                        if (len(dLabel) < 4):
                            dLabel = cLabel
                        else:
                            madeChange += 1
                    else:
                        dLabel = cLabel
                    if (dLabel[0] == '_'):
                        dLabel = dLabel[1:]
                    newKey += [dLabel]

                newList = []
                for cLabel in labelList:
                    if (cLabel.lower().startswith(commonPrefix)):
                        dLabel = cLabel[len(commonPrefix):]
                        if (len(dLabel) < 4):
                            dLabel = cLabel
                        else:
                            madeChange += 1
                    else:
                        dLabel = cLabel
                    if (dLabel[0] == '_'):
                        dLabel = dLabel[1:]
                    newList += [dLabel]

                if (len(labelList) == len(newList)):
                    labelList = newList
                    oneKey = newKey

    if (madeChange > 0):
        print " after removeCommonPrefix : ", madeChange, labelList

    return (oneKey, labelList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def removeCommonSuffix(oneKey, labelList):

    print " in removeCommonSuffix : ", labelList
    madeChange = 0

    nLabel = len(labelList)
    for ii in range(nLabel):
        for jj in range(ii + 1, nLabel):
            commonSuffix = getCommonSuffix(labelList[ii], labelList[jj])

            # if the commonSuffix is *ever* the entire string, then
            # we cannot really use this ...
            if (commonSuffix == labelList[ii]):
                continue
            if (commonSuffix == labelList[jj]):
                continue

            if (len(commonSuffix) > 4):
                print ii, jj, commonSuffix

                newKey = []
                for cLabel in oneKey:
                    if (cLabel.lower().endswith(commonSuffix)):
                        dLabel = cLabel[:-len(commonSuffix)]
                        if (len(dLabel) < 4):
                            dLabel = cLabel
                        else:
                            madeChange += 1
                    else:
                        dLabel = cLabel
                    if (dLabel[-1] == '_'):
                        dLabel = dLabel[:-1]
                    newKey += [dLabel]

                newList = []
                for cLabel in labelList:
                    if (cLabel.lower().endswith(commonSuffix)):
                        dLabel = cLabel[:-len(commonSuffix)]
                        if (len(dLabel) < 4):
                            dLabel = cLabel
                        else:
                            madeChange += 1
                    else:
                        dLabel = cLabel
                    if (dLabel[-1] == '_'):
                        dLabel = dLabel[:-1]
                    newList += [dLabel]

                if (len(labelList) == len(newList)):
                    labelList = newList
                    oneKey = newKey

                if (0):
                    print " removeCommonSuffix has not yet been fully tested ... "
                    print labelList
                    print oneKey
                    sys.exit(-1)

    if (madeChange > 0):
        print " after removeCommonSuffix : ", madeChange, labelList

    return (oneKey, labelList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def abbrevCategStrings(allClinDict):

    print " "
    print " in abbrevCategStrings ... "
    print " "

    keyList = allClinDict.keys()
    keyList.sort()

    for aKey in keyList:

        if (aKey.find("bcr_patient_barcode") >= 0): 
            print " all barcodes : "
            print allClinDict[aKey]
            print " done "
            continue

        (keyType, nCount, nNA, nCard, labelList, labelCount) = miscClin.lookAtKey(allClinDict[aKey])
        print aKey, keyType, nCount, nNA

        if (keyType == "NOMINAL"):

            # remove weird characters from the strings ...
            print " calling removeSpecialChars ... <%s> " % (aKey)
            allClinDict[aKey] = removeSpecialChars(allClinDict[aKey])

            # if we get nothing back, then skip ...
            if (allClinDict[aKey] == []): 
                print " WARNING ... got nothing back ??? ", aKey
                continue

            # otherwise, look at cardinality, type, etc ...
            (keyType, nCount, nNA, nCard, labelList, labelCount) = miscClin.lookAtKey(allClinDict[aKey])

            maxLen = 0
            skipFlag = 0
            for aLabel in labelList:
                try:
                    maxLen = max(maxLen, len(aLabel))
                except:
                    print " what is up with this key ??? ", aKey, labelList
                    skipFlag = 1

            if (skipFlag):
                continue

            if (maxLen > 10):

                ## print aKey, labelList, maxLen

                # first try at making the labels a bit shorter by removing
                # parenthetical elements ...
                allClinDict[aKey] = removeParens(allClinDict[aKey])
                (keyType, nCount, nNA, nCard, labelList,
                 labelCount) = miscClin.lookAtKey(allClinDict[aKey])

                maxLen = 0
                for aLabel in labelList:
                    maxLen = max(maxLen, len(aLabel))
                ## print aKey, labelList, maxLen

                # removing this step for now (04dec12)
                if (0):

                    # next try to remove common prefixes or suffixes ...
                    if (maxLen > 10):
                        (allClinDict[aKey], labelList) = removeCommonPrefix(
                            allClinDict[aKey], labelList)
                        (allClinDict[aKey], labelList) = removeCommonSuffix(
                            allClinDict[aKey], labelList)

                        maxLen = 0
                        for aLabel in labelList:
                            maxLen = max(maxLen, len(aLabel))
                        ## print aKey, labelList, maxLen
                        if (maxLen > 25):
                            print "     --> strings are still rather long, but not sure what to do about this ... "

                    print labelList, maxLen
                    print " "
                    print " "

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def checkPrefix(labelList, aPrefix):

    nLabel = len(labelList)
    nHas = 0
    for aLabel in labelList:
        bLabel = aLabel.upper()
        if (bLabel == "NA"):
            nLabel -= 1
            continue
        if (bLabel.startswith(aPrefix)):
            nHas += 1

    if ((nHas + 2) >= nLabel): return (1)

    return (0)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def translateArabic(aLabel, usePrefix):

    # print " in translateArabic ... "

    pLen = len(usePrefix)
    bLabel = aLabel.upper()
    if (bLabel.startswith(usePrefix)):
        bLabel = bLabel[pLen:]
        if (bLabel[0] == "_"):
            bLabel = bLabel[1:]
        bLen = len(bLabel)
        found = 0
        for iLen in range(bLen, 0, -1):
            # print found, iLen, bLabel[:iLen]
            if (not found):
                try:
                    curN = int(bLabel[:iLen])
                    found = 1
                except:
                    doNothing = 1

        if (not found):
            # X means that it could not be assessed, so returning NA
            if (bLabel == "X"):
                return ("NA")
            # B means 'borderline' but returning NA ...
            elif (bLabel == "B"):
                return ("NA")
            else:
                print " ERROR ??? <%s> <%s>  --> returning NA " % (bLabel, usePrefix)
                return ("NA")

        rLen = len(str(curN))
        if (len(bLabel) > rLen):
            bLabel = bLabel[rLen:]
            if (bLabel == "A"):
                curN += 0.2
            elif (bLabel == "B"):
                curN += 0.4
            elif (bLabel == "C"):
                curN += 0.6
            else:
                print "     left over in translateArabic <%s> <%s> <%s> " % (bLabel, aLabel, usePrefix)

        return (curN)

    else:
        return ("NA")

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def translateRoman(aLabel, usePrefix):

    romanList = ["VIII", "III", "VII", "IV", "IX", "II", "VI", "I", "V", "X"]
    numbrList = [8, 3, 7, 4, 9, 2, 6, 1, 5, 10]

    pLen = len(usePrefix)
    bLabel = aLabel.upper()
    if (bLabel.startswith(usePrefix)):
        bLabel = bLabel[pLen:]
        if (bLabel[0] == "_"):
            bLabel = bLabel[1:]
        found = 0
        for kk in range(len(romanList)):
            if (not found):
                if (bLabel.startswith(romanList[kk])):
                    found = 1
                    curKK = kk
                    curN = numbrList[kk]
                    curR = romanList[kk]

        if (not found):
            if (bLabel == "X"):
                return ("NA")
            elif (bLabel == "TIS"):
                return ("NA")
            else:
                print " ERROR ??? ", bLabel, usePrefix
                sys.exit(-1)

        rLen = len(curR)
        if (len(bLabel) > rLen):
            bLabel = bLabel[rLen:]
            if (bLabel == "A"):
                curN += 0.2
            elif (bLabel == "B"):
                curN += 0.4
            elif (bLabel == "C"):
                curN += 0.6
            else:
                print "     left over in translateRoman <%s> <%s> <%s> " % (bLabel, aLabel, usePrefix)

        return (curN)

    else:
        return ("NA")

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def checkRomanNumerals(labelList, usePrefix):

    skipList = ["_"]
    stripList = ["A", "B", "C", "X", "0"]
    romanList = ["I", "V", "X"]

    pLen = len(usePrefix)
    yesR = 0
    notR = 0
    for aLabel in labelList:
        bLabel = aLabel.upper()
        if (bLabel.startswith(usePrefix)):
            bLabel = bLabel[pLen:]
            if (bLabel[-1] in stripList):
                bLabel = bLabel[:-1]
            for ii in range(len(bLabel)):
                if (bLabel[ii] in romanList):
                    yesR += 1
                else:
                    if (bLabel[ii] not in skipList):
                        notR += 1

    # print "         in checkRomanNumerals : ", yesR, notR

    if (notR == 0):
        return (1)
    if (notR > yesR):
        return (0)

    if (yesR > 0):
        print " ??? strange counts in checkRomanNumerals ??? "
        return (1)

    return (0)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this function tries to create a numerical feature for a categorical
# feature ...


def addNumericalFeatures(allClinDict):

    print " "
    print " "
    print " in addNumericalFeatures ... "

    keyList = allClinDict.keys()
    keyList.sort()

    # CAREFUL: add on things only at the end of this list ...
    prefixList = ["T", "N", "M", "STAGE", "GRADE", "G", "PT"]
    nPrefix = len(prefixList)
    prefixBits = [0] * nPrefix

    for aKey in keyList:
        if (aKey == "bcr_patient_barcode"):
            continue
        (keyType, nCount, nNA, nCard, labelList,
         labelCount) = miscClin.lookAtKey(allClinDict[aKey])

        if (keyType == "NOMINAL"):
            if (nCard > 2 and nCard < 15):

                tmpKey = aKey.lower()
                if (tmpKey.find("stage") >= 0 or tmpKey.find("grade") >= 0 or
                        tmpKey.find("pathologic_spread") >= 0):
                    print " considering this categorical feature ... ", aKey, keyType, nCard, labelList, labelCount

                    for iP in range(nPrefix):
                        aPrefix = prefixList[iP]
                        prefixBits[iP] = checkPrefix(labelList, aPrefix)

                    # if the 'GRADE' bit gets set, then unset the 'G' bit
                    if (prefixBits[4]):
                        prefixBits[5] = 0

                    # print prefixBits
                    usePrefix = ""
                    if (sum(prefixBits) == 1):
                        for iP in range(nPrefix):
                            if (prefixBits[iP]):
                                usePrefix = prefixList[iP]
                    elif (sum(prefixBits) > 1):
                        print " ERROR ??? how can it have multiple prefix bits ON ??? "
                        sys.exit(-1)

                    # print " usePrefix <%s> " % usePrefix

                    isRoman = checkRomanNumerals(labelList, usePrefix)
                    # print " isRoman = %d " % isRoman

                    if (aKey[1] == ":"):
                        tokenList = aKey.split(':')
                        newLabel = "N:" + \
                            tokenList[1] + ":" + tokenList[2] + "_derived"
                        for ii in range(3, len(tokenList)):
                            newLabel += ":" + tokenList[ii]
                    else:
                        newLabel = "N:CLIN:" + aKey + "_derived"
                    if (newLabel in allClinDict.keys()):
                        print " this feature label already exists ??? ", newLabel
                        sys.exit(-1)

                    curV = allClinDict[aKey]
                    numClin = len(curV)
                    tmpV = [0] * numClin

                    for kk in range(numClin):
                        if (curV[kk] == "NA"):
                            tmpV[kk] = "NA"
                        elif (isRoman):
                            tmpV[kk] = translateRoman(curV[kk], usePrefix)
                        else:
                            tmpV[kk] = translateArabic(curV[kk], usePrefix)

                        if (0):
                            if (tmpV[kk] == 0):
                                print " why is tmpV[kk] still ZERO ??? ", kk, numClin, curV[kk], usePrefix, tmpV[kk]

                    numNA = 0
                    notNA = 0
                    for kk in range(numClin):
                        if (tmpV[kk] == "NA"):
                            numNA += 1
                        else:
                            notNA += 1

                    if (numNA > 10 * notNA):
                        print " --> NOT adding this new feature <%s> " % newLabel, list(set(tmpV)), numNA, notNA, usePrefix, isRoman
                    else:
                        print " --> ADDING new feature !!! <%s> " % newLabel, list(set(tmpV)), numNA, notNA, usePrefix, isRoman
                        allClinDict[newLabel] = tmpV

                    print " "

    print " "
    print " "

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getMappingDict(featName, auxName):

    mapDict = {}

    if (featName[1] == ':'):
        if (featName[6] == ':'):
            tokenList = featName.split(':')
            tmpFeatName = tokenList[2]
    else:
        tmpFeatName = featName

    try:
        mapFilename = "../" + auxName + "/" + tmpFeatName + ".map"
        fh = file(mapFilename)
        firstLine = 1
        for aLine in fh:
            aLine = aLine.strip()
            ## aLine = aLine.upper()
            tokenList = aLine.split('\t')
            if (firstLine):
                if (tokenList[0].upper() == tmpFeatName.upper()):
                    numNew = len(tokenList) - 1
                    newNames = tokenList[1:]
                    print newNames
                    firstLine = 0
                else:
                    print " ERROR ??? invalid mapping file ??? "
                    print mapFilename
                    print tokenList
                    print tmpFeatName
                    print " FAILING out of TRY "
                    sys.exit(-1)
            else:
                mapDict[str(tokenList[0])] = tokenList[1:]
        fh.close()
        print " mapping dictionary read from <%s> : " % mapFilename
        print mapDict
        print " "
        return (mapDict, newNames)
    except:
        return (mapDict, [])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getMapping ( mapDict, curV, ii ):

    for k in mapDict.keys():
        if ( k.lower() == curV.lower() ):
            return ( mapDict[k][ii] )

    print " FAILED TO GET MAPPING ??? ", curV, ii
    print mapDict

    sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def addDerivedFeatures(allClinDict, auxName):

    print " "
    print " "
    print " in addDerivedFeatures ... "

    keyList = allClinDict.keys()
    keyList.sort()

    for aKey in keyList:

        if (aKey == "bcr_patient_barcode"):
            continue
        (keyType, nCount, nNA, nCard, labelList, labelCount) = miscClin.lookAtKey(allClinDict[aKey])
        print " considering key <%s> " % (aKey), keyType, nCard

        if (keyType == "NOMINAL"):
            if (nCard > 2 and nCard < 25):

                tmpKey = aKey.lower()

                tmpList = []
                for aLabel in labelList:
                    tmpL = str(aLabel)
                    if (tmpL not in tmpList):
                        tmpList += [tmpL]
                labelList = tmpList

                if (1):
                    print " considering this categorical feature ... ", aKey, keyType, nCard, labelList, labelCount

                    (mapDict, newNames) = getMappingDict(aKey, auxName)

                    # if there is no mapping file, then we won't be making any
                    # new features ...
                    if (len(newNames) == 0):
                        continue

                    # sanity check ...
                    if (0):
                        for bKey in mapDict.keys():
                            if ( stringInList_CaseInsens ( bKey, labelList ) ):
                                print " ERROR ??? mapping does not match this feature ??? "
                                print mapDict
                                print labelList
                                sys.exit(-1)
                    if (1):
                        for bLabel in labelList:
                            try:
                                if ( not stringInList_CaseInsens ( bLabel, mapDict.keys() ) ):
                                    print " ************************************************** "
                                    print " ERROR ??? feature value not in mapDict ??? ", bLabel
                                    print " labelList : ", labelList
                                    print " mapDict   : ", mapDict
                                    print " --> WILL NOT ADD ANY DERIVED FEATURES AT THIS TIME "
                                    print " ************************************************** "
                                    continue
                                    # sys.exit(-1)
                            except:
                                doNothing = 1

                    # if there is no mapping file, then we won't be making any
                    # new features ...
                    if (len(newNames) == 0):
                        continue

                    # but if we do have one or more mappings, then we need
                    # to create those features ...
                    for ithName in range(len(newNames)):
                        aName = newNames[ithName]
                        print " looping over %d mappings ... " % len(newNames), ithName, aName

                        # the first thing we need to figure out is whether this is another
                        # categorical feature, or a numerical one ...
                        isNum = 1
                        uVec = []
                        for bKey in mapDict.keys():
                            curVal = mapDict[bKey][ithName]
                            if (curVal == "NA"):
                                continue
                            if ( stringInList_CaseInsens ( curVal, uVec ) ):
                                uVec += [curVal]
                            try:
                                fVal = float(curVal)
                            except:
                                isNum = 0

                        print " is numerical ??? ", isNum
                        if (len(uVec) == 1):
                            print " mapping to a constant ??? "
                            sys.exit(-1)
                        elif (len(uVec) == 2):
                            print " mapping is binary "
                            # if the mapping produces a binary feature, then
                            # over-ride the numerical feature
                            if (isNum):
                                print " over-riding the fact that the features LOOKS numerical ... "
                                isNum = 0

                        if (aName[1] == ":"):
                            if (aName[0] == "N"):
                                if (not isNum):
                                    print " ERROR ??? new feature does not look to be numerical ???? "
                                    print aName, uVec
                                    sys.exit(-1)

                        # start setting up the new feature ...
                        newLabel = aName
                        if (newLabel in allClinDict.keys()):
                            print " this feature label already exists ??? ", newLabel
                            sys.exit(-1)

                        curV = allClinDict[aKey]
                        numClin = len(curV)
                        tmpV = [0] * numClin

                        for kk in range(numClin):
                            if (curV[kk].upper() == "NA"):
                                tmpV[kk] = "NA"
                            else:
                                try:
                                    tmpV[kk] = getMapping ( mapDict, curV[kk], ithName )
                                    ## tmpV[kk] = mapDict[curV[kk]][ithName]
                                except:
                                    print " ERROR ??? failed to map ??? setting to NA but MUST FIX !!! "
                                    print kk, curV[kk], ithName
                                    print mapDict
                                    if (1):
                                        tmpV[kk] = "NA"
                                    else:
                                        sys.exit(-1)

                        numNA = 0
                        notNA = 0
                        for kk in range(numClin):
                            if (tmpV[kk] == "NA"):
                                numNA += 1
                            else:
                                notNA += 1

                        if (numNA > 10 * notNA):
                            print " --> NOT adding this new feature <%s> " % newLabel, list(set(tmpV)), numNA, notNA
                        else:
                            print " --> ADDING new feature !!! <%s> " % newLabel, list(set(tmpV)), numNA, notNA
                            allClinDict[newLabel] = tmpV

                    print " "

    print " "
    print " "
    print " RETURNING from addDerivedFeatures ... "

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this function creates N binary indicator vectors based on a single nominal
# (categorical) variable of cardinality N -- the indicator vectors still
# contain strings ("I0" and "I1") so that we can tell that they are still not
# truly "numeric" vectors ...


def addIndicatorFeatures(allClinDict):

    magicStrings = ["patient", "person", "vital", "surviv", "race", "ethnic",
                    "prior", "gender", "age_at", "ageat", "radiation", "chemo",
                    "therapy", "treat", "performance", "days_to_", "daysto",
                    "year_of", "yearof", "surgical", "recurrence", "pregnancies"]

    keyList = allClinDict.keys()
    keyList.sort()

    for aKey in keyList:
        if (aKey == "bcr_patient_barcode"):
            continue
        (keyType, nCount, nNA, nCard, labelList,
         labelCount) = miscClin.lookAtKey(allClinDict[aKey])

        if (keyType == "NOMINAL"):
            if (nCard > 2 and nCard < 27):

                print " "
                print " "
                print " in addIndicatorFeatures ... ", aKey, keyType, nCard, labelList, labelCount

                for aLabel in labelList:

                    # sometimes even though we have a "categorical" feature, some of the
                    # categories appear to be integers or floating point values
                    # ...
                    if (type(aLabel) is float):
                        print " we seem to have a floating point value ??? ", aLabel
                        iVal = int(aLabel + 0.001)
                        xVal = float(aLabel) - iVal
                        print iVal, xVal
                        if (abs(xVal) < 0.001):
                            aLabel = "%d" % iVal
                        else:
                            aLabel = str(aLabel)
                    elif (type(aLabel) is int):
                        iVal = int(aLabel)
                        aLabel = "%d" % iVal

                    print " "
                    ## print aKey, aLabel
                    try:
                        # 012345678901234567890123456789...
                        # C:CLIN:<label>
                        # C:CLIN:<label>:a:b:c:d:e
                        if (aKey[1] == ":" and aKey[6] == ":"):
                            # if this feature name already has a prefix (eg
                            # "C:CLIN:")
                            featType = aKey[2:7]
                            i1 = aKey[7:].find(':')
                            if (i1 < 0):
                                # if there are no further ':'
                                firstName = aKey[7:]
                                secondName = ":::::"
                            else:
                                # if there are ...
                                firstName = aKey[7:7 + i1]
                                secondName = aKey[7 + i1 + 1:]
                            print " (a) got to here ... ", featType, aLabel, firstName, secondName
                            newLabel = "B:" + featType + \
                                "I(" + aLabel + "|" + firstName + ")" + \
                                secondName
                            print " (b) got to here ... ", newLabel
                            if (newLabel.find("|):") > 0):
                                print " (a) BAILING !!!! ", newLabel
                                sys.exit(-1)
                        else:
                            # here we really need to have some way to guess whether this
                            # should be a CLIN or a SAMP feature ...
                            typeString = "UNK"
                            for aString in magicStrings:
                                if (aKey.find(aString) >= 0):
                                    typeString = "CLIN"
                            if (typeString == "UNK"):
                                print " defaulting to type SAMP for this feature : <%s> " % (aKey)
                                typeString = "SAMP"

                            print " (c) got to here ... ", typeString, aLabel

                            newLabel = "B:" + typeString + ":" + \
                                "I(" + aLabel + "|" + aKey + ")"
                    except:
                        print " (b) BAILING !!! "
                        print " ERROR in addIndicatorFeatures ??? ", aLabel, aKey
                        sys.exit(-1)

                    # make sure there are no blanks ...
                    newLabel = tsvIO.replaceBlanks(newLabel, "_")

                    if (newLabel in allClinDict.keys()):
                        print " this indicator variable already exists so I will not make a new one ... ", newLabel
                        continue

                    curV = allClinDict[aKey]
                    numClin = len(curV)
                    tmpV = [0] * numClin
                    print "     ... looping over %d values ... default new value is zero " % (numClin)
                    for kk in range(numClin):
                        print kk, allClinDict[aKey][kk], aLabel, type(allClinDict[aKey][kk]), type(aLabel)
                        if (allClinDict[aKey][kk] == "NA"):
                            tmpV[kk] = "NA"
                        elif (str(allClinDict[aKey][kk]).lower() == str(aLabel).lower()):
                            tmpV[kk] = 1
                    print " adding new feature : ", newLabel
                    allClinDict[newLabel] = tmpV

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def addPairwiseIndicatorFeatures(allClinDict):

    magicStrings = ["patient", "person", "vital", "surviv", "race", "ethnic",
                    "prior", "gender", "age_at", "ageat", "radiation", "chemo",
                    "therapy", "treat", "performance", "days_to_", "daysto",
                    "year_of", "yearof", "surgical", "recurrence", "pregnancies"]

    print " "
    print " "

    keyList = allClinDict.keys()
    keyList.sort()

    for aKey in keyList:

        if (aKey == "bcr_patient_barcode"):
            continue
        (keyType, nCount, nNA, nCard, labelList,
         labelCount) = miscClin.lookAtKey(allClinDict[aKey])

        if (keyType == "NOMINAL"):

            # we do this only for categorical features with 3-9 categories
            if (nCard > 2 and nCard < 10):

                print " "
                print " in addPairwiseIndicatorFeatures ... ", aKey, keyType, nCard, labelList, labelCount

                for ak in range(len(labelList)):
                    aLabel = labelList[ak]

                    for bk in range(ak + 1, len(labelList)):
                        bLabel = labelList[bk]

                        print " aLabel=<%s>  bLabel=<%s> " % (aLabel, bLabel)

                        try:
                            if (aKey[1] == ":" and aKey[6] == ":"):
                                i1 = aKey[7:].find(':')
                                if (i1 < 0):
                                    i1 = len(aKey)
                                    i2 = len(aKey)
                                else:
                                    i1 = i1 + 7
                                    i2 = aKey[(i1 + 1):].find(':')
                                    if (i2 < 0):
                                        i2 = len(aKey)

                                if (i2 > 0 and i2 < len(aKey)):
                                    newLabel = "B:" + \
                                        aKey[
                                            2:7] + "I(" + aLabel + "," + bLabel + "|" + aKey[7:i1] + ")" + aKey[i2:]
                                else:
                                    newLabel = "B:" + \
                                        aKey[
                                            2:7] + "I(" + aLabel + "," + bLabel + "|" + aKey[7:i1] + ")" + "::::"

                            else:
                                # here we really need to have some way to guess whether this
                                # should be a CLIN or a SAMP feature ...
                                typeString = "UNK"
                                for aString in magicStrings:
                                    if (aKey.find(aString) >= 0):
                                        typeString = "CLIN"
                                if (typeString == "UNK"):
                                    print " defaulting to type SAMP for this feature : <%s> " % (aKey)
                                    typeString = "SAMP"
                                newLabel = "B:" + typeString + ":" + \
                                    "I(" + aLabel + "," + bLabel + "|" + aKey + ")" + \
                                    "::::"

                        except:
                            print " NOT continuing in addPairwiseIndicatorFeatures !!! ", aLabel, bLabel, aKey
                            continue

                        # make sure there are no blanks ...
                        newLabel = tsvIO.replaceBlanks(newLabel, "_")
                        print "             --> new label: <%s> " % newLabel

                        if (newLabel in allClinDict.keys()):
                            print " this indicator variable already exists so I will not make a new one ... ", newLabel
                            continue

                        curV = allClinDict[aKey]
                        numClin = len(curV)
                        tmpV = ["NA"] * numClin
                        for kk in range(numClin):
                            if (allClinDict[aKey][kk].lower() == aLabel.lower()):
                                tmpV[kk] = 1
                            elif (allClinDict[aKey][kk].lower() == bLabel.lower()):
                                tmpV[kk] = 0

                        print " adding new feature : ", newLabel
                        # print tmpV
                        allClinDict[newLabel] = tmpV

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if ( (len(sys.argv)!=4) and (len(sys.argv)!=5) ):
        print " Usage : %s <input TSV> <output TSV> <public/private> [auxName] " % sys.argv[0]
        print " ERROR -- bad command line arguments "
        sys.exit(-1)

    tsvNameIn = sys.argv[1]
    tsvNameOut = sys.argv[2]
    ppString = sys.argv[3]
    if ( len(sys.argv) == 5 ):
        auxName = sys.argv[4]
    else:
        auxName = "aux"

    # test out readTSV ...
    ## tsvName = "coad_read_clinical.27jan.tsv"
    print " "
    print " ****************************************************************** "
    print " reading input file <%s> " % tsvNameIn
    allClinDict = tsvIO.readTSV(tsvNameIn)
    print " A "
    checkBarcodes(allClinDict)

    # take a look ...
    (naCounts, otherCounts) = miscClin.lookAtClinDict(allClinDict)

    if (1):
        # remove constant-value keys ...
        allClinDict = miscClin.removeConstantKeys(allClinDict)
        print " B "
        checkBarcodes(allClinDict)

    if (1):
        # remove uninformative keys ...
        allClinDict = miscClin.removeUninformativeKeys(allClinDict)
        print " C "
        checkBarcodes(allClinDict)

    # check the tumor stage based on the other T/N/M definitions, update if possible
    # (and if the original setting was "NA")
    if (1):
        allClinDict = checkTumorStage(allClinDict)
        print " D "
        checkBarcodes(allClinDict)

    # new as of 16aug13 ... vital_status strings are inconsistent between
    # 'living' or 'alive' or 'deceased' or 'dead' ...
    #           --> standard should be "Alive" or "Dead"
    if (1):
        allClinDict = checkVitalStatus(allClinDict)
        print " E "
        checkBarcodes(allClinDict)

    # new as of 13sep13 ... makig 'age' a continuous feature that
    # exactly matches the days_to_birth ...
    if (1):
        allClinDict = updateAge(allClinDict)
        print " F "
        checkBarcodes(allClinDict)

    # remap some categorical features to numerical features ...
    # oh, this shouldn't still be here, should it ??? 15aug2014
    if (0):
        allClinDict = remapCategoricalFeatures(allClinDict)
        print " G "
        checkBarcodes(allClinDict)

    # add the lymphnodes_positive fraction ...
    allClinDict = computeLymphnodesFraction(allClinDict)
    print " H "
    checkBarcodes(allClinDict)

    # fill in some missing information that we have collected from elsewhere
    # ...
    if (0):
        allClinDict = addMissingInfo(allClinDict)
        print " I "
        checkBarcodes(allClinDict)

    # NEW: look at some of the "days_to_" fields and do some fix-ups ...
    if (1):
        allClinDict = addFollowupInfo(allClinDict)
        print " J "
        checkBarcodes(allClinDict)

    # new as of 04dec13 ... checking that vital_status and various days_to_???
    # features are consistent ...
    if (1):
        allClinDict = checkFollowupInfo(allClinDict)
        print " K "
        checkBarcodes(allClinDict)

    # take a look at the updated dictionary ...
    (naCounts, otherCounts) = miscClin.lookAtClinDict(allClinDict)

    if (1):
        # remove constant-value keys ...
        allClinDict = miscClin.removeConstantKeys(allClinDict)
        print " L "
        checkBarcodes(allClinDict)

    if (0):
        # removing this ... 02Feb2012 SMR

        # filter out keys with too little information ...
        # or maybe leave nearly everything in ;-)
        categorical_naFracThresh = 0.90
        numerical_naFracThresh = 0.90
        classSize_minFracThresh = 0.
        classSize_maxFracThresh = 0.995

        allClinDict = miscClin.filterClinDict(allClinDict,
                                              categorical_naFracThresh,
                                              numerical_naFracThresh,
                                              classSize_minFracThresh,
                                              classSize_maxFracThresh)
        print " M "
        checkBarcodes(allClinDict)

    # try to abbreviate clinical feature strings
    allClinDict = abbrevCategStrings(allClinDict)
    print " N "
    checkBarcodes(allClinDict)

    if (0):
        # automatically generate indicator features for remaining categorical
        # features
        allClinDict = addIndicatorFeatures(allClinDict)
        print " O "
        checkBarcodes(allClinDict)
        # new 10Feb2012 : add pairwise indicator features
        allClinDict = addPairwiseIndicatorFeatures(allClinDict)
        print " P "
        checkBarcodes(allClinDict)

    # new 09Jan2013 : try to add numeric features that map the non-binary categorical features ...
    # as of 06Aug2014, this is only done for "private" runs
    if ( ppString == "private" ):
        allClinDict = addDerivedFeatures(allClinDict, auxName)
        print " Q "
        checkBarcodes(allClinDict)

    # look at pairwise MI ...
    if (0):
        print " "
        print " ****************************************** "
        print " * looking at pairwise Mutual Information * "
        print " ****************************************** "
        print " "
        miscClin.pairwiseMI(allClinDict, "miNetwork.A.13feb12")

    # look at the data again and re-pick the 'best' key order ...
    (naCounts, otherCounts) = miscClin.lookAtClinDict(allClinDict)
    bestKeyOrder = miscClin.getBestKeyOrder(allClinDict, naCounts)

    doWriteTSV = 1
    if (doWriteTSV):
        outName = tsvNameOut
        tsvIO.writeTSV_clinical(allClinDict, bestKeyOrder, outName)

    if (1):
        outName = tsvNameOut[:-4] + ".flipNumeric.tsv"
        tsvIO.writeTSV_clinicalFlipNumeric(
            allClinDict, bestKeyOrder, outName)

    print " "
    print " "
    print " FINISHED "
    print " "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
