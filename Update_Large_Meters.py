import arcpy, sys, time, re, importlib
from arcpy import env

moduleName = "shapely"
try:
    importlib.import_module(moduleName)
    print(f"{moduleName} already imported.")
except ImportError:
    sys.path.append("W:\\GIS\\Tools\\Codes_for_Tools_ArcGIS_Pro")
    print(f"Importing {moduleName}.")
finally:
    from shapely.geometry import Point, Polygon, LineString


def createNewMeterTable():

    """
    Testing workspace: C:\\Users\\Emyers\\Documents\\ArcGIS\\Projects\\testLargeMeterUpdater\\testLargeMeterUpdater.gdb

    After comparing existing meters in GIS Production, create a table that only has brand new meters from maximo.
    This prevents the next steps from adding duplicate meters.
    """

    # Create file paths for new Tables:
    wServiceConnectionSDEImport = workspace + "\\wServiceConnectionSDEImport"
    newLargeMaximoMeters = workspace + "\\newLargeMaximoMeters"


    # Make New Empty ServiceConnection Table to match schema (just in case)
    arcpy.management.CreateFeatureclass(workspace, "wServiceConnectionSDEImport", "POINT", wServiceConnectionProd,  # wServConn_Local
                                        "DISABLED", "DISABLED", '2236')
    arcpy.management.CreateTable(workspace, "newLargeMaximoMeters", largeMeterMaximo)
    addquery = "SERVICE_LOC_SEQ IN {0}".format(missingMeters)
    arcpy.management.Append(largeMeterMaximo, newLargeMaximoMeters, "TEST_AND_SKIP", None, '', addquery)

    return newLargeMaximoMeters, wServiceConnectionSDEImport

def createNewPoints(newLargeMaximoMeters):

    """
    Create two new tables: LargeMeters_XYTable, LargeMeters_Address
    These tables separete the two types of data, ones with XY and ones with an Address, to create proper point location.

    Create two new Layers: LargeMetersAddress_GeocodePoints, LargeMeters_XYPoints
    """

    LargeMeters_XYTable = workspace + "\\LargeMeters_XYTable"
    LargeMetersXY_Points = workspace + "\\LargeMeters_XYPoints"
    LargeMetersAddress = workspace + "\\LargeMeters_Address"
    LargeMetersAddress_GeocodePoints = workspace + "\\LargeMetersAddress_GeocodePoints"

    Composite_SITUS_CenterlineLocator_loc = "W:\\GIS\\Composite_SITUS_CenterlineLocator3_0.loc"

    sqlQueryXY = "SERVICE_TYPE_DESC_TEXT IN ('POTABLE WATER', 'RECLAIMED WATER') AND Longitude IS NOT Null AND Longitude <> 0"
    sqlQueryAddress = "SERVICE_TYPE_DESC_TEXT IN ('POTABLE WATER', 'RECLAIMED WATER') AND (Longitude = 0 OR Longitude IS Null)"

    # Make LargeMeter table with only XY values then Create Points using "XY to Point" tool
    arcpy.conversion.TableToTable(newLargeMaximoMeters, workspace, "LargeMeters_XYTable", sqlQueryXY)
    arcpy.management.XYTableToPoint(LargeMeters_XYTable, "LargeMeters_XYPoints", "LONGITUDE", "LATITUDE",
                                    z_field="", coordinate_system='4326')

    # Make LargeMeter table with only Addresses then Create Points using Geocoder
    if LargeMetersXY_Points:
        arcpy.conversion.TableToTable(newLargeMaximoMeters, workspace, "LargeMeters_Address", sqlQueryAddress)
        arcpy.geocoding.GeocodeAddresses(LargeMetersAddress, Composite_SITUS_CenterlineLocator_loc,
                                         "'Single Line Input' SERVICE_ADDRESS VISIBLE NONE",
                                         LargeMetersAddress_GeocodePoints, out_relationship_type="STATIC",
                                         country=[], location_type="", category=[], output_fields="")

    return LargeMetersXY_Points, LargeMetersAddress_GeocodePoints

