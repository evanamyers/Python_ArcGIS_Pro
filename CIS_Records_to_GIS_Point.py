"""

Code tested and works in python 3.7

"""

import arcpy
import os
from arcpy import env
from datetime import datetime


def create_WUDCISGISINFO(workspace):  # Create a table that will be populated with XY values from SITUS and Parcels
    # Nothing in CIS or ProdDB is edited or deleted.

    print("Creating WUDCISGISINFO table. Brand new table with 'Generated_By' and 'XY' fields.")
    arcpy.AddMessage("Creating WUDCISGISINFO table. Brand new table with 'Generated_By' and 'XY' fields.")

    # CISGISINFO = r"W:\GIS\Database Connections\pCIS.sde\WUDCIS.V_GIS_INFO"
    CISGISINFO = r"W:\GIS\WORKING FILES\EM Working Files\CustomerStuff.gdb\V_GIS_INFO"
    allFields = []
    fieldnames = arcpy.Describe(CISGISINFO).fields
    for fields in fieldnames:
        if fields not in allFields:
            if fields.baseName not in ['Shape', 'OBJECTID', 'GlobalID', 'Shape_Length']:
                allFields.append(fields.baseName.upper())
    del fieldnames

    print ("Creating copy of GIS_INFO table.")
    arcpy.AddMessage("Creating copy of GIS_INFO table.")
    WUDCISGISINFO = workspace + "\\WUDCISGISINFO"
    if arcpy.Exists(WUDCISGISINFO):
        arcpy.Delete_management(WUDCISGISINFO)
    arcpy.CreateTable_management(workspace, "WUDCISGISINFO", CISGISINFO)
    print("Finished creating GIS_INFO table.")
    arcpy.AddMessage("Finished creating GIS_INFO table.")

    targetCur = arcpy.da.InsertCursor(WUDCISGISINFO, allFields)
    with arcpy.da.SearchCursor(CISGISINFO, allFields) as sourceCur:
        for row in sourceCur:
            targetCur.insertRow(row)

    del targetCur

    print("Adding 'Generated_by', 'X', and 'Y' fields to GIS_INFO table.")
    arcpy.AddMessage("Adding 'Generated_by', 'X', and 'Y' fields to GIS_INFO table.")
    lstFields = [f.name for f in arcpy.ListFields(WUDCISGISINFO)]
    if "Generated_By" not in lstFields:
        arcpy.AddField_management(WUDCISGISINFO, "Generated_By", "TEXT")
    if 'X' not in lstFields:
        arcpy.AddField_management(WUDCISGISINFO, "X", "DOUBLE")
    if 'Y' not in lstFields:
        arcpy.AddField_management(WUDCISGISINFO, "Y", "DOUBLE")

    del lstFields

    print("Finished creating WUDCISGISINFO table.")
    arcpy.AddMessage("Finished creating WUDCISGISINFO table.")


def calcXY_SITUS():
    # Nothing in CIS or ProdDB is edited or deleted.

    print("Running calcXY_SITUS function. Adding XY from SITUS.")
    arcpy.AddMessage("Running calcXY_SITUS function. Adding XY from SITUS.")

    CWSITUS_reproj = "W:\\GIS\\Tools\\WorkspacesForTools\\Update_SITUS_to_PBC.gdb\\CWSITUS_reproj"

    print("Adding X and Y fields if needed to CWSITUS_reproj and Calculating X and Y fields to decimal degrees.")
    arcpy.AddMessage("Adding X and Y fields if needed to CWSITUS_reproj and Calculating X and Y fields to decimal degrees.")
    lstFields = [f.name for f in arcpy.ListFields(CWSITUS_reproj)]
    if 'X' not in lstFields:
        arcpy.AddField_management(CWSITUS_reproj, "X", "DOUBLE")
    if 'Y' not in lstFields:
        arcpy.AddField_management(CWSITUS_reproj, "Y", "DOUBLE")

    with arcpy.da.UpdateCursor(CWSITUS_reproj, ['X', 'Y', 'Shape@']) as cursor:
        for row in cursor:
            if row[2]:
                # Calculating Longitude Field
                if row[0] is None or not 724000 < row[0] < 960000:
                    pt = row[2].projectAs('2236').centroid
                    row[0] = round(pt.X, 3)
                # Calculating Latitude Field
                if row[1] is None or not 724000 < row[1] < 960000:
                    pt = row[2].projectAs('2236').centroid
                    row[1] = round(pt.Y, 3)

                cursor.updateRow(row)

    del lstFields

    print("Finished calculating XY from SITUS.")
    arcpy.AddMessage("Finished calculating XY from SITUS.")


