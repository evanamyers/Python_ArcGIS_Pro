"""

For each def (function), the referenced workspace is the Database that contains the feature being updated.  For example,
the SITUS points that will be updated are in the wGISProd@GISdb.WUD.sde.


---Data from GISProd that is used:---
wGISProd.WUD.PBCWUD_ZONES
wGISProd.WUD.PARCELS
wGISProd.WUD.CENTERLINE_LN
wGISProd.WUD.WATER_PY
wGISProd.WUD.MUNICIPALITIES

---Data from PBCGIS that is used:---
PAO.PARCELS
ENG.CENTERLINE
ENG.WATER
PZB.MUNICIPALITIES

---Data from GISProd that is Updated:---
Parcels
Centerline
Waterbodies
Municipalities


"""


def SITUS(workspaceforCodes, PBCGIS_BaseConnection, prodDB_BaseConnection):  # (set the database you want updated in the "__main__" variables found at the bottom of the script)

    # featureSet = prodDB_BaseConnection + "/Address_Points"  # for Testing
    featureSet = prodDB_BaseConnection + "/wGISProd.WUD.Address_Points"  # Feature Set that contains the SITUS points you want updated
    # prodDB_SITUS = featureSet + "/SITUS"  # Testing
    prodDB_SITUS = featureSet + "/wGISProd.WUD.SITUS"
    prodDB_SITUS_copy = workspaceforCodes + "/PROD_SITUS_copy"
    pbcSITUS = str(PBCGIS_BaseConnection / "CWGIS.SITUS")
    reprojectedSource = workspaceforCodes + "/CWSITUS_reproj"
    # PBC_Zones = prodDB_BaseConnection + "/Boundaries/PBCWUD_ZONES"  # for testing
    PBC_Zones = prodDB_BaseConnection + "/wGISProd.WUD.Boundaries/wGISProd.WUD.PBCWUD_ZONES"
    CWSITUS_reproj_Layer = "CWSITUS_reproj_Layer"
    Join_Field = 'SITUS_SEQ'

    # Starting WUD SITUS Update
    print("Creating a reprojected version of the CWSITUS feature class")
    if arcpy.Exists(reprojectedSource):
        arcpy.Delete_management(reprojectedSource)

    arcpy.management.Project(in_dataset=pbcSITUS,
                             out_dataset=reprojectedSource,
                             out_coor_system="102658",
                             transform_method="NAD_1983_To_HARN_Florida",
                             in_coor_system="102258",
                             preserve_shape="NO_PRESERVE_SHAPE", max_deviation="", vertical="NO_VERTICAL")

    print("Creating backup of WUD SITUS")
    # Create a backup of the existing WUD SITUS points just in case
    arcpy.management.CopyFeatures(prodDB_SITUS, prodDB_SITUS_copy)


    # newWUDSource = "WUDSITUS_backup"
    # arcpy.management.CreateFeatureclass(workspaceforCodes,
    #                                     newWUDSource, 'POINT',
    #                                     "W:\\GIS\\WORKING FILES\\EM Working Files\\Databases\\Local WUD Data.gdb\\Address_Points\\SITUS",
    #                                     'DISABLED', 'DISABLED', "102658")

    # Collect all fields from the sourceWUDFC except Geometry field
    # lstFields = [field.name for field in arcpy.ListFields(prodDB_SITUS) if field.type not in ['Geometry', 'GlobalID']]
    # lstFields.append("SHAPE@")  # add the full Geometry object

    # targetCursor = arcpy.da.InsertCursor(prodDB_SITUS_copy, lstFields)
    # # read as: for each row in the sourceFC table, copy it into the targetFC
    # with arcpy.da.SearchCursor(prodDB_SITUS, lstFields) as cursor:
    #     for row in cursor:
    #         targetCursor.insertRow(row)
    # del targetCursor


    # Delete all the reprojected CWSITUS points that are outside our service area
    print("Deleting all Source points outside of Service Zones.")
    # Make Feature Layer for WUDSITUS and reprojected CWSITUS
    WUD_SITUS_Layer = "WUD_SITUS_layer"
    arcpy.MakeFeatureLayer_management(prodDB_SITUS_copy, WUD_SITUS_Layer)
    arcpy.MakeFeatureLayer_management(reprojectedSource, CWSITUS_reproj_Layer)
    # Select SITUS points outside our service area then delete them
    arcpy.SelectLayerByLocation_management(CWSITUS_reproj_Layer, "INTERSECT", PBC_Zones, "", "NEW_SELECTION",
                                           "INVERT")
    with arcpy.da.UpdateCursor(CWSITUS_reproj_Layer, 'OBJECTID') as cursor:
        for row in cursor:
            cursor.deleteRow()
    del cursor
    arcpy.SelectLayerByAttribute_management(CWSITUS_reproj_Layer, "CLEAR_SELECTION")

    print("Adding required fields and attributes to the new SITUS points")
    inTable = reprojectedSource
    inJoinField = outJoinField = Join_Field
    joinTable = prodDB_SITUS_copy
    joinFields = "PRIMARY_;Zone;MAPGRID;MXLOCATION;MXADDRESSCODE"

    arcpy.AddMessage(
        '\nJoining fields from {0} to {1} via the join {2}:{3}'.format(joinTable, inTable, inJoinField, outJoinField))

    # Define generator for join data
    def joindataGen(joinTable, fieldList, sortField):
        with arcpy.da.SearchCursor(joinTable, fieldList, sql_clause=['DISTINCT', 'ORDER BY ' + sortField]) as cursor:
            for row in cursor:
                yield row

    # Function for progress reporting
    def percentile(n, pct):
        return int(float(n) * float(pct) / 100.0)

    # Add join fields
    arcpy.AddMessage('\nAdding join fields...')
    fList = [f for f in arcpy.ListFields(joinTable) if f.name in joinFields.split(';')]
    for i in range(len(fList)):
        name = fList[i].name
        type = fList[i].type
        if type in ['Integer', 'OID']:
            arcpy.AddField_management(inTable, name, field_type='LONG')
        elif type == 'String':
            arcpy.AddField_management(inTable, name, field_type='TEXT', field_length=fList[i].length)
        elif type == 'Double':
            arcpy.AddField_management(inTable, name, field_type='DOUBLE')
        elif type == 'Date':
            arcpy.AddField_management(inTable, name, field_type='DATE')
        elif type == 'SmallInteger':
            arcpy.AddField_management(inTable, name, field_type='SHORT')
        else:
            arcpy.AddError('\nUnknown field type: {0} for field: {1}'.format(type, name))

    # Write values to join fields
    arcpy.AddMessage('\nJoining data...')
    # Create generator for values
    fieldList = [outJoinField] + joinFields.split(';')
    joinDataGen = joindataGen(joinTable, fieldList, outJoinField)
    version = sys.version_info[0]
    if version == 2:
        joinTuple = joinDataGen.next()
    else:
        joinTuple = next(joinDataGen)
    #
    fieldList = [inJoinField] + joinFields.split(';')
    count = int(arcpy.GetCount_management(inTable).getOutput(0))
    breaks = [percentile(count, b) for b in range(10, 100, 10)]
    j = 0
    with arcpy.da.UpdateCursor(inTable, fieldList, sql_clause=(None, 'ORDER BY ' + inJoinField)) as cursor:
        for row in cursor:
            j += 1
            if j in breaks:
                arcpy.AddMessage(str(int(round(j * 100.0 / count))) + ' percent complete...')
            row = list(row)
            key = row[0]
            try:
                while joinTuple[0] < key:
                    if version == 2:
                        joinTuple = joinDataGen.next()
                    else:
                        joinTuple = next(joinDataGen)
                if key == joinTuple[0]:
                    for i in range(len(joinTuple))[1:]:
                        row[i] = joinTuple[i]
                    row = tuple(row)
                    cursor.updateRow(row)
            except StopIteration:
                arcpy.AddWarning('\nEnd of join table.')
                break

    arcpy.SetParameter(5, inTable)
    arcpy.AddMessage('\nDone.')

    print("Updating Primary_ field with up to date values then removing PRIMARY and 'SE_ANNO_CAD_DATA' fields.")
    with arcpy.da.UpdateCursor(reprojectedSource, ["PRIMARY", "PRIMARY_"]) as cursor:
        for row in cursor:
            row[0] = row[1]
            cursor.updateRow(row)
    arcpy.DeleteField_management(reprojectedSource, "PRIMARY")
    arcpy.DeleteField_management(reprojectedSource, "SE_ANNO_CAD_DATA")

    print("Updating Production WUDSITUS points to the new points.")
    # Starting edit session
    edit = arcpy.da.Editor(prodDB_BaseConnection)
    arcpy.env.workspace = featureSet
    if edit.isEditing:
        edit.stopEditing()
    try:
        edit.startEditing(False, True)
        edit.startOperation()
    except():
        print("Could not start an edit session. Try again later or close ArcMap or ArcCatalog.")
        arcpy.AddMessage("Could not start an edit session. Try again later or close ArcMap or ArcCatalog.")

    print("Deleting existing WUD SITUS points")
    # Delete all features in the WUD SITUS feature class.
    try:
        counter = 0
        with arcpy.da.UpdateCursor(prodDB_SITUS, '*') as cursor:
            for row in cursor:
                counter += 1
                cursor.deleteRow()
    except():
        arcpy.ClearWorkspaceCache_management()

    print("Adding reprojectedSource attributes to ProdWUDSITUS")
    inTable = reprojectedSource
    toTable = prodDB_SITUS

    # Collect all fields except the Geometry field
    lstFields = [field.name for field in arcpy.ListFields(inTable) if
                 field.type not in ['Geometry']]  #
    # print(lstFields)
    lstFields.append("SHAPE@")  # add the full Geometry object

    # Similar to previous with fields specified
    targetTable = arcpy.da.InsertCursor(toTable, lstFields)
    with arcpy.da.SearchCursor(inTable, lstFields) as cursor:
        for row in cursor:
            targetTable.insertRow(row)
    del targetTable

    edit.stopOperation()
    if edit.isEditing:
        edit.stopEditing(True)

    print("Done Updating SITUS." + "\n")