def addNewToExisting(wServiceConnectionSDEImport, wServiceConnectionProd):

    try:
        # Append into wServiceConnectionSDEImport to field map rows:
        fieldMap = r'FACILITYID "Facility Identifier" true true false 20 Text 0 0,First,#;ACCOUNTID "Account Number" true true false 30 Text 0 0,First,#,LargeMeters_XYTable,ACCT_SEQ,-1,-1,LargeMetersAddress,ACCT_SEQ,-1,-1;METSERVICE "Metered Service" true true false 5 Text 0 0,First,#;SERVICETYPE "Service Type" true true false 50 Text 0 0,First,#,LargeMeters_XYTable,TYPE_OF_SERVICE,0,50,LargeMetersAddress,TYPE_OF_SERVICE,0,50;INSTALLDATE "Install Date" true true false 8 Date 0 0,First,#;LOCDESC "Location Description" true true false 200 Text 0 0,First,#,LargeMeters_XYTable,SERVICE_ADDRESS,0,200,LargeMetersAddress,SERVICE_ADDRESS,0,200;ROTATION "Rotation" true true false 8 Double 0 0,First,#;LOCATIONID "Location Identifier" true true false 20 Text 0 0,First,#;CRITICAL "CriticalCustomer" true true false 2 Short 0 0,First,#;ENABLED "Enabled" true true false 2 Short 0 0,First,#;ACTIVEFLAG "Active Flag" true true false 2 Short 0 0,First,#;OWNEDBY "Owned By" true true false 2 Short 0 0,First,#;MAINTBY "Managed By" true true false 2 Short 0 0,First,#;LASTUPDATE "Last Update Date" true true false 8 Date 0 0,First,#;LASTEDITOR "Last Editor" true true false 50 Text 0 0,First,#;METERTYPE "Meter Type" true true false 50 Text 0 0,First,#;WATERTYPE "Water Type" true true false 25 Text 0 0,First,#,LargeMeters_XYTable,SERVICE_TYPE_DESC_TEXT,0,50,LargeMetersAddress,SERVICE_TYPE_DESC_TEXT,0,50;DIAMETER "Diameter" true true false 8 Double 0 0,First,#,W:\GIS\Scripts\Scheduled_Scripts_GISLIC\Workspaces\LargeMeterUpdate.gdb\LargeMeters_XYTable,DIAMETER,-1,-1,W:\GIS\Scripts\Scheduled_Scripts_GISLIC\Workspaces\testLargeMeterUpdater.gdb\LargeMetersAddress,DIAMETER,-1,-1;ASBUILTDATE "ASBUILTDATE" true true false 8 Date 0 0,First,#;SOURCE "SOURCE" true true false 75 Text 0 0,First,#;LIFECYCLESTATUS "LifecycleStatus" true true false 20 Text 0 0,First,#;ZONE "ZONE" true true false 2 Short 0 0,First,#;GlobalID "GlobalID" false false true 38 GlobalID 0 0,First,#;MAPGRID "MAPGRID" true true false 8 Text 0 0,First,#;MXASSETNUM "MXASSETNUM" true true false 12 Text 0 0,First,#;GEOWORXSYNCID "GEOWORXSYNCID" true true false 12 Text 0 0,First,#;MXLOCATION "MXLOCATION" true true false 31 Text 0 0,First,#;WUD_KEY "WUD_KEY" true true false 8 Double 0 0,First,#;SITUS "SITUS" true true false 8 Double 0 0,First,#,W:\GIS\Scripts\Scheduled_Scripts_GISLIC\Workspaces\testLargeMeterUpdater.gdb\LargeMeters_XYTable,SITUS,-1,-1,W:\GIS\Scripts\Scheduled_Scripts_GISLIC\Workspaces\testLargeMeterUpdater.gdb\LargeMetersAddress,SITUS,-1,-1;SERVICE_LOC_SEQ "SERVICE_LOC_SEQ" true true false 8 Double 0 0,First,#,W:\GIS\Scripts\Scheduled_Scripts_GISLIC\Workspaces\testLargeMeterUpdater.gdb\LargeMeters_XYTable,SERVICE_LOC_SEQ,0,20,W:\GIS\Scripts\Scheduled_Scripts_GISLIC\Workspaces\testLargeMeterUpdater.gdb\LargeMetersAddress,SERVICE_LOC_SEQ,0,20;LONGITUDE "LONGITUDE" true true false 8 Double 0 0,First,#,W:\GIS\Scripts\Scheduled_Scripts_GISLIC\Workspaces\testLargeMeterUpdater.gdb\LargeMeters_XYTable,LONGITUDE,-1,-1,W:\GIS\Scripts\Scheduled_Scripts_GISLIC\Workspaces\testLargeMeterUpdater.gdb\LargeMetersAddress,LONGITUDE,-1,-1;LATITUDE "LATITUDE" true true false 8 Double 0 0,First,#,W:\GIS\Scripts\Scheduled_Scripts_GISLIC\Workspaces\testLargeMeterUpdater.gdb\LargeMeters_XYTable,LATITUDE,-1,-1,W:\GIS\Scripts\Scheduled_Scripts_GISLIC\Workspaces\testLargeMeterUpdater.gdb\LargeMetersAddress,LATITUDE,-1,-1;created_user "created_user" true true false 255 Text 0 0,First,#;created_date "created_date" true true false 8 Date 0 0,First,#;last_edited_user "last_edited_user" true true false 255 Text 0 0,First,#;last_edited_date "last_edited_date" true true false 8 Date 0 0,First,#'
        arcpy.management.Append("LargeMetersAddress_GeocodePoints;LargeMeters_XYPoints", wServiceConnectionSDEImport,
                                "NO_TEST", fieldMap, '', '')
        # arcpy.management.Append("LargeMetersAddress_GeocodePoints;LargeMeters_XYPoints", wServiceConnectionSDEImport, "NO_TEST", r'FACILITYID "Facility Identifier" true true false 20 Text 0 0,First,#;ACCOUNTID "Account Number" true true false 30 Text 0 0,First,#,LargeMeters_XYTable,ACCT_SEQ,-1,-1,LargeMetersAddress,ACCT_SEQ,-1,-1;METSERVICE "Metered Service" true true false 5 Text 0 0,First,#;SERVICETYPE "Service Type" true true false 50 Text 0 0,First,#,LargeMeters_XYTable,TYPE_OF_SERVICE,0,50,LargeMetersAddress,TYPE_OF_SERVICE,0,50;INSTALLDATE "Install Date" true true false 8 Date 0 0,First,#;LOCDESC "Location Description" true true false 200 Text 0 0,First,#,LargeMeters_XYTable,SERVICE_ADDRESS,0,200,LargeMetersAddress,SERVICE_ADDRESS,0,200;ROTATION "Rotation" true true false 8 Double 0 0,First,#;LOCATIONID "Location Identifier" true true false 20 Text 0 0,First,#;CRITICAL "CriticalCustomer" true true false 2 Short 0 0,First,#;ENABLED "Enabled" true true false 2 Short 0 0,First,#;ACTIVEFLAG "Active Flag" true true false 2 Short 0 0,First,#;OWNEDBY "Owned By" true true false 2 Short 0 0,First,#;MAINTBY "Managed By" true true false 2 Short 0 0,First,#;LASTUPDATE "Last Update Date" true true false 8 Date 0 0,First,#;LASTEDITOR "Last Editor" true true false 50 Text 0 0,First,#;METERTYPE "Meter Type" true true false 50 Text 0 0,First,#;WATERTYPE "Water Type" true true false 25 Text 0 0,First,#,LargeMeters_XYTable,SERVICE_TYPE_DESC_TEXT,0,50,LargeMetersAddress,SERVICE_TYPE_DESC_TEXT,0,50;DIAMETER "Diameter" true true false 8 Double 0 0,First,#,C:\Users\Emyers\Documents\ArcGIS\Projects\testLargeMeterUpdater\testLargeMeterUpdater.gdb\LargeMeters_XYTable,DIAMETER,-1,-1,C:\Users\Emyers\Documents\ArcGIS\Projects\testLargeMeterUpdater\testLargeMeterUpdater.gdb\LargeMetersAddress,DIAMETER,-1,-1;ASBUILTDATE "ASBUILTDATE" true true false 8 Date 0 0,First,#;SOURCE "SOURCE" true true false 75 Text 0 0,First,#;LIFECYCLESTATUS "LifecycleStatus" true true false 20 Text 0 0,First,#;ZONE "ZONE" true true false 2 Short 0 0,First,#;GlobalID "GlobalID" false false true 38 GlobalID 0 0,First,#;MAPGRID "MAPGRID" true true false 8 Text 0 0,First,#;MXASSETNUM "MXASSETNUM" true true false 12 Text 0 0,First,#;GEOWORXSYNCID "GEOWORXSYNCID" true true false 12 Text 0 0,First,#;MXLOCATION "MXLOCATION" true true false 31 Text 0 0,First,#;WUD_KEY "WUD_KEY" true true false 8 Double 0 0,First,#;SITUS "SITUS" true true false 8 Double 0 0,First,#,C:\Users\Emyers\Documents\ArcGIS\Projects\testLargeMeterUpdater\testLargeMeterUpdater.gdb\LargeMeters_XYTable,SITUS,-1,-1,C:\Users\Emyers\Documents\ArcGIS\Projects\testLargeMeterUpdater\testLargeMeterUpdater.gdb\LargeMetersAddress,SITUS,-1,-1;SERVICE_LOC_SEQ "SERVICE_LOC_SEQ" true true false 8 Double 0 0,First,#,C:\Users\Emyers\Documents\ArcGIS\Projects\testLargeMeterUpdater\testLargeMeterUpdater.gdb\LargeMeters_XYTable,SERVICE_LOC_SEQ,0,20,C:\Users\Emyers\Documents\ArcGIS\Projects\testLargeMeterUpdater\testLargeMeterUpdater.gdb\LargeMetersAddress,SERVICE_LOC_SEQ,0,20;LONGITUDE "LONGITUDE" true true false 8 Double 0 0,First,#,C:\Users\Emyers\Documents\ArcGIS\Projects\testLargeMeterUpdater\testLargeMeterUpdater.gdb\LargeMeters_XYTable,LONGITUDE,-1,-1,C:\Users\Emyers\Documents\ArcGIS\Projects\testLargeMeterUpdater\testLargeMeterUpdater.gdb\LargeMetersAddress,LONGITUDE,-1,-1;LATITUDE "LATITUDE" true true false 8 Double 0 0,First,#,C:\Users\Emyers\Documents\ArcGIS\Projects\testLargeMeterUpdater\testLargeMeterUpdater.gdb\LargeMeters_XYTable,LATITUDE,-1,-1,C:\Users\Emyers\Documents\ArcGIS\Projects\testLargeMeterUpdater\testLargeMeterUpdater.gdb\LargeMetersAddress,LATITUDE,-1,-1;created_user "created_user" true true false 255 Text 0 0,First,#;created_date "created_date" true true false 8 Date 0 0,First,#;last_edited_user "last_edited_user" true true false 255 Text 0 0,First,#;last_edited_date "last_edited_date" true true false 8 Date 0 0,First,#', '', '')

        # Fix field values to match domain codes:
        with arcpy.da.UpdateCursor(wServiceConnectionSDEImport,['LOCDESC', 'WATERTYPE', 'SOURCE','ZONE','MAPGRID']) as ucursor:
            for row in ucursor:
                if row[1] == "RECLAIMED WATER":
                    row[1] = "Reclaimed"
                if row[1] == "POTABLE WATER":
                    row[1] = "Potable"
                row[2] = "CIS"
                ucursor.updateRow(row)


        zonePoly = prodworkspace + "\\wGISProd.WUD.Boundaries\\wGISProd.WUD.PBCWUD_ZONES"
        gridPoly = prodworkspace + "\\wGISProd.WUD.LandBase\\wGISProd.WUD.ORTHO_GRID_PY"

        # Get list of Zone Polygons and its Number
        zoneList = []
        with arcpy.da.SearchCursor(zonePoly, "ZONE_") as zcursor:
            for row1 in zcursor:
                zoneList.append(row1[0])

        # Get list of Grid Polygons and its Number
        gridList = []
        with arcpy.da.SearchCursor(gridPoly, "GRID") as gcursor:
            for row2 in gcursor:
                gridList.append(row2[0])


        # Get list of Meter Points and their IDs and Coordinates
        allmeterIDS = []
        allmeterCoords = []
        meterPointShapes = []
        with arcpy.da.SearchCursor(wServiceConnectionSDEImport, ["OBJECTID", "SHAPE@XY"]) as mcursor:
            for row in mcursor:
                # create a point Object:
                meterCoord = row[1]
                meter = Point(meterCoord)
                # append data to respective list:
                allmeterIDS.append(row[0])
                allmeterCoords.append(row[1])
                meterPointShapes.append(meter)

        print (allmeterCoords)

        # Loop through each Grid, and whichever point is within its boundary, apply its grid number to the point
        print("Adding Grid number to meter.")
        for each1 in gridList:
            try:
                gridNumQuery = "GRID = '{0}'".format(str(each1))
                gridCoords = []
                with arcpy.da.SearchCursor(gridPoly, ["SHAPE@", "GRID"], gridNumQuery) as cursor:
                    for row in cursor:
                        for point in row[0]:
                            for coord in point:
                                gridCoords.append((coord.X, coord.Y))
                gridPolyShape = Polygon(gridCoords)

                with arcpy.da.UpdateCursor(wServiceConnectionSDEImport, ["OBJECTID", "SHAPE@XY", "MAPGRID"]) as gucursor:
                    for urow in gucursor:
                        meterCoord = urow[1]
                        meter = Point(meterCoord)
                        if gridPolyShape.contains(meter):
                            urow[2] = each1
                        else:
                            continue
                        gucursor.updateRow(urow)
            except RuntimeWarning:
                print("Meter points not within a Grid polygon.")


        # Loop through each Zone, and whichever point is within its boundary, apply its zone number to the point
        print("Adding Zone number to meter.")
        for each2 in zoneList:
            zoneNumQuery = "ZONE_ = {}".format(each2)
            zoneCoords = []
            with arcpy.da.SearchCursor(zonePoly, ["SHAPE@", "ZONE_"], zoneNumQuery) as cursor:
                for row in cursor:
                    for point in row[0]:
                        for coord in point:
                            zoneCoords.append((coord.X, coord.Y))
            zonePolyShape = Polygon(zoneCoords)

            with arcpy.da.UpdateCursor(wServiceConnectionSDEImport, ["OBJECTID", "SHAPE@XY", "ZONE"]) as zucursor:
                for urow in zucursor:
                    meterCoord = urow[1]
                    meter = Point(meterCoord)
                    if zonePolyShape.contains(meter):
                        urow[2] = each2
                    else:
                        continue
                    zucursor.updateRow(urow)


    except Exception:
        print("addNewToExisting code section died")
        time.sleep(5)
        sys.exit(1)

    print("Adding new meter(s) to Production.")
    arcpy.management.Append(wServiceConnectionSDEImport, wServiceConnectionProd, "NO_TEST")