def calcXY_ParcelPoints(workspace, prodworkspace):
    # Nothing in CIS or ProdDB is edited or deleted.

    print("Running calcXY_ParcelPoints function. Adding XY from Parcels.")
    arcpy.AddMessage("Running calcXY_ParcelPoints function. Adding XY from Parcels.")

    Parcels = prodworkspace + "\\wGISProd.WUD.LandBase\\wGISProd.WUD.PARCELS"
    ParcelPoint = workspace + "\\ParcelPoint"

    print ("Creating points from wGISProd.WUD.PARCELS")
    arcpy.AddMessage("Creating points from wGISProd.WUD.PARCELS")
    arcpy.FeatureToPoint_management(Parcels, ParcelPoint)

    lstFields = [f.name for f in arcpy.ListFields(ParcelPoint)]
    print ("Adding X and Y fields if needed to ParcelPoint and Calculating X and Y fields to decimal degrees.")
    arcpy.AddMessage("Adding X and Y fields if needed to ParcelPoint and Calculating X and Y fields to decimal degrees.")
    if 'X' not in lstFields:
        arcpy.AddField_management(ParcelPoint, "X", "DOUBLE")
    if 'Y' not in lstFields:
        arcpy.AddField_management(ParcelPoint, "Y", "DOUBLE")

    with arcpy.da.UpdateCursor(ParcelPoint, ['X', 'Y', 'Shape@']) as cursor:
        for row in cursor:
            if row[2]:
                # Calculating Longitude Field
                if row[0] is None or not 724000 < row[0] < 960000:
                    pt = row[2].projectAs('2236').centroid
                    row[0] = round(pt.X, 3)
                # Calculating Latitude Field
                if row[1] is None or not 724000 < row[1] < 960000:
                    pt = row[2].projectAs('2236').centroid
                    row[1] = round(pt.Y, 3)

                cursor.updateRow(row)

    del lstFields

    print("Finished calculating XY from Parcels.")
    arcpy.AddMessage("Finished calculating XY from Parcels.")


def geocodeGISINFO(workspace):
    # Nothing in CIS or ProdDB is edited or deleted.

    print("Running geocodeGISINFO function.  Adding XY for geocoded locations.")
    arcpy.AddMessage("Running geocodeGISINFO function.  Adding XY for geocoded locations.")

    WUDCISGISINFO = workspace + "\\WUDCISGISINFO"
    geocoder = "W:\\GIS\\Composite_SITUS_CenterlineLocator3_0.loc"
    geocodePoints = workspace + "\\geocodePoints"

    arcpy.geocoding.GeocodeAddresses(WUDCISGISINFO, geocoder,
                                     "'Address or Place' SRVC_STREET VISIBLE NONE;Address2 <None> VISIBLE "
                                     "NONE;Address3 <None> VISIBLE NONE;Neighborhood <None> VISIBLE NONE;City "
                                     "CITY_NAME VISIBLE NONE;County <None> VISIBLE NONE;State <None> VISIBLE NONE;ZIP "
                                     "ZIP_CODE VISIBLE NONE;ZIP4 <None> VISIBLE NONE;Country <None> VISIBLE NONE",
                                     geocodePoints, "STATIC",
                                     None, "ADDRESS_LOCATION", None, "ALL")


    with arcpy.da.UpdateCursor(geocodePoints, ['USER_LONGITUDE', 'USER_LATITUDE', 'Shape@']) as cursor:
        for row in cursor:
            if row[2]:
                # Calculating Longitude Field
                if row[0] is None or not 724000 < row[0] < 960000:
                    pt = row[2].projectAs('2236').centroid
                    row[0] = round(pt.X, 3)
                # Calculating Latitude Field
                if row[1] is None or not 724000 < row[1] < 960000:
                    pt = row[2].projectAs('2236').centroid
                    row[1] = round(pt.Y, 3)

                cursor.updateRow(row)

    print("Finished calculating XY from geocoder.")
    arcpy.AddMessage("Finished calculating XY from geocoder.")