def Parcels(workspaceforCodes, prodDB_BaseConnection, prodDB_LandBase):

    print("Updating PARCELS feature class.")

    PBCGIS_Parcels = "https://services1.arcgis.com/ZWOoUZbtaYePLlPw/arcgis/rest/services" \
                     "/Parcels_and_Property_Details_Local_Prj/FeatureServer/0"
    parcelsPBC_copy = workspaceforCodes + "/PARCELS_PBC_copy"
    # parcelsWUD = prodDB_LandBase + "/PARCELS"  # for testing
    parcelsWUD = prodDB_LandBase + "/wGISMaps.WUD.Parcels"  # Feature that needs updating
    parcelsWUD_copy = workspaceforCodes + "/PARCELS_WUD_copy"
    projectedOutput = workspaceforCodes + "/PARCELS_reprojected"
    # PBC_Zones = prodDB_BaseConnection + "/Boundaries/PBCWUD_ZONES"  # for testing
    PBC_Zones = prodDB_BaseConnection + "/wGISMaps.WUD.Boundaries/wGISMaps.WUD.PBCWUD_ZONES"


    print("Cleaning up workspace.")
    if arcpy.Exists(projectedOutput):
        print("Removing old Reprojected Parcels.")
        arcpy.Delete_management(projectedOutput)
    if arcpy.Exists(parcelsPBC_copy):
        print("Removing copy of PBC Parcels.")
        arcpy.Delete_management(parcelsPBC_copy)
    if arcpy.Exists(parcelsWUD_copy):
        print("Removing Parcels.")
        arcpy.Delete_management(parcelsWUD_copy)
    print("Copying PBC Parcels from Open Data site.")
    arcpy.management.CopyFeatures(PBCGIS_Parcels, parcelsPBC_copy)
    print("Copying WUD Parcels.")
    arcpy.management.CopyFeatures(parcelsWUD, parcelsWUD_copy)

    try:
        print("Reprojecting PARCELS to be Florida State Plane.")
        arcpy.management.Project(parcelsPBC_copy,projectedOutput,
                                 'PROJCS["NAD_1983_StatePlane_Florida_East_FIPS_0901_Feet",'
                                 'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",'
                                 '6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",'
                                 '0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",'
                                 '656166.6666666665],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",'
                                 '-81.0],PARAMETER["Scale_Factor",0.9999411764705882],PARAMETER["Latitude_Of_Origin",'
                                 '24.33333333333333],UNIT["Foot_US",0.3048006096012192]]',
                                 "NAD_1983_To_HARN_Florida",
                                 'PROJCS["NAD_1983_HARN_StatePlane_Florida_East_FIPS_0901_Feet",'
                                 'GEOGCS["GCS_North_American_1983_HARN",DATUM["D_North_American_1983_HARN",'
                                 'SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],'
                                 'UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],'
                                 'PARAMETER["False_Easting",656166.6666666665],PARAMETER["False_Northing",0.0],'
                                 'PARAMETER["Central_Meridian",-81.0],PARAMETER["Scale_Factor",0.9999411764705882],PARAMETER["Latitude_Of_Origin",24.33333333333333],UNIT["Foot_US",0.3048006096012192]]',
                                 "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")


        # arcpy.management.Project(in_dataset=parcelsPBC_copy, out_dataset=projectedOutput,
        #                          out_coor_system="102658",
        #                          transform_method="NAD_1983_To_HARN_Florida", in_coor_system="102258",
        #                          preserve_shape="NO_PRESERVE_SHAPE", max_deviation="", vertical="NO_VERTICAL")

    except Exception as e:
        print(f"Projecting PBC Parcels failed. Check the variables for the 'Project' geoprocessing tool: {e}")
        sys.exit(0)


    try:
        # Set workspace environment
        arcpy.env.workspace = prodDB_LandBase

        print("Creating feature layers")
        arcpy.management.MakeFeatureLayer(parcelsWUD, "PARCELS_WUD_layer")
        arcpy.management.MakeFeatureLayer(projectedOutput, "PARCELS_reprojected_layer")
        arcpy.management.MakeFeatureLayer(PBC_Zones, "PBC_Zones_layer")

        print("Selecting Parcels within our service boundary (with 2000ft buffer).")
        sel_updatedOutput = arcpy.SelectLayerByLocation_management("PARCELS_reprojected_Layer", "INTERSECT",
                                                                   "PBC_Zones_layer", 2000,
                                                                   "NEW_SELECTION", "INVERT")
        if len(sel_updatedOutput) > 1:

            arcpy.DeleteFeatures_management(sel_updatedOutput)
            print("Reduced size of new parcel data. Only include data within Service Zones with 2000' buffer.")

            arcpy.SelectLayerByAttribute_management("PARCELS_reprojected_Layer", "CLEAR_SELECTION")

            deleteOld = arcpy.DeleteFeatures_management("PARCELS_WUD_layer")
            print("Deleted old features from local dataset")
            if deleteOld:

                print("Starting Append process.")
                appendDone = arcpy.Append_management("PARCELS_reprojected_layer", "PARCELS_WUD_layer",
                                                     "NO_TEST")

                if appendDone:
                    print("Append complete. WUD.PARCELS have been updated according to PBCGIS data")
                    # do clean up
                    print("Cleaning up tempDatabase." + "\n")
                    arcpy.DeleteFeatures_management(parcelsWUD_copy)
                    arcpy.DeleteFeatures_management(projectedOutput)

                else:
                    print("Append failed.")
                    sys.exit(0)
        else:
            print("No parcels where selected in our service area. Check the output from the reprojected feature class.")

    except():
        sys.exit(0)