if __name__ == '__main__':
    # Global Environment settings
    env.workspace = "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\LargeMeterUpdate.gdb"
    env.scratchWorkspace = "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\LargeMeterUpdate.gdb"
    workspace = env.workspace
    prodworkspace = "W:\\GIS\\Database Connections\\GISdb_wGISProd.WUD.sde"
    largeMeterMaximo = prodworkspace + "\\wGISProd.dbo.vWUD_Need_Large_Meter_Added"
    wServiceConnectionProd = prodworkspace + "\\wGISProd.WUD.WaterDistribution\\wGISProd.WUD.wServiceConnection"
    # wServConn_Local = r"C:\Users\Emyers\Documents\ArcGIS\Projects\testLargeMeterUpdater\testLargeMeterUpdater.gdb\wServiceConnection"

    # To allow overwriting outputs change overwriteOutput option to True.
    env.overwriteOutput = True
    # Don't add newly created tables/layers if a map is open
    arcpy.env.addOutputsToMap = 0

    # Check for new Large Meters.  Compare with Production Database using SERVICE_LOC_SEQ.
    maximoMeters = []
    with arcpy.da.SearchCursor(largeMeterMaximo, ["SERVICE_LOC_SEQ"]) as mcursor:
        for row in mcursor:
            maximoMeters.append(int(row[0]))

    prodMeters = []
    with arcpy.da.SearchCursor(wServiceConnectionProd, ['SERVICE_LOC_SEQ'], "DIAMETER >= 2") as pcursor:   # wServiceConnection
        for row in pcursor:
            if row[0] is not None:
                prodMeters.append(int(row[0]))

    setMaximoMeters = set(maximoMeters)
    setProdMeters = set(prodMeters)
    missingMeters = tuple(sorted(setMaximoMeters - setProdMeters))  # converting list to tuple
    if len(missingMeters) == 1:
        missingMeters = re.sub(r',', '', str(missingMeters))  # prepare code for sql query by removing comma at the end of tuple

    if not missingMeters:
        print ("No new meters.  Exiting")
        time.sleep(2)
        sys.exit(1)

    else:
        print("Meters with the SERVICE_LOC_SEQ to be added: {}".format(missingMeters))
        newLargeMaximoMeters, wServiceConnectionSDEImport = createNewMeterTable()
        LargeMeters_XYPoints, LargeMetersAddress_GeocodePoints = createNewPoints(newLargeMaximoMeters)
        addNewToExisting(wServiceConnectionSDEImport, wServiceConnectionProd)