def joinTables(workspace, prodworkspace):

    print("Running joinTables function.  Adding XY values")
    arcpy.AddMessage("Running joinTables function.  Adding XY values")

    WUDCISGISINFO = workspace + "\\WUDCISGISINFO"
    CWSITUS_reproj = "W:\\GIS\\Tools\\WorkspacesForTools\\Update_SITUS_to_PBC.gdb\\CWSITUS_reproj"
    prod_meters = prodworkspace + "\\wGISProd.WUD.GPS_Features\\wGISProd.WUD.wMeterGPS"
    ParcelPoint = workspace + "\\ParcelPoint"
    geocodePoints = workspace + "\\geocodePoints"


    # Source's field lists
    WUDCISFields = ['SITUS', 'PCN', 'SEVICE_LOC_SEQ', 'ACCT_SEQ', 'Generated_By', 'X', 'Y']
    CWSITUSFields = ['SITUS_SEQ', 'X', 'Y']
    ParcelFields = ['PARID', 'X', 'Y']
    MeterFields = ['S_LOC_SEQ', 'Easting', 'Northing']
    geocodeFields = ['USER_ACCT_SEQ', 'USER_LONGITUDE', 'USER_LATITUDE']

    # Use list comprehension to build a dictionary from a da.SearchCursor
    valueDict1 = {r[0]: (r[1:]) for r in arcpy.da.SearchCursor(CWSITUS_reproj, CWSITUSFields)}
    valueDict2 = {r[0]: (r[1:]) for r in arcpy.da.SearchCursor(ParcelPoint, ParcelFields)}
    valueDict3 = {r[0]: (r[1:]) for r in arcpy.da.SearchCursor(prod_meters, MeterFields)}
    valueDict4 = {r[0]: (r[1:]) for r in arcpy.da.SearchCursor(geocodePoints, geocodeFields)}

    with arcpy.da.UpdateCursor(WUDCISGISINFO, WUDCISFields) as updateCur:
        for urow in updateCur:
            if urow[4] is None:
                # store the Join value of the row being updated in a keyValue variable
                keyValue1 = urow[0]  # SITUS value
                keyValue2 = urow[1]  # PCN value
                keyValue3 = urow[2]  # S_LOC_SEQ value
                keyValue4 = urow[3]  # ACCT_SEQ value
                # verify that the keyValue is in the Dictionary
                if keyValue1 in valueDict1:
                    # transfer the values stored under the keyValue from the dictionary to the updated fields.
                    urow[4] = "SITUS_XY"
                    urow[5] = valueDict1[keyValue1][0]
                    urow[6] = valueDict1[keyValue1][1]
                elif keyValue2 in valueDict2:
                    urow[4] = "PARCELPOINT_XY"
                    urow[5] = valueDict2[keyValue2][0]
                    urow[6] = valueDict2[keyValue2][1]
                elif keyValue3 in valueDict3:
                    urow[4] = "GPSMETER_XY"
                    if valueDict3[keyValue3][0] != 0:
                        urow[5] = valueDict3[keyValue3][0]
                    if valueDict3[keyValue3][1] != 0:
                        urow[6] = valueDict3[keyValue3][1]
                elif keyValue4 in valueDict4:
                    urow[4] = "GEOCODED_XY"
                    if valueDict4[keyValue4][0] != 0:
                        urow[5] = valueDict4[keyValue4][0]
                    if valueDict4[keyValue4][1] != 0:
                        urow[6] = valueDict4[keyValue4][1]

                else:
                    continue
                updateCur.updateRow(urow)


    del valueDict1
    del valueDict2
    del valueDict3
    del valueDict4

    CISaccounts = "W:\\GIS\\Database Connections\\GISagl_wGISMaps.WUD.sde\\wGISMaps.WUD.CIS\\wGISMaps.WUD.CISaccounts"
    arcpy.management.XYTableToPoint(WUDCISGISINFO, CISaccounts, "X", "Y", None, 2236)

    with arcpy.da.UpdateCursor(CISaccounts, ["X", "Y"]) as dcur:
        for drow in dcur:
            if drow[0] == 0 and drow[1] == 0:
                dcur.deleteRow()
            if drow[0] is None and drow[1] is None:
                dcur.deleteRow()

    arcpy.conversion.TableToTable(WUDCISGISINFO, ws, "geocodeNoMatch", "X IS NULL And Y IS NULL")

    print("Exporting CIS Records with no matach to an excel table: "
          "'W:\GIS\Scripts\Scheduled_Scripts_GISLIC\CIS_Records_No_Match.xlsx'")
    arcpy.AddMessage("Exporting CIS Records with no matach to an excel table: "
                     "'W:\GIS\Scripts\Scheduled_Scripts_GISLIC\CIS_Records_No_Match.xlsx'")
    geocodeNoMatch = workspace + "\\geocodeNoMatch"
    arcpy.conversion.TableToExcel(geocodeNoMatch, r"W:\GIS\Scripts\Scheduled_Scripts_GISLIC\CIS_Records_No_Match.xlsx",
                                  "ALIAS", "DESCRIPTION")


if __name__ == '__main__':

    cisDB = "W:\\GIS\\Database Connections\\pCIS.sde"
    ws = "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\CIS_to_GIS_Point.gdb"
    pws = "W:\\GIS\\Database Connections\\GISdb_wGISProd.OSA.sde"

    env.workspace = ws
    env.scratchWorkspace = ws
    env.overwriteOutput = True

    startTime = datetime.now()

    create_WUDCISGISINFO(ws)
    calcXY_SITUS()
    calcXY_ParcelPoints(ws, pws)
    geocodeGISINFO(ws)
    joinTables(ws, pws)
    print("Code completion time: {}".format(datetime.now() - startTime))