def Centerlines(workspaceforCodes, PBCGIS_BaseConnection, prodDB_LandBase):

    print("Updating CENTERLINE_LN feature class.")

    # centerlineWUD = prodDB_LandBase + "/CENTERLINE_LN"  # for testing
    centerlineWUD = prodDB_LandBase + "/wGISMaps.WUD.CENTERLINE_LN"  # Feature that needs updating
    fcInput_copy = workspaceforCodes + "/CENTERLINE_copy"

    centerlinePBC = str(PBCGIS_BaseConnection / "ENG.CENTERLINE")  # Source of the new information
    projectedOutput = workspaceforCodes + "/ENG_CENTERLINE_reprojected"

    print("Cleaning up workspace.")
    if arcpy.Exists(projectedOutput):
        print("Removing old Reprojected Parcels.")
        arcpy.Delete_management(projectedOutput)

    print("Creating backups.")
    arcpy.management.CopyFeatures(centerlineWUD, fcInput_copy)

    # try:
    print("Reprojecting Centerlines to be Florida State Plane.")
    arcpy.management.Project(in_dataset=centerlinePBC, out_dataset=projectedOutput,
                             out_coor_system="102658",
                             transform_method="NAD_1983_To_HARN_Florida",
                             in_coor_system="102258",
                             preserve_shape="NO_PRESERVE_SHAPE", max_deviation="", vertical="NO_VERTICAL")

    # except():
    #     print("Projecting PBC ENG.CENTERLINE failed. Check the variables for the 'Project' geoprocessing tool")

    # try:
    # Set workspace environment
    arcpy.env.workspace = prodDB_LandBase

    arcpy.management.MakeFeatureLayer(centerlineWUD, "centerlineWUD_layer")

    print("Deleting old features from local dataset")
    deleteOld = arcpy.DeleteFeatures_management("centerlineWUD_layer")

    if deleteOld:
        print("Starting Append process.")
        appendDone = arcpy.Append_management(projectedOutput, "centerlineWUD_layer", "NO_TEST")
        if appendDone:
            print("Append complete. WUD.CENTERLINE_LN have been updated according to PBCGIS data")
            # do clean up
            print("Cleaning up tempDatabase." + "\n")
            arcpy.DeleteFeatures_management(fcInput_copy)
            arcpy.DeleteFeatures_management(projectedOutput)

    # except():
    #     sys.exit(0)


