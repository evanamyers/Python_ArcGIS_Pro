"""
This code is used in the AsBuilt Polygon tool for ArcGIS Pro.  It automates the creation of the polygons around selected
Points and Lines.  It also completes the Source and AsBuilt Date fields with values the user provides.
"""



def checkFeatureSelection(lyrList):
    print("Checking Production layers.")
    # arcpy.AddMessage("Checking Production layers.")

    prodLayers = []

    for maplayer in lyrList:
        if maplayer.isFeatureLayer:
            descmap = arcpy.Describe(maplayer)
            descCatPath = descmap.catalogPath
            fcFields = [f.name for f in arcpy.ListFields(maplayer.longName)]
            if "wGISProd" in descCatPath:
                if 'WUD.SewerStormwater' or 'WUD.WaterDistribution' in descCatPath:
                    if 'SOURCE' in fcFields:
                        if maplayer.name not in prodLayers:
                            prodLayers.append(maplayer.longName)

    # Check if proper layers are selected
    result = ()
    for fclayer in prodLayers:
        desclayer = arcpy.Describe(fclayer)
        FID = desclayer.FIDSet
        if FID == '':
            result = False
            continue
        else:
            result = True
            break

    if not result:
        arcpy.AddMessage("A selection is required for this tool to run")
        print('no selection')
        sys.exit()

    else:
        print("Production layers selected.")
        # arcpy.AddMessage("Production layers selected.")

    del lyrList

    return prodLayers

