# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscClin
import tsvIO

import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

remapDict = {}

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


def renameB2mutations(allClinDict):

    # print " "
    # print " in renameB2mutations ... "

    lastGene = ''
    fh = file("/proj/ilyalab/TCGA/COAD+READ/clinicalPlus/B2_mappings.tsv")
    B2names = {}
    for aLine in fh:
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        # print tokenList

        if (len(tokenList) == 3):
            lastGene = tokenList[0]
            newName = lastGene + "_" + tokenList[1]
            oldName = "B2_" + tokenList[2]
        elif (len(tokenList) == 2):
            newName = lastGene + "_" + tokenList[0]
            oldName = "B2_" + tokenList[1]

        oldName = oldName.lower()
        newName = newName.lower()

        if (not newName.endswith("_mut")):
            newName += "_mut"

        if (newName.find(' ') >= 0):
            print " ERROR ??? blank ??? <%s> " % newName
            sys.exit(-1)
        if (oldName in B2names.keys()):
            print " ERROR ??? oldName already in dict ??? <%s> " % oldName
            sys.exit(-1)
        B2names[oldName] = newName

    fh.close()

    keyList = allClinDict.keys()
    keyList.sort()
    for aKey in keyList:

        aKey2 = aKey.lower()
        if (aKey2 in B2names.keys()):
            newKey = B2names[aKey2]
            allClinDict[newKey] = allClinDict[aKey]
            del allClinDict[aKey]
            # print aKey2, newKey, len(allClinDict[newKey])

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def computeLymphnodesFraction(allClinDict):

    aKey = "number_of_lymphnodes_positive_by_he"
    bKey = "number_of_lymphnodes_examined"

    if (aKey not in allClinDict.keys()):
        print " "
        print " skipping computeLymphnodesFraction "
        return (allClinDict)
    if (bKey not in allClinDict.keys()):
        print " "
        print " skipping computeLymphnodesFraction "
        return (allClinDict)

    print " "
    print " in computeLymphnodesFractoin ... "

    numClin = len(allClinDict[aKey])
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
    allClinDict["fraction_lymphnodes_positive_by_he"] = newV

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# fields of interest:
# days_to_birth
# days_to_initial_pathologic_diagnosis        <-- this is always 0
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

    # FIRST: if there is a days_to_last_known_alive, then check that it is
    # used consistently, otherwise create it

    aKey = "days_to_last_known_alive"
    bKey = "days_to_last_followup"
    cKey = "days_to_death"

    haveA = (aKey in allClinDict.keys())
    haveB = (bKey in allClinDict.keys())
    haveC = (cKey in allClinDict.keys())

    if (haveA):

        # if we have the "days_to_last_known_alive" field, check that it
        # is consistent with the other two fields ...
        numClin = len(allClinDict[aKey])
        numNotNA = 0
        for kk in range(numClin):

            if (haveC):
                if (str(allClinDict[cKey][kk]).upper() != "NA"):
                    allClinDict[aKey][kk] = allClinDict[cKey][kk]

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
        if (haveB):
            numClin = len(allClinDict[bKey])
        elif (haveC):
            numClin = len(allClinDict[cKey])
        else:
            print " FATAL ERROR ??? no followup or death information ??? "
            sys.exit(-1)

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
        print newVec
        allClinDict["days_to_last_known_alive"] = newVec

    # SECOND: if there is a "days_to_submitted_specimen_dx", then create
    # a set of "days_to_" features that instead of being relative
    # to "initial_pathologic_diagnosis" are relative to "submitted_specimen"

    aKey = "days_to_submitted_specimen_dx"
    tKey = "days_to_initial_pathologic_diagnosis"
    try:
        numClin = len(allClinDict[aKey])
        for bKey in allClinDict.keys():
            if (bKey == aKey):
                continue
            if (bKey.startswith("days_to_")):
                newKey = bKey + "_relSS"
                newVec = [0] * numClin
                numNotNA = 0
                for kk in range(numClin):
                    newVec[kk] = "NA"
                    if (str(allClinDict[aKey][kk]).upper() == "NA"):
                        continue
                    if (str(allClinDict[tKey][kk]).upper() == "NA"):
                        continue
                    deltaDays = allClinDict[aKey][kk] - allClinDict[tKey][kk]
                    if (str(allClinDict[bKey][kk]).upper() == "NA"):
                        continue
                    newVec[kk] = allClinDict[bKey][kk] - deltaDays
                    numNotNA += 1
                print " adding new key (%d) : " % numNotNA, newKey
                print newVec
                allClinDict[newKey] = newVec
    except:
        doNothing = 1

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def addMissingInfo(allClinDict):

    barcodeList = [
        "TCGA-A6-2672", "TCGA-A6-2676", "TCGA-A6-3809", "TCGA-A6-2683", "TCGA-A6-3808",
        "TCGA-AY-4070", "TCGA-AY-4071", "TCGA-A6-3807", "TCGA-A6-3810", "TCGA-AF-2692"]
    tumorList = [
        "COAD",         "COAD",         "COAD",         "COAD",         "COAD",
        "READ",         "READ",         "COAD",         "COAD",         "READ"]
    tissueList = [
        "COLON",        "COLON",        "COLON",        "COLON",        "COLON",
        "RECTUM",       "RECTUM",       "COLON",        "COLON",        "RECTUM"]
    genderList = [
        "FEMALE",       "FEMALE",       "NA",           "FEMALE",       "NA",
        "NA",           "NA",           "FEMALE",       "MALE",         "FEMALE"]

    numClin = len(allClinDict["bcr_patient_barcode"])

    for kk in range(len(barcodeList)):
        aCode = barcodeList[kk]
        for ii in range(numClin):
            if (allClinDict["bcr_patient_barcode"][ii] == aCode):
                print " adding missing information ... ", aCode, tumorList[kk], tissueList[kk], genderList[kk]
                allClinDict["disease_code"][ii] = tumorList[kk]
                allClinDict["tumor_tissue_site"][ii] = tissueList[kk]
                allClinDict["gender"][ii] = genderList[kk]

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

    numClin = len(allClinDict["bcr_patient_barcode"])
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

    for ii in range(numClin):
        aCode = allClinDict["bcr_patient_barcode"][ii]
        curTumorStage = allClinDict["tumor_stage"][ii]
        curT = allClinDict["primary_tumor_pathologic_spread"][ii]
        curN = allClinDict["lymphnode_pathologic_spread"][ii]
        curM = allClinDict["distant_metastasis_pathologic_spread"][ii]
        # print " checking tumor stage for <%s> <%s> <%s> <%s> <%s> " % (
        # aCode, curTumorStage, curN, curM, curT )

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
            allClinDict["tumor_stage"][ii] = newStage

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
        if (aString.startswith("grade_")):
            for ii in range(len(oneKey)):
                aLabel = str(oneKey[ii])
                if (aLabel.upper() == "NA"):
                    continue
                if (not aLabel.startswith("grade_")):
                    try:
                        iVal = int(aLabel)
                        aString = "grade_%d" % iVal
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
            print " this is weird, no ??? ", aInt, aString
            print oneKey
            sys.exit(-1)

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
            return (aLabel[:nn].lower())
        if (nn >= len(bLabel)):
            return (aLabel[:nn].lower())

    return (aLabel[:nn].lower())

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
        return (aLabel[nn + 1:].lower())

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
                    cLabel = cLabel.lower()
                    if (cLabel.startswith(commonPrefix)):
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
                    cLabel = cLabel.lower()
                    if (cLabel.startswith(commonPrefix)):
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
                    cLabel = cLabel.lower()
                    if (cLabel.endswith(commonSuffix)):
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
                    cLabel = cLabel.lower()
                    if (cLabel.endswith(commonSuffix)):
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

        if (aKey == "bcr_patient_barcode"):
            continue
        (keyType, nCount, nNA, nCard, labelList,
         labelCount) = miscClin.lookAtKey(allClinDict[aKey])

        if (keyType == "NOMINAL"):

            # remove weird characters from the strings ...
            print " calling removeSpecialChars ... <%s> " % (aKey)
            allClinDict[aKey] = removeSpecialChars(allClinDict[aKey])
            (keyType, nCount, nNA, nCard, labelList,
             labelCount) = miscClin.lookAtKey(allClinDict[aKey])

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

                print aKey, labelList, maxLen

                # first try at making the labels a bit shorter by removing
                # parenthetical elements ...
                allClinDict[aKey] = removeParens(allClinDict[aKey])
                (keyType, nCount, nNA, nCard, labelList,
                 labelCount) = miscClin.lookAtKey(allClinDict[aKey])

                maxLen = 0
                for aLabel in labelList:
                    maxLen = max(maxLen, len(aLabel))
                print aKey, labelList, maxLen

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
                        print aKey, labelList, maxLen
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

    if ((nHas + 2) >= nLabel):
        return (1)
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