def WaterBodies(workspaceforCodes, PBCGIS_BaseConnection, prodDB_LandBase):

    print("Updating WATER_PY feature class.")

    # waterWUD = prodDB_LandBase + "/WATER_PY"  # for testing
    waterWUD = prodDB_LandBase + "/wGISMaps.WUD.WATER_BODIES"  # Feature that needs updating
    fcInput_copy = workspaceforCodes + "/WATER_BODIES_copy"

    waterPBC = str(PBCGIS_BaseConnection / "ENG.WATER")  # Source of the new information
    projectedOutput = workspaceforCodes + "/ENG_WATER_reprojected"

    print("Cleaning up workspace.")
    if arcpy.Exists(projectedOutput):
        print("Removing old Reprojected Waterbodies.")
        arcpy.Delete_management(projectedOutput)

    print("Copying a backups.")
    arcpy.management.CopyFeatures(waterWUD, fcInput_copy)

    try:
        print("Reprojecting Waterbodies to be Florida State Plane.")
        arcpy.management.Project(in_dataset=waterPBC, out_dataset=projectedOutput,
                                 out_coor_system="102658",
                                 transform_method="NAD_1983_To_HARN_Florida",
                                 in_coor_system="102258",
                                 preserve_shape="NO_PRESERVE_SHAPE", max_deviation="", vertical="NO_VERTICAL")

    except():
        print("Projecting PBC ENG.WATER failed. Check the variables for the 'Project' geoprocessing tool")

    try:
        # Set workspace environment
        arcpy.env.workspace = prodDB_LandBase

        print("Deleting old features from local dataset")
        deleteOld = arcpy.DeleteFeatures_management(waterWUD)

        if deleteOld:
            print("Starting Append process.")
            appendDone = arcpy.Append_management(projectedOutput, waterWUD, "NO_TEST")
            if appendDone:
                print("Append complete. WUD.WATER_PY have been updated according to PBCGIS data")
                # do clean up
                print("Cleaning up tempDatabase." + "\n")
                arcpy.DeleteFeatures_management(fcInput_copy)
                arcpy.DeleteFeatures_management(projectedOutput)

    except():
        sys.exit(0)


