# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import sys

from env import gidgetConfigVars
import miscClin
import miscTCGA
import path
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getFeatList(fName):

    fList = []

    fh = file(fName)
    for aLine in fh:
        aLine = aLine.strip()
        # print aLine
        if aLine not in fList:
            fList += [aLine]

    fList.sort()
    return (fList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def findKey ( allClinDict, keyStr ):

    for aKey in allClinDict.keys():
        if ( aKey == keyStr ): return ( aKey )
        tmpStr = ":" + keyStr + ":"
        if ( aKey.find(tmpStr) >= 0 ): return ( aKey )

    print " NOT found ? ", keyStr

    keyStr = keyStr.lower()
    for aKey in allClinDict.keys():
        bKey = aKey.lower()
        if ( bKey.find(keyStr) >= 0 ): 
            print " possible match: ", aKey

    print " WARNING !!! failed to findKey in reParseClin_CESC "
    sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def assignBMIcategory ( bmi ):
    if ( bmi < 18.5 ): return ( "underweight" )
    if ( bmi < 25 ): return ( "normal" )
    if ( bmi < 30 ): return ( "overweight" )
    return ( "obese" )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def addBMI ( allClinDict ):

    bmiVec = []
    catVec = []

    weightKey = findKey ( allClinDict, "weight" )
    heightKey = findKey ( allClinDict, "height" )

    for ii in range(len(allClinDict[weightKey])):
        w = allClinDict[weightKey][ii]
        h = allClinDict[heightKey][ii]
        try:
            bmi = float(w) / ( float(h/100.) * float(h/100.) )
            bmiCat = assignBMIcategory ( bmi )
            ## print w, h, bmi, bmiCat
            catVec += [ bmiCat ]
            bmiVec += [ bmi ]
        except:
            ## print w, h, "NA"
            ## if ( w != "NA" ): print " weight is not NA ??? "
            ## if ( h != "NA" ): print " height is not NA ??? "
            bmiVec += [ "NA" ]
            catVec += [ "NA" ]

    allClinDict["N:CLIN:BMI:::::"] = bmiVec
    allClinDict["C:CLIN:BMIcat:::::"] = catVec

    ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict["N:CLIN:BMI:::::"] )
    print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount

    ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict["C:CLIN:BMIcat:::::"] )
    print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount
    print labelList

    return ( allClinDict )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def checkMenopause ( allClinDict ):

    print " in checkMenopause ... "
    print " "

    newVec = []

    menopauseKey = findKey ( allClinDict, "menopause_status" )
    ageKey = findKey ( allClinDict, "age_at_initial_pathologic_diagnosis" )

    for ii in range(len(allClinDict[ageKey])):
        m = allClinDict[menopauseKey][ii]
        a = allClinDict[ageKey][ii]
        if ( m.startswith("Pre_") ):
            newVec += [ "Pre" ]
        elif ( m.startswith("Post_") ):
            newVec += [ "Post" ]
        elif ( a >= 50 ):
            newVec += [ "Post" ]
        else:
            newVec += [ "Pre" ]

    allClinDict["C:CLIN:menopause50:::::"] = newVec

    ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict["C:CLIN:menopause50:::::"] )
    print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount
    print labelList

    return ( allClinDict )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def addAgeSplits ( allClinDict ):

    print " in addAgeSplits ... "
    print " "

    ageKey = findKey ( allClinDict, "age_at_initial_pathologic_diagnosis" )
    numP = len(allClinDict[ageKey])

    youngMax = [ 30, 35, 40, 45, 50, 40, 40, 35 ]
    oldMin   = [ 30, 35, 40, 45, 50, 45, 50, 55 ]
    numC = len(youngMax)
    newVecs = [0] * numC
    for iC in range(numC):
        newVecs[iC] = ["NA"] * numP

    for ii in range(numP):
        a = allClinDict[ageKey][ii]
        if ( a != "NA" ):
            for iC in range(numC):
                if ( a <= youngMax[iC] ):
                    newVecs[iC][ii] = "young"
                elif ( a > oldMin[iC] ):
                    newVecs[iC][ii] = "old"

    for iC in range(numC):
        if ( youngMax[iC] == oldMin[iC] ):
            keyString = "B:CLIN:ageSplit_%d:::::" % ( youngMax[iC] )
        else:
            keyString = "B:CLIN:ageSplit_%d_%d:::::" % ( youngMax[iC], oldMin[iC] )
        print keyString
        allClinDict[keyString] = newVecs[iC]
        ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict[keyString] )
        print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount
        print labelList

    return ( allClinDict )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def checkCancerStatus ( allClinDict ):

    print " in checkCancerStatus ... "
    print " "

    newSite = []

    nteKey = findKey ( allClinDict, "new_tumor_event_after_initial_treatment" )
    siteKey = findKey ( allClinDict, "new_neoplasm_event_occurrence_anatomic_site" )
    typeKey = findKey ( allClinDict, "new_neoplasm_event_type" )
    textKey = findKey ( allClinDict, "new_neoplasm_occurrence_anatomic_site_text" )
    days2nteKey = findKey ( allClinDict, "days_to_new_tumor_event_after_initial_treatment" )

    numP = len(allClinDict[nteKey])

    for ii in range(numP):
        if ( allClinDict[nteKey][ii] == "YES" ):

            siteStr = allClinDict[siteKey][ii]

            if ( 1 ):
                if ( siteStr == "Other_specify" ):
                    siteStr = allClinDict[textKey][ii]
                elif ( siteStr == "NA" ):
                    siteStr = allClinDict[textKey][ii]

            if ( siteStr != "NA" ): siteStr = siteStr.lower()
            newSite += [ siteStr ]

            if ( 0 ):
                print " "
                print ii
                ## print " site : ", allClinDict[siteKey][ii]
                print " type : ", allClinDict[typeKey][ii]
                ## print " text : ", allClinDict[textKey][ii]
                print " siteStr : ", siteStr
                print " days : ", allClinDict[days2nteKey][ii]

        else:
            newSite += [ "NA" ]

    ## the types of things I'm seeing are:
    ##     type: Distant_Metastasis
    ##          --> then 'site' sometimes gives the location, or else says "Other_specify"
    ##              in which case the 'text' might give the location

    ## also note that the "days_to_nte" ranges from 62 to 2893 (the lowest numbers are 62, 77, 93, 94, 153, 178...)

    keyString = "C:CLIN:nte_site:::::"
    allClinDict[keyString] = newSite
    ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict[keyString] )
    print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount
    print labelList

    return ( allClinDict )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def checkTumorStatus ( allClinDict ):

    print " in checkTumorStatus ... "
    print " "

    newStatus1 = []
    newStatus2 = []

    statusKey = findKey ( allClinDict, "person_neoplasm_cancer_status" )
    days2fupKey = findKey ( allClinDict, "days_to_last_followup" )
    vitalKey = findKey ( allClinDict, "vital_status" )
    days2deathKey = findKey ( allClinDict, "days_to_death" )

    numP = len(allClinDict[statusKey])

    for ii in range(numP):

        days2last = -1
        if ( allClinDict[days2fupKey][ii] != "NA" ):
            days2last = allClinDict[days2fupKey][ii]
        if ( allClinDict[days2deathKey][ii] != "NA" ):
            days2last = max ( allClinDict[days2deathKey][ii], days2last )

        if ( 0 ):
            print " "
            print " "
            print ii
            print " status     : ", allClinDict[statusKey][ii]
            print " vital      : ", allClinDict[vitalKey][ii]
            ## print " days2fup   : ", allClinDict[days2fupKey][ii]
            ## print " days2death : ", allClinDict[days2deathKey][ii]
            print " days2last  : ", days2last
            if ( allClinDict[vitalKey][ii] == "Alive" ):
                if ( days2last < 90 ):
                    print "         Alive and less than 90 days ", allClinDict[statusKey][ii]

        newStatus1 += [ "NA" ]
        if ( allClinDict[statusKey][ii] == "TUMOR_FREE" and days2last >= 90 ):
            newStatus1[-1] = "TUMOR_FREE"
        elif ( allClinDict[statusKey][ii] == "WITH_TUMOR" and days2last >= 90 ):
            newStatus1[-1] = "WITH_TUMOR"

        newStatus2 += [ "NA" ]
        if ( allClinDict[statusKey][ii] == "TUMOR_FREE" and allClinDict[vitalKey][ii] == "Alive" ):
            newStatus2[-1] = "Alive_woTumor"
        elif ( allClinDict[statusKey][ii] == "WITH_TUMOR" and allClinDict[vitalKey][ii] == "Dead" ):
            newStatus2[-1] = "Dead_wTumor"

    ## as of 13aug ... there are 57 patients who are alive and have less than 90 days of follow-up
    ## of these:        24 are "tumor_free"
    ##                  17 are "NA"
    ##                  16 are "with_tumor"

    keyString = "C:CLIN:tumorStatus1:::::"
    allClinDict[keyString] = newStatus1
    ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict[keyString] )
    print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount
    print labelList

    keyString = "C:CLIN:tumorStatus2:::::"
    allClinDict[keyString] = newStatus2
    ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict[keyString] )
    print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount
    print labelList

    return ( allClinDict )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def checkHistologicGrade ( allClinDict ):

    print " in checkHistologicGrade ... "
    print " "

    gradeKey = findKey ( allClinDict, "neoplasm_histologic_grade" )

    numP = len(allClinDict[gradeKey])

    for ii in range(numP):

        if ( allClinDict[gradeKey][ii] == "G4" ):
            print " changing to G3 ... ", ii, gradeKey, allClinDict[gradeKey][ii]
            allClinDict[gradeKey][ii] = "G3"

    return ( allClinDict )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def checkClinicalStage ( allClinDict ):

    print " in checkClinicalStage ... "
    print " "

    newStage = []

    stageKey = findKey ( allClinDict, "clinical_stage" )
    TstageKey = findKey ( allClinDict, "pathologic_T" )
    barcodeKey = findKey ( allClinDict, "bcr_patient_barcode" )

    numP = len(allClinDict[stageKey])

    for ii in range(numP):

        if ( allClinDict[TstageKey][ii].startswith("T1a") ):
            allClinDict[TstageKey][ii] = "T1b1"

        curStage = allClinDict[stageKey][ii]
        if ( curStage.startswith("IV") ):
            newStage += [ "III,IV" ]
        elif ( curStage.startswith("III") ):
            newStage += [ "III,IV" ]
        elif ( curStage.startswith("II") ):
            newStage += [ "II" ]
        elif ( curStage.startswith("I") ):
            newStage += [ "I" ]
        else:
            newStage += [ "NA" ]

        if ( 0 ):
            print " "
            print " "
            print ii, allClinDict[barcodeKey][ii], allClinDict[stageKey][ii], allClinDict[TstageKey][ii]

    ## as of 22sep ... there is stage info for 240 patients, and the counts
    ## look like this:
    ##          70  IB1
    ##          35  IB
    ##          34  IB2
    ##          33  IIIB
    ##          26  IIB
    ##           7  IIA2
    ##           7  IIA
    ##           5  IVB
    ##          etc
    ## after grouping, we get 147 stage I (61%), 49 stage II (20%), and 44 stage III,IV (18%)

    keyString = "C:CLIN:clinStage:::::"
    allClinDict[keyString] = newStage
    ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict[keyString] )
    print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount
    print labelList

    return ( allClinDict )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this started out as a function to deal with lymph-node features but then
