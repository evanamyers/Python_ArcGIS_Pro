import arcpy, os, re

featureClass = arcpy.GetParameterAsText(0)
removeTypicalFields = arcpy.GetParameterAsText(1)
keepFields = arcpy.GetParameterAsText(2)
outFolder = arcpy.GetParameterAsText(3)
outDatabase = arcpy.GetParameterAsText(4)

arcpy.env.overwriteOutput = 'True'


try:
    # Create a new Geodatabase in specified folder if it doesn't exist
    newDB = os.path.join(outFolder, (outDatabase + '.gdb'))
    if not arcpy.Exists(newDB):
        newDB = arcpy.CreateFileGDB_management(outFolder, outDatabase, "CURRENT")

    if ";" in featureClass:
        listFC = featureClass.split(";")
    else:
        listFC = [featureClass]

    arcpy.AddMessage(listFC)

    # Format name of Feature for export
    for each in listFC:
        newName = re.sub("[\'.]", "_", each)
        newName = newName.rsplit('_')
        print(newName[-1])
        arcpy.FeatureClassToFeatureClass_conversion(each, newDB, newName[-1])
    # for each in listFC:
    #     if "'" in each:
    #         eachStrp = each.strip("'")
    #         if '.' in eachStrp:
    #             newName = eachStrp.rsplit('.').replace(" ","_")
    #             arcpy.AddMessage(newName)
    #             arcpy.FeatureClassToFeatureClass_conversion(eachStrp, newDB, newName[-1])
    #         else:
    #             arcpy.AddMessage(eachStrp)
    #             arcpy.FeatureClassToFeatureClass_conversion(eachStrp, newDB, eachStrp)
    #     else:
    #         if '.' in each:
    #             newName = each.rsplit('.').replace(" ","_")
    #             arcpy.AddMessage(newName)
    #             arcpy.FeatureClassToFeatureClass_conversion(each, newDB, newName[-1])
    #         else:
    #             arcpy.AddMessage(each)
    #             arcpy.FeatureClassToFeatureClass_conversion(each, newDB, each)


    if str(removeTypicalFields) == 'true':  # because the checkbox is being translated to a 'GetParameterAsText', its now a string 'true'
        keepFieldsList = ['FACILITYID', 'Shape', 'OBJECTID', 'GlobalID', 'Shape_Length', 'MXLOCATION', 'LOCDESC', 'DIAMETER', 'MATERIAL', 'VALVETYPE', 'OWNEDBY', 'MAINTBY', 'LIFECYCLESTATUS', 'WATERTYPE', 'STRUCTTYPE', 'METERTYPE', 'LS_ID', 'WW_NUM', 'BYPASSVALVE', 'OPERABLE', 'CURROPEN', 'FITTINGTYPE', 'LINED', 'MH_Num', 'LINEDDATE', 'LS', 'CAPLOCK', 'HYDRFLAG', 'MAINSHAPE', 'LINEDYEAR', 'LINERTYPE', 'FROMMH', 'TOMH', 'MATERIAL_2ND', 'LINETYPE', 'CROSSING', 'LS_No', 'GPSSTATUS']

        fieldsToBeRemoved = []
        for each in listFC:
            fcFields = [f.name for f in arcpy.ListFields(each)]
            for field in fcFields:
                if field not in keepFieldsList and field not in fieldsToBeRemoved:
                    fieldsToBeRemoved.append(field)

    else:
        allFields = []
        for each in listFC:
            eachStrp = each.strip("'")
            fcFields = [f.name for f in arcpy.ListFields(each)]
            for fields in fcFields:
                if fields not in allFields:
                    if fields not in ['Shape', 'OBJECTID', 'GlobalID', 'Shape_Length']:
                        allFields.append(fields.upper())

        if ";" in keepFields:
            keepFieldsList = keepFields.split(";")
        else:
            keepFieldsList = [keepFields]

        fieldsToBeRemoved = []
        for each in allFields:
            if each not in keepFields:
                fieldsToBeRemoved.append(each)

    newDBPath = outFolder + "\\" + outDatabase + ".gdb"
    arcpy.env.workspace = newDBPath
    newFCList = arcpy.ListFeatureClasses()

    for each in arcpy.ListFeatureClasses():
        newFP = os.path.join(arcpy.env.workspace, each)
        arcpy.DeleteField_management(newFP, fieldsToBeRemoved)


    xlsxPath = outFolder + "\\" + outDatabase + ".xlsx"
    FeatureListPaths = [newDBPath + "\\" + each for each in newFCList]
    FeatureListText = str(tuple(FeatureListPaths)).rstrip(',)').replace(', ', ';') + ')'
    print(FeatureListText)
    arcpy.AddMessage(FeatureListText)
    arcpy.AddMessage(xlsxPath)
    arcpy.conversion.TableToExcel(FeatureListText, str(xlsxPath), "ALIAS", "DESCRIPTION")

except():
    pass