def createBuffers(asbuiltSource, asbuiltDate, asbuiltWUDNUM, buffersize, prodLayers):

    print("Creating temp gdb.")
    # arcpy.AddMessage("Creating temp gdb.")
    fileGDB = arcpy.management.CreateFileGDB(tempDir, 'asbuiltPolygonToolWS')


    print("Checking if asBuiltBuffer layer exists.  If it does, clear the table.")
    # arcpy.AddMessage("Checking if asBuiltBuffer layer exists.  If it does, clear the table.")
    asBuiltBuffers = arcpy.CreateFeatureclass_management(fileGDB, "asBuiltBuffers", 'POLYGON',
                                                         r'Database '
                                                         r'Connections\wGISProd@GISdb.OSA.sde\wGISProd.WUD.Asbuilt_Support_Data\wGISProd.WUD.Asbuilt_Polygons',
                                                         'SAME_AS_TEMPLATE', 'SAME_AS_TEMPLATE', '2236')

    print("Populating SOURCE and ASBUILTDATE fields for selected features.")
    arcpy.AddMessage("Populating SOURCE and ASBUILTDATE fields for selected features.")
    # Fill out SOURCE and ASBUILTDATE fields for the selected features (this step is not for the as-built polygons, thats later)
    for eachlayer in prodLayers:
        desc = arcpy.Describe(eachlayer)
        FID = desc.FIDSet
        if FID:
            with cursorsPro.UpdateCursor(eachlayer, ['SOURCE', 'ASBUILTDATE']) as cursor:
                for row in cursor:
                    row[0] = r"{}".format(asbuiltSource)
                    row[1] = asbuiltDate
                    cursor.updateRow(row)

    workGDB = fileGDB.getOutput(0)
    arcpy.env.workspace = workGDB

    print("Creating Buffers for the selected features:")
    arcpy.AddMessage("Creating Buffers for the selected features:")
    bufferSource = arcpy.Describe(asBuiltBuffers).catalogPath
    arcpy.AddMessage(bufferSource)
    for each in prodLayers:
        desc = arcpy.Describe(each)
        try:
            FID = desc.FIDSet
        except():
            continue
        if FID:
            arcpy.AddMessage(desc.shapeType)
            if desc.shapeType == 'Polyline':
                print("Making buffer for: {}".format(desc.name))
                arcpy.AddMessage("Making buffer for: {}".format(desc.name))
                fields = [f.name for f in arcpy.ListFields(each)]
                if "WATERTYPE" in fields:
                    lineBuffer = arcpy.analysis.Buffer(each, "lineBuffer", buffersize, "FULL", "ROUND", "LIST",
                                                       "SOURCE;WATERTYPE", "PLANAR")

                    field_map = {"WATER": "Potable", "SEWER": "Sewage", "RECLAIMED": "Reclaimed", "RAW": "Raw",
                                 "OTHER": "Treated"}
                    fields = ["WATER", "SEWER", "RECLAIMED", "RAW", "OTHER", "SHAPE@"]
                    insert_cursor = arcpy.da.InsertCursor(asBuiltBuffers, fields)

                    with arcpy.da.SearchCursor(lineBuffer, ["WATERTYPE", "SHAPE@"]) as search_cursor:
                        for row in search_cursor:
                            # Create a dictionary for the current polygon
                            polygon_dict = {"WATERTYPE": row[0], "SHAPE@": row[1]}

                            # Update the dictionary with the new field names and values
                            updated_dict = {}
                            for output_field, input_value in field_map.items():
                                updated_dict[output_field] = "Yes" if polygon_dict["WATERTYPE"] == input_value else "No"

                            insert_cursor.insertRow(tuple(
                                updated_dict[field] if field != "SHAPE@" else polygon_dict[field] for field in fields))
                    del insert_cursor

            if desc.shapeType == 'Point':
                print("Making buffer for: {}".format(desc.name))
                arcpy.AddMessage("Making buffer for: {}".format(desc.name))
                fields = [f.name for f in arcpy.ListFields(each)]
                if "WATERTYPE" in fields:
                    pointBuffer = arcpy.analysis.Buffer(each, "pointBuffer", "20 Feet", "FULL", "ROUND", "LIST",
                                                        "SOURCE;WATERTYPE", "PLANAR")

                    field_map = {"WATER": "Potable", "SEWER": "Sewage", "RECLAIMED": "Reclaimed", "RAW": "Raw",
                                 "OTHER": "Treated"}
                    fields = ["WATER", "SEWER", "RECLAIMED", "RAW", "OTHER", "SHAPE@"]
                    insert_cursor = arcpy.da.InsertCursor(asBuiltBuffers, fields)

                    with arcpy.da.SearchCursor(pointBuffer, ["WATERTYPE", "SHAPE@"]) as search_cursor:
                        for row in search_cursor:
                            # Create a dictionary for the current polygon
                            polygon_dict = {"WATERTYPE": row[0], "SHAPE@": row[1]}

                            # Update the dictionary with the new field names and values
                            updated_dict = {}
                            for output_field, input_value in field_map.items():
                                updated_dict[output_field] = "Yes" if polygon_dict["WATERTYPE"] == input_value else "No"

                            insert_cursor.insertRow(tuple(
                                updated_dict[field] if field != "SHAPE@" else polygon_dict[field] for field in fields))
                    del insert_cursor

                if '.ssNetworkStructure' in desc.name:
                    pass
                    # ssNetStruc = 'True'
                    # pointBuffer = arcpy.analysis.Buffer(each, "pointBuffer", "20 Feet", "FULL", "ROUND", "LIST",
                    #                                     "SOURCE", "PLANAR")
            else:
                pass
        else:
            print('{} not selected, no polygon made'.format(each))


    print("Populating other required fields for buffer.")
    arcpy.AddMessage("Populating other required fields for buffer.")
    with cursorsPro.UpdateCursor(bufferSource, ["HYPERLINK", "PBCWUDFILE", "P56FOLDER", "ASBUILTNO", "ASBUILTDATE", "WUDPROJECTNUM", "LifeCycleStatusRemoved"]) as cursor:
        for row in cursor:
            try:
                row[0] = asbuiltSource
            except():
                continue
            if row[0]:
                # pbcwudfile = row[0].split("\\")[-1]
                #if
                p56 = row[0].split("\\")[2]
                asbuiltno = row[0].split("\\")[-1][0:4]
                row[1] = os.path.basename(row[0])
                row[2] = p56
                row[3] = asbuiltno
                row[4] = asbuiltDate
                row[5] = asbuiltWUDNUM
                row[6] = 'No'
            cursor.updateRow(row)

    # Go through all the polygons, if their hyperlink is the same, update their 'watertype' fields to share 'Yes' values
    with arcpy.da.SearchCursor(bufferSource, ['HYPERLINK', 'SHAPE@', 'WATER', 'SEWER', 'RECLAIMED', 'RAW', 'OTHER']) as bufferList:
        for buffer in bufferList:
            keyBuffer = buffer[0]
            if buffer[2] == 'Yes' and buffer[3] == 'Yes':
                pass
            else:
                if "'" in keyBuffer:
                    sqlQuery1 = """HYPERLINK = '{}'""".format(keyBuffer.replace("'", "''"))
                else:
                    sqlQuery1 = """HYPERLINK = '{}'""".format(keyBuffer)
                print("Populating buffer {}".format(keyBuffer))
                sel_values = []
                try:
                    with arcpy.da.SearchCursor(bufferSource, ['OBJECTID', 'HYPERLINK', 'WATER', 'SEWER', 'RECLAIMED', 'RAW', 'OTHER'], sqlQuery1) as cursor:
                        for row in cursor:
                            if row not in sel_values:
                                sel_values.append(row)

                            checkListWater = []
                            checkListSewer = []
                            checkListReclaimed = []
                            checkListRaw = []
                            checkListOther = []
                            for each in sel_values:
                                if each[2] == 'Yes':
                                    checkListWater.append('Yes')
                                if each[3] == 'Yes':
                                    checkListSewer.append('Yes')
                                if each[4] == 'Yes':
                                    checkListReclaimed.append('Yes')
                                if each[5] == 'Yes':
                                    checkListRaw.append('Yes')
                                if each[6] == 'Yes':
                                    checkListOther.append('Yes')
                            # print(checkListWater, checkListSewer)
                    with cursorsPro.UpdateCursor(bufferSource, ['WATER', 'SEWER', 'RECLAIMED', 'RAW', 'OTHER'], sqlQuery1) as cursor1:
                        for each1 in cursor1:
                            if checkListWater:
                                each1[0] = 'Yes'
                                cursor1.updateRow(each1)
                            if checkListSewer:
                                each1[1] = 'Yes'
                                cursor1.updateRow(each1)
                            if checkListReclaimed:
                                each1[2] = 'Yes'
                                cursor1.updateRow(each1)
                            if checkListRaw:
                                each1[3] = 'Yes'
                                cursor1.updateRow(each1)
                            if checkListOther:
                                each1[4] = 'Yes'
                                cursor1.updateRow(each1)

                except():
                    pass

    print ("Dissolving Buffers")
    arcpy.AddMessage("Dissolving Buffers")
    dissolvedBufferPath = workGDB + "\\asBuiltBuffer_dissolved"

    dissolvedBuffer = arcpy.management.Dissolve("asBuiltBuffers", dissolvedBufferPath,
                              "PBCWUDFILE;HYPERLINK;P56FOLDER;ASBUILTNO;ASBUILTDATE;WUDPROJECTNUM;WATER;SEWER;RECLAIMED;RAW;OTHER;LifeCycleStatusRemoved",
                              None, "MULTI_PART", "DISSOLVE_LINES", '')


    return dissolvedBuffer, asBuiltBuffers