# was augmented to handle hysterectomy- and diagnosis-related features ...

def checkLymphNodes_HystDx ( allClinDict ):

    print " in checkLymphNodes_HystDx ... "
    print " "

    newHyst = []
    newDxM = []
    numLNpos = []
    tfLNpos = []

    ## here we have 138 'radical', 6 'simple', and 5 'other'
    hysTypeKey = findKey ( allClinDict, "hysterectomy_performed_type" )
    hysTextKey = findKey ( allClinDict, "hysterectomy_performed_text" )
    dxMeth1Key = findKey ( allClinDict, "initial_pathologic_diagnosis_method" )
    dxMeth2Key = findKey ( allClinDict, "init_pathology_dx_method_other" )

    barKey = findKey ( allClinDict, "bcr_patient_barcode" )
    LNEcountKey = findKey ( allClinDict, "lymph_node_examined_count" )
    LNEposHEkey = findKey ( allClinDict, "number_of_lymphnodes_positive_by_he" )
    LNEposIHCkey = findKey ( allClinDict, "number_of_lymphnodes_positive_by_ihc" )

    numP = len(allClinDict[hysTypeKey])

    for ii in range(numP):

        if ( 0 ):
            print " "
            print " "
            print " patient index ", ii, allClinDict[barKey][ii]

        if ( allClinDict[hysTypeKey][ii] == "NA" and allClinDict[hysTextKey][ii] == "NA" ):
            newHyst += [ "NO_or_NA" ]
        else:
            newHyst += [ "YES" ]

        ## here we want to figure out what method was used for diagnosis ...
        newDxM += [ "NA" ]
        dxMethod = "NA"

        if ( allClinDict[hysTypeKey][ii].lower().find("hysterect") >= 0 ):
            if ( allClinDict[hysTypeKey][ii].lower().find("radical") >= 0 ):
                dxMethod = "radical_hysterectomy"
            elif ( allClinDict[hysTypeKey][ii].lower().find("simple") >= 0 ):
                dxMethod = "simple_hysterectomy"
            elif ( allClinDict[hysTypeKey][ii].lower().find("total_abd") >= 0 ):
                dxMethod = "total_abdominal_hysterectomy"
        if ( allClinDict[hysTextKey][ii].lower().find("hysterect") >= 0 ):
            if ( allClinDict[hysTextKey][ii].lower().find("radical") >= 0 ):
                dxMethod = "radical_hysterectomy"
            elif ( allClinDict[hysTextKey][ii].lower().find("simple") >= 0 ):
                dxMethod = "simple_hysterectomy"
            elif ( allClinDict[hysTextKey][ii].lower().find("total_abd") >= 0 ):
                dxMethod = "total_abdominal_hysterectomy"

        if ( dxMethod == "NA" ):
            if ( allClinDict[dxMeth1Key][ii].lower().find("cone") >= 0 ):
                dxMethod = "cone_biopsy"
        if ( dxMethod == "NA" ):
            if ( allClinDict[dxMeth2Key][ii].lower().find("cone") >= 0 ):
                dxMethod = "cone_biopsy"

        if ( dxMethod == "NA" ):
            if ( allClinDict[dxMeth1Key][ii].lower().find("biops") >= 0 ):
                dxMethod = "biopsy"
        if ( dxMethod == "NA" ):
            if ( allClinDict[dxMeth2Key][ii].lower().find("biops") >= 0 ):
                dxMethod = "biopsy"

        if ( dxMethod == "NA" ):
            if ( allClinDict[hysTypeKey][ii] != "NA" ): dxMethod = "other"
            if ( allClinDict[hysTextKey][ii] != "NA" ): dxMethod = "other"
            if ( allClinDict[dxMeth1Key][ii] != "NA" ): dxMethod = "other"
            if ( allClinDict[dxMeth2Key][ii] != "NA" ): dxMethod = "other"
            if ( dxMethod == "other" ): print " setting dxMethod to OTHER ", ii, \
                        allClinDict[hysTypeKey][ii], allClinDict[hysTextKey][ii], \
                        allClinDict[dxMeth1Key][ii], allClinDict[dxMeth2Key][ii]
        
        newDxM[-1] = dxMethod


        numPos = 0
        if ( allClinDict[LNEposHEkey][ii] != "NA" ):
            numPos += allClinDict[LNEposHEkey][ii]
        if ( allClinDict[LNEposIHCkey][ii] != "NA" ):
            numPos += allClinDict[LNEposIHCkey][ii]

        if ( (allClinDict[LNEposHEkey][ii] == "NA") and (allClinDict[LNEposIHCkey][ii] == "NA") ):
            numLNpos += [ "NA" ]
            tfLNpos  += [ "NA" ]
        else:
            numLNpos += [ numPos ]
            if ( numPos == 0 ):
                tfLNpos += [ "FALSE" ]
            else:
                tfLNpos += [ "TRUE" ]

        if ( 0 ):
            if ( allClinDict[hysTypeKey][ii] == "NA" ):
                if ( allClinDict[hysTextKey][ii] != "NA" ):
                    print " text filled out but not type "
            if ( allClinDict[hysTextKey][ii] == "NA" ):
                if ( allClinDict[hysTypeKey][ii] != "NA" ):
                    print " type filled out but not text "
    
            print " hysTypeKey  : ", allClinDict[hysTypeKey][ii]
            print " hysTextKey  : ", allClinDict[hysTextKey][ii]
            print " lymph nodes : ", allClinDict[LNEcountKey][ii], \
                                     allClinDict[LNEposHEkey][ii], \
                                     allClinDict[LNEposIHCkey][ii]

    print " done working through each patient ... "
    print len(newHyst), len(newDxM), len(tfLNpos), len(numLNpos)
    print " "

    keyString = "C:CLIN:hysterectomy:::::"
    allClinDict[keyString] = newHyst
    print " (a) ", keyString, newHyst
    ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict[keyString] )
    print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount
    print labelList

    keyString = "C:CLIN:dx_method:::::"
    allClinDict[keyString] = newDxM
    print " (b) ", keyString, newDxM
    ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict[keyString] )
    print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount
    print labelList

    keyString = "C:CLIN:LNposTF:::::"
    allClinDict[keyString] = tfLNpos
    print " (c) ", keyString, tfLNpos
    ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict[keyString] )
    print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount
    print labelList

    keyString = "N:CLIN:numLNpos:::::"
    allClinDict[keyString] = numLNpos
    print " (3) ", keyString, numLNpos
    ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict[keyString] )
    print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount

    print " DONE DONE DONE "

    return ( allClinDict )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def makeMergedDx ( allClinDict ):

    print " in makeMergedDx ... "
    print " "

    mergeDx = []
    epcReview = []

    histTypeKey = findKey ( allClinDict, "histological_type" )
    epcDxKey = findKey ( allClinDict, "C:CLIN:Dx_EPC" )

    barKey = findKey ( allClinDict, "bcr_patient_barcode" )

    numP = len(allClinDict[histTypeKey])

    for ii in range(numP):

        if ( 1 ):
            print " "
            print " "
            print " patient index ", ii, allClinDict[barKey][ii], allClinDict[histTypeKey][ii], allClinDict[epcDxKey][ii]

        ## expected possible values for the histological_type field:
        ##      206 Cervical_Squamous_Cell_Carcinoma
        ##       23 Endocervical_Type_of_Adenocarcinoma
        ##        6 Mucinous_Adenocarcinoma_of_Endocervical_Type
        ##        5 Adenosquamous
        ##        4 Endometrioid_Adenocarcinoma_of_Endocervix
        ##        4 Endocervical_Adenocarcinoma_of_the_Usual_Type
        ##       70 NA

        ## expected values for Dx_EPC field:
        ##      4 Adenosquamous
        ##     27 Endocervical_Adeno
        ##    123 NA
        ##     99 Squamous

        if ( allClinDict[epcDxKey][ii] != "NA" ): 
            epcReview += [ "TRUE" ]
        else:
            epcReview += [ "FALSE" ]

        if ( allClinDict[epcDxKey][ii] != "NA" ):
            mergeDx += [ allClinDict[epcDxKey][ii] ]
        else:
            if ( allClinDict[histTypeKey][ii] == "Cervical_Squamous_Cell_Carcinoma" ):
                mergeDx += [ "Squamous" ]
            elif ( allClinDict[histTypeKey][ii] == "Endocervical_Type_of_Adenocarcinoma" ):
                mergeDx += [ "Adenocarcinoma" ]
            elif ( allClinDict[histTypeKey][ii] == "Mucinous_Adenocarcinoma_of_Endocervical_Type" ):
                mergeDx += [ "Adenocarcinoma" ]
            elif ( allClinDict[histTypeKey][ii] == "Adenosquamous" ):
                mergeDx += [ "Adenosquamous" ]
            elif ( allClinDict[histTypeKey][ii] == "Endometrioid_Adenocarcinoma_of_Endocervix" ):
                mergeDx += [ "Adenocarcinoma" ]
            elif ( allClinDict[histTypeKey][ii] == "Endocervical_Adenocarcinoma_of_the_Usual_Type" ):
                mergeDx += [ "Adenocarcinoma" ]
            elif ( allClinDict[histTypeKey][ii] == "NA" ):
                mergeDx += [ "NA" ]
            else:
                print " ERROR ??? we should not be here ... ", ii, allClinDict[barKey][ii], \
                    allClinDict[histTypeKey][ii], allClinDict[epcDxKey][ii]

        ## just double-checking terminology one more time ...
        if ( mergeDx[-1] == "Endocervical_Adeno" ):
            mergeDx[-1] = "Adenocarcinoma"
            
    keyString = "C:CLIN:Dx_merged:::::"
    allClinDict[keyString] = mergeDx
    ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict[keyString] )
    print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount
    print labelList

    keyString = "C:CLIN:EPC_review:::::"
    allClinDict[keyString] = epcReview
    ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict[keyString] )
    print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount
    print labelList

    return ( allClinDict )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if ( (len(sys.argv)==3) or (len(sys.argv)==4) ):
            tumorString = sys.argv[1]
            dateString = sys.argv[2]
            featureList = sys.argv[3]
        else:
            print " "
            print " Usage: %s <tumor-type> <run-id> <feature-list> "
            print " "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

    print " "
    print " Running : %s %s %s %s " % (sys.argv[0], sys.argv[1], sys.argv[2], sys.argv[3])
    print " "
    print " "

    listDict = {}

    # read in the current clinical file ...
    topDir = "%s/%s/%s" % (gidgetConfigVars['TCGAFMP_DATA_DIR'], tumorString, dateString)
    clin1name = topDir + "/" + "%s.clinical.%s.tsv" % ( tumorString, dateString )
    print clin1name
    allClinDict = tsvIO.readTSV ( clin1name )

    # find out which features are interesting ...

    # BUT IS THIS REALLY COMPLETELY NOT NECESSARY ??? 
    # was this just for debugging purposes ???
    fList = getFeatList ( featureList )

    for aF in fList:
        print aF

        for aKey in allClinDict.keys():

            if ( aKey[1] == ":" ):
                aTokens = aKey.split(':')
                tKey = aTokens[2]
            else:
                tKey = aKey

            if ( aF == tKey ):
                ( keyType, nCount, naCount, cardCount, labelList, labelCount ) = miscClin.lookAtKey ( allClinDict[aKey] )
                print " %s  N=%d  NA=%d  not-NA=%d  card=%d " % ( keyType, nCount, naCount, (nCount-naCount), cardCount ), labelCount
                if ( keyType != "NUMERIC" ): print labelList
                print " "
                print " "


    # now we need to do some massaging and computing ...
    try:
        allClinDict = addBMI ( allClinDict )
    except:
        print " addBMI function failed "

    try:
        allClinDict = checkMenopause ( allClinDict )
    except:
        print " checkMenopause function failed "

    try:
        allClinDict = addAgeSplits ( allClinDict )
    except:
        print " addAgeSplits function failed "

    try:
        allClinDict = checkCancerStatus ( allClinDict )
    except:
        print " checkCancerStatus function failed "

    try:
        allClinDict = checkTumorStatus ( allClinDict )
    except:
        print " checkTumorStatus function failed "

    try:
        allClinDict = checkHistologicGrade ( allClinDict )
    except:
        print " checkHistologicGrade function failed "

    try:
        allClinDict = checkClinicalStage ( allClinDict )
    except:
        print " checkClinicalStage function failed "

    try:
        allClinDict = checkLymphNodes_HystDx ( allClinDict )
    except:
        print " checkLymphNodes_HystDx function failed "

    try:
        allClinDict = makeMergedDx ( allClinDict )
    except:
        print " makeMergedDx function failed "


    print " FINISHED creating and modifying CESC features ... "

    # now we're ready to re-write this ...
    (naCounts, otherCounts) = miscClin.lookAtClinDict(allClinDict)
    print "     --> getting bestKeyOrder ... "
    bestKeyOrder = miscClin.getBestKeyOrder(allClinDict, naCounts)

    outName = topDir + "/" + "%s.clinical.%s.cesc.tsv" % ( tumorString, dateString )
    print " --> writing output to ", outName
    tsvIO.writeTSV_clinical ( allClinDict, bestKeyOrder, outName )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