def getMappingDict(featName):

    mapDict = {}

    try:
        mapFilename = "../aux/" + featName + ".map"
        fh = file(mapFilename)
        firstLine = 1
        for aLine in fh:
            aLine = aLine.strip()
            tokenList = aLine.split('\t')
            if (firstLine):
                if (tokenList[0] == featName):
                    numNew = len(tokenList) - 1
                    newNames = tokenList[1:]
                    print newNames
                    firstLine = 0
                else:
                    print " ERROR ??? invalid mapping file ??? "
                    print mapFilename
                    print tokenList
                    sys.exit(-1)
            else:
                mapDict[tokenList[0]] = tokenList[1:]
        fh.close()
        print " "
        print mapDict
        print " "
        return (mapDict, newNames)
    except:
        return (mapDict, [])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def addDerivedFeatures(allClinDict):

    print " "
    print " "
    print " in addDerivedFeatures ... "

    keyList = allClinDict.keys()
    keyList.sort()

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

                    (mapDict, newNames) = getMappingDict(aKey)
                    # sanity check ...
                    for bKey in mapDict.keys():
                        if (bKey.upper() not in labelList):
                            print " ERROR ??? mapping does not match this feature ??? "
                            print mapDict
                            print labelList
                            sys.exit(-1)

                    # if there is no mapping file, then we won't be making any
                    # new features ...
                    if (len(newNames) == 0):
                        continue

                    # but if we do have one or more mappings, then we need
                    # to create those files ...
                    for ithName in range(len(newNames)):
                        aName = newNames[ithName]
                        print ithName, aName

                        # the first thing we need to figure out is whether this is another
                        # categorical feature, or a numerical one ...
                        isNum = 1
                        uVec = []
                        for bKey in mapDict.keys():
                            curVal = mapDict[bKey][ithName]
                            if (curVal == "NA"):
                                continue
                            if (curVal not in uVec):
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
                                    tmpV[kk] = mapDict[curV[kk]
                                                       .upper()][ithName]
                                except:
                                    print " failed to map ??? "
                                    print kk, curV[kk].upper(), ithName
                                    print mapDict
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
            if (nCard > 2 and nCard < 11):

                print " "
                print " "
                print " in addIndicatorFeatures ... ", aKey, keyType, nCard, labelList, labelCount

                for aLabel in labelList:
                    print " "
                    print aKey, aLabel
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
                                    aKey[2:7] + \
                                    "I(" + aLabel + "|" + \
                                    aKey[7:i1] + ")" + aKey[i2:]
                            else:
                                newLabel = "B:" + \
                                    aKey[2:7] + \
                                    "I(" + aLabel + "|" + \
                                    aKey[7:i1] + ")" + "::::"
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

                            # sometimes even though we have a "categorical" feature, some of the
                            # categories appear to be integers or floating
                            # point values ...
                            if (type(aLabel) is float):
                                iVal = int(aLabel + 0.001)
                                xVal = float(aLabel) - iVal
                                if (abs(xVal) < 0.001):
                                    aLabel = "%d" % iVal
                                else:
                                    aLabel = str(aLabel)
                            elif (type(aLabel) is int):
                                iVal = int(aLabel)
                                aLabel = "%d" % iVal

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

    if (len(sys.argv) != 3):
        print " Usage : %s <input TSV> <output TSV> " % sys.argv[0]
        sys.exit(-1)

    tsvNameIn = sys.argv[1]
    tsvNameOut = sys.argv[2]

    # test out readTSV ...
    ## tsvName = "coad_read_clinical.27jan.tsv"
    print " "
    print " ****************************************************************** "
    print " reading input file <%s> " % tsvNameIn
    allClinDict = tsvIO.readTSV(tsvNameIn)

    # take a look ...
    (naCounts, otherCounts) = miscClin.lookAtClinDict(allClinDict)

    if (1):
        # remove constant-value keys ...
        allClinDict = miscClin.removeConstantKeys(allClinDict)

    if (1):
        # remove uninformative keys ...
        allClinDict = miscClin.removeUninformativeKeys(allClinDict)

    # check the tumor stage based on the other T/N/M definitions, update if possible
    # (and if the original setting was "NA")
    if (1):
        allClinDict = checkTumorStage(allClinDict)

    # remap some categorical features to numerical features ...
    if (1):
        allClinDict = remapCategoricalFeatures(allClinDict)

    # rename Brady's mutation fields
    if (0):
        allClinDict = renameB2mutations(allClinDict)

    # add the lymphnodes_positive fraction ...
    allClinDict = computeLymphnodesFraction(allClinDict)

    # fill in some missing information that we have collected from elsewhere
    # ...
    if (0):
        allClinDict = addMissingInfo(allClinDict)

    # NEW: look at some of the "days_to_" fields and do some fix-ups ...
    if (1):
        allClinDict = addFollowupInfo(allClinDict)

    # total hack ...
    if (0):
        if ("location" in allClinDict.keys()):
            del allClinDict["location"]

    # take a look at the updated dictionary ...
    (naCounts, otherCounts) = miscClin.lookAtClinDict(allClinDict)

    if (1):
        # remove constant-value keys ...
        allClinDict = miscClin.removeConstantKeys(allClinDict)

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

    # try to abbreviate clinical feature strings
    allClinDict = abbrevCategStrings(allClinDict)

    # automatically generate indicator features for remaining categorical
    # features
    allClinDict = addIndicatorFeatures(allClinDict)

    # new 10Feb2012 : add pairwise indicator features
    allClinDict = addPairwiseIndicatorFeatures(allClinDict)

    # new 09Jan2013 : try to add numeric features that map the non-binary categorical features ...
    ## allClinDict = addNumericalFeatures ( allClinDict )
    allClinDict = addDerivedFeatures(allClinDict)

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