def addNewPolygons(dissolvedBuffer, abPoly, asBuiltBuffers):

    print ("Appending Buffers to Production")
    arcpy.AddMessage("Appending Buffers to Production")

    arcpy.management.Append(dissolvedBuffer, abPoly, "NO_TEST")

    bufferSource = arcpy.Describe(asBuiltBuffers).catalogPath
    with cursorsPro.UpdateCursor(bufferSource, "*") as cursor:
        for row in cursor:
            cursor.deleteRow()

    del bufferSource
    del dissolvedBuffer


if __name__ == '__main__':

    import arcpy, tempfile, sys, os, shutil

    try:
        cursorForPro = "W:\\GIS\\Tools\\Codes_for_Tools_ArcGIS_Pro\\cursorsPro.py"
        libFolder = os.path.dirname(os.path.abspath(os.__file__))
        # if "cursorsPro.py" not in libFolder:
        import shutil

        shutil.copy(cursorForPro, libFolder)
    except():
        arcpy.AddMessage("Could not copy cursorsPro.py to proper folder.")
        sys.exit(0)
    finally:
        import cursorsPro

    arcpy.SetLogMetadata(False)
    arcpy.SetLogHistory(False)
    #sys.tracebacklimit = 0

    asbuiltSourceRaw = r"{}".format(arcpy.GetParameterAsText(0))
    asbuiltDateRaw = arcpy.GetParameterAsText(1)
    asbuiltWUDNUM = arcpy.GetParameterAsText(2)
    buffersize = arcpy.GetParameterAsText(3) + " Feet"

    splitSource = asbuiltSourceRaw.split('originals')
    asbuiltDate = asbuiltDateRaw.split(' ')[0]

    asbuiltSource = r"{}".format(asbuiltSourceRaw.replace(splitSource[0], '..\\'))
    arcpy.AddMessage(asbuiltSource)

    # List layers in currently opened map in project
    aprx = arcpy.mp.ArcGISProject('current')
    currentMap = aprx.activeMap
    lyrList = currentMap.listLayers()

    abPoly = ()

    for eachLyr in lyrList:
        if "Asbuilt" and "Polygon" in eachLyr.name:
            if eachLyr.isFeatureLayer:
                descLyr = arcpy.Describe(eachLyr)
                fcDB = descLyr.catalogPath
                if "wGISProd" in fcDB:
                    keyFC = eachLyr.longName
                    if "wGISProd.WUD.Asbuilt_Polygons" in keyFC:
                        abPoly = keyFC
                        break

    if abPoly:
        # arcpy.AddMessage("Found As-Built Polygon layer")
        print("Found As-Built Polygon layer")

    else:
        raise ValueError("An Asbuilt Polygon layer is not in the current map.  "
                         "Make sure the layer is sourced Production Database.  "
                         "Remember to change it to a version if needed.")


    arcpy.env.overwriteOutput = True
    arcpy.env.addOutputsToMap = 0


    with tempfile.TemporaryDirectory() as tempDir:
        tempDir = tempfile.mkdtemp()
        arcpy.AddMessage(tempDir)
        try:
            prodLayers = checkFeatureSelection(lyrList)
            dissolvedBuffer, asbuiltBuffers = createBuffers(asbuiltSource, asbuiltDate, asbuiltWUDNUM, buffersize, prodLayers)
            addNewPolygons(dissolvedBuffer, abPoly, asbuiltBuffers)
        finally:
            del prodLayers
            del lyrList

    # shutil.rmtree(tempDir)

    # except Exception as e:
    #     logger.error(str(e))