def Municipalities(workspaceforCodes, PBCGIS_BaseConnection, prodDB_LandBase):

    print("Updating MUNICIPALITIES feature class.")
    # muniWUD = prodDB_LandBase + "/MUNICIPALITIES"  # for testing
    muniWUD = prodDB_LandBase + "/wGISMaps.WUD.MUNICIPALITIES"  # Feature that needs updating
    fcInput_copy = workspaceforCodes + "/PROD_MUNICIPALITIES_copy"

    muniPBC = str(PBCGIS_BaseConnection / "PZB.MUNICIPALITIES")  # Source of the new information
    projectedOutput = workspaceforCodes + "/PZB_MUNICIPALITIES_reprojected"

    print("Cleaning up workspace.")
    if arcpy.Exists(projectedOutput):
        print("Removing old Reprojected Municipalities.")
        arcpy.Delete_management(projectedOutput)

    print("Creating backups.")
    arcpy.management.CopyFeatures(muniWUD, fcInput_copy)

    try:
        print("Reprojecting Municipalities to be Florida State Plane.")
        arcpy.management.Project(in_dataset=muniPBC, out_dataset=projectedOutput,
                                 out_coor_system="102658",
                                 transform_method="NAD_1983_To_HARN_Florida",
                                 in_coor_system="102258",
                                 preserve_shape="NO_PRESERVE_SHAPE", max_deviation=None, vertical="NO_VERTICAL")

    except():
        print("Projecting PBC PZB.MUNICIPALITIES failed. Check the variables for the 'Project' geoprocessing tool")

    try:

        arcpy.env.workspace = prodDB_LandBase

        print("Deleting old features from local dataset")
        deleteOld = arcpy.DeleteFeatures_management(muniWUD)

        if deleteOld:
            print("Starting Append process.")
            appendDone = arcpy.Append_management(projectedOutput, muniWUD, "NO_TEST")
            if appendDone:
                # do clean up
                print("Append complete. WUD.MUNICIPALITIES have been updated according to PBCGIS data.")
                print("Cleaning up tempDatabase." + "\n")
                arcpy.DeleteFeatures_management(fcInput_copy)
                arcpy.DeleteFeatures_management(projectedOutput)

    except():
        sys.exit(0)


if __name__ == '__main__':

    import logging

    logging.basicConfig(filename=r"W:\GIS\Scripts\Logs\Sync_PBCWUD_with_PBC_error.log", level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)

    try:

        from pathlib import Path
        import arcpy
        import sys, os
        import importlib

        moduleName = "shapely"
        try:
            importlib.import_module(moduleName)
            print(f"{moduleName} already imported.")
        except ImportError:
            sys.path.append("W:\\GIS\\Tools\\Codes_for_Tools_ArcGIS_Pro")
            print(f"Importing {moduleName}.")
        finally:
            from shapely.geometry import Point, Polygon, LineString

        try:
            connOra = "W:\\GIS\\Scripts\\ConnectToOracle.py"
            libFolder = os.path.dirname(os.path.abspath(os.__file__))
            if "cursorsPro.py" not in libFolder:
                import shutil

                shutil.copy(connOra, libFolder)
        except():
            arcpy.AddMessage("Could not copy ConnectToOracle.py to proper folder.")
            sys.exit(0)
        finally:
            import ConnectToOracle

        # Global Environment settings
        arcpy.SetLogMetadata(False)
        arcpy.SetLogHistory(False)
        arcpy.env.overwriteOutput = True
        arcpy.env.addOutputsToMap = 0
        workspaceforCodes = "W:/GIS/Scripts/Scheduled_Scripts_GISLIC/Workspaces/Sync_WUD_to_PBC.gdb"

        PBCGIS_BaseConnection = Path("W:/GIS/Database Connections/PBCGIS - GISPROD.sde")
        # prodDB_BaseConnection = "W:/GIS/WORKING FILES/EM Working Files/Databases/Local WUD Data.gdb"  # for testing
        prodDB_BaseConnection = "W:/GIS/Database Connections/GISdb_wGISProd.WUD.sde"
        aglMaps_BaseConnection = "W:/GIS/Database Connections/GISagl_wGISMaps.WUD.sde"
        # prodDB_LandBase = prodDB_BaseConnection + "/LandBase"  # for testing
        prodDB_LandBase = aglMaps_BaseConnection + "/wGISMaps.WUD.LandBase"

        SITUS(workspaceforCodes, PBCGIS_BaseConnection, prodDB_BaseConnection)
        Parcels(workspaceforCodes, aglMaps_BaseConnection, prodDB_LandBase)
        # Centerlines(workspaceforCodes, PBCGIS_BaseConnection, prodDB_LandBase)
        WaterBodies(workspaceforCodes, PBCGIS_BaseConnection, prodDB_LandBase)
        Municipalities(workspaceforCodes, PBCGIS_BaseConnection, prodDB_LandBase)


    except Exception as e:
        logger.error(str(e))

