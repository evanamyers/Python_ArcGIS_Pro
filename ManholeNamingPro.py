# coding: utf-8
# This code will only work if one Lift Station boundary is selected

# NOTE: the "cursors" import will only work if both "cursorsPro" python scripts (found in W:\GIS\Tools\Codes for Tools) is
# copied and pasted into your ArcGIS Pro's python Lib folder (e.g C:\Program Files\ArcGISPro\bin\Python\envs\arcgispro-py3\Lib)

# created using python 2.7, works with 3.6
# created by Evan Myers

from __future__ import print_function, unicode_literals, absolute_import
import arcpy
import sys
import os
import shutil
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
    cursorForPro = "W:\\GIS\\Tools\\Codes_for_Tools_ArcGIS_Pro\\cursorsPro.py"
    libFolder = os.path.dirname(os.path.abspath(os.__file__))
    if "cursorsPro.py" not in libFolder:
        shutil.copy(cursorForPro, libFolder)
except():
    arcpy.AddMessage("Could not copy cursorsPro.py to proper folder.")
    sys.exit(0)
finally:
    import cursorsPro


def setup(mh, grvmains, lsbnd, sqlQuery):

    # Get coordinates of Lift Station Boundary
    lsbndCoords = []
    with arcpy.da.SearchCursor(lsbnd, ["SHAPE@", "LS_NO"]) as cursor:
        for row in cursor:
            for point in row[0]:
                for coord in point:
                    lsbndCoords.append((coord.X, coord.Y))

    lsbndPoly = Polygon(lsbndCoords)
    print(lsbndPoly)

    # Get coordinates of all Manholes that are within the selected Lift Station Boundary
    allmhIDS = []
    mhNoMH_NUM = []
    with arcpy.da.SearchCursor(mh, ["OBJECTID", "SHAPE@XY", "MH_Num"], where_clause=sqlQuery) as cursor:
        for row in cursor:
            mhcoord = row[1]
            manhole = Point(mhcoord)
            if lsbndPoly.contains(manhole):
                if row[2] is None:
                    mhNoMH_NUM.append(row[0])
                allmhIDS.append(row[0])
            else:
                continue

    mhOIDList = str(tuple(allmhIDS)).rstrip(',)') + ')'
    print(mhOIDList)

    # Get coordinates of all Gravity Mains that are within the selected Lift Station Boundary
    grvmainIDS = []
    grvmainNoID = []
    with arcpy.da.SearchCursor(grvmains,["OBJECTID", "SHAPE@", "FACILITYID"]) as cursor:
        for line in cursor:
            grvmainCoords = []
            for vert in line[1]:
                for coord in vert:
                    grvmainCoords.append((coord.X, coord.Y))
                grvmainLine = LineString(grvmainCoords)
            if lsbndPoly.contains(grvmainLine):
                if line[2] is None:
                    grvmainNoID.append(line[0])
                grvmainIDS.append(line[0])
            else:
                continue

    grvmainOIDList = str(tuple(grvmainIDS)).rstrip(',)') + ')'
    print(grvmainOIDList)

    if not grvmainNoID and not mhNoMH_NUM:
        arcpy.AddMessage("All PBCWUD Manholes and GravityMains have been numbered in this basin. "
                         "None will be edited.")
        sys.exit(0)

    elif not mhNoMH_NUM:
        arcpy.AddMessage("All PBCWUD Manholes have a number in this basin. None will be edited.")

    else:
        if not grvmainNoID:
            arcpy.AddMessage("All PBCWUD GravityMains have a FACILITYID in this basin. None will be edited.")



    mhListQuery = "OWNEDBY = 1 AND LIFECYCLESTATUS = 'ACTIVE' AND OBJECTID IN {0}".format(mhOIDList)
    grvmainListQuery = "OWNEDBY = 1 AND LIFECYCLESTATUS = 'ACTIVE' AND OBJECTID IN {0}".format(grvmainOIDList)

    print("Finished setup function")

    return lsbndPoly, mhOIDList, mhListQuery, grvmainListQuery, grvmainOIDList



def numberManholes(mhListQuery):

    print("Numbering Manholes")


    # Using mhListQuery from above, give manholes the number of the selected lift staion boundary
    with cursorsPro.UpdateCursor(mh, "LS", where_clause=mhListQuery) as cursor:
        for row in cursor:
            row[0] = selBdn_num
            cursor.updateRow(row)
    del cursor


    try:
        # Create list with all Lift Station numbers:
        LSlist = []
        # mhSource = lambda mh: arcpy.Describe(mh).catalogPath
        with arcpy.da.SearchCursor(mh, ["LS", "MH_Num", "OBJECTID"],
                                   where_clause=mhListQuery) as lscur:  # use "mhSource(mh)" for the first part if you
            # want every manhole
            for each in lscur:
                if each[0]:
                    num = int(each[0])
                    if num not in LSlist:
                        LSlist.append(num)
                else:
                    print(f"Manhole #{each[2]} has no LS Number to add to the list. Skipping")
        del lscur

        # Create dictionary for all manholes sharing the same Lift Station number:
        # e.g {4167: [41670001, 41670002, etc...]}
        # this is needed to find what numbers have already been used in the basin
        #mhSource = lambda mh: arcpy.Describe(mh).catalogPath
        for lsNum in LSlist:
            LSdict = {}
            mhList = []
            arcpy.AddMessage(f"Searching basin: {lsNum}")
            with arcpy.da.SearchCursor(mh, ["LS", "MH_Num", "OBJECTID"], where_clause=mhListQuery) as cur:  # mhSource
                for row in cur:
                    if row[0] == str(lsNum):
                        mhList.append(row[2])
                        LSkey = int(row[0])
                        LSdict.setdefault(LSkey, [])
                        if row[1] not in LSdict[LSkey] and row[1] is not None:
                            LSdict[LSkey].append(row[1])
            del cur
            mhNum = len(mhList)

            # availNums, list of numbers that can be used before new ones are made:
            for key, values in LSdict.items():
                if isinstance(values, list):
                    print (key, values)

                    # Do this if there are no numbered manholes in the LS Boundary:
                    if values[0] is None:
                        arcpy.AddMessage(f"Basin {key} has no values. Numbering starting at {key}0001")
                        start = key * 10000 + 1
                        maxnum = key * 10000 + mhNum
                        with cursorsPro.UpdateCursor(mh, ["LS", "MH_Num", "OBJECTID"],
                                                     where_clause=mhListQuery) as ucur:  # mhSource
                            while start <= maxnum:
                                for row in ucur:
                                    if row[1] is None and row[0] == str(key):
                                        print(f"Manhole OID {row[2]} has been numbered: {start}")
                                        row[1] = start
                                        start = start + 1
                                        ucur.updateRow(row)
                        del ucur

                        arcpy.AddMessage(f"Finished numbering {len(maxnum)} manholes.")

                    # Do this if some manholes have been numbered already:
                    else:
                        # values used for equations:
                        mhBasin = key * 10000
                        mhNum = len(mhList)
                        maxnum = mhBasin + mhNum

                        # Create a list of numbers that should be used when the tool is finished.
                        mhBasinNums = []
                        for i in range(1, mhNum + 1):
                            mhBasinNums.append(mhBasin + i)
                            print(i)
                        print(mhBasinNums)

                        # valuesf = list(filter(lambda a: a is not None, values))  ###########
                        gapValues = set(range(values[0], maxnum + 1)) # valuesf
                        availNums = sorted(set(mhBasinNums) - set(values))
                        # availNums = sorted(set(list(gapValues)) - set(values)) # valuesf
                        # availNums = [x for x in range(values[0], values[-1]) if x not in values and not None]
                        arcpy.AddMessage(f"Use these before new ones are needed: {availNums}")
                        availNums_iter = iter(availNums)
                        with cursorsPro.UpdateCursor(mh, ["LS", "MH_Num", "OBJECTID"],
                                                     where_clause=mhListQuery) as ucur1:  # mhSource
                            for row in ucur1:
                                if row[1] is None and row[0] == str(key):
                                    if availNums:
                                        try:
                                            value = next(availNums_iter)
                                            row[1] = value
                                            print(f"Manhole OID {row[2]} will be numbered {value}")
                                            arcpy.AddMessage(f"Manhole OID {row[2]} has been numbered: {value}")
                                            ucur1.updateRow(row)
                                        except StopIteration:
                                            print('No more values in list')
                        del ucur1

                        arcpy.AddMessage(f"Finished numbering {len(availNums)} manholes.")

        arcpy.SelectLayerByAttribute_management(mh, 'CLEAR_SELECTION')


    except():
        print("No manholes selected")
        arcpy.AddMessage("This basin has no manholes to select.")


def numberGravityMains(mhListQuery, grvmainListQuery):

    print("Numbering Gravity Mains")

    try:

        # Get all the XY of the selected manholes in the LS Boundary
        manholeXY = []
        with arcpy.da.SearchCursor(mh, ["OID@", "SHAPE@XY", "MH_NUM", "LS"], where_clause=mhListQuery) as scur:
            for row in scur:
                x, y = row[1]
                manholeXY.append([(float("{:.3f}".format(x)), float("{:.3f}".format(y))), row[2]])
        del scur

        # Get the XY of the first and last vertex of each gravity main.  The manhole that shares the exact XY for that
        # vertex will have its number copied to the respected Upstream/Downstream field.
        # grvmainsSource = lambda grvmains: arcpy.Describe(grvmains).catalogPath
        pipecount = 0
        with cursorsPro.UpdateCursor(grvmains, ["OID@", "SHAPE@", "FACILITYID", "FROMMH", "TOMH", "LS"],
                                     where_clause=grvmainListQuery) as ucur2:  # grvmainsSource(grvmains)
            for row in ucur2:
                if row[2] is None or len(row[2]) == 1:
                    newGravityXY = []
                    gravityXY = []
                    for part in row[1]:
                        for pnt in part:
                            gravityXY.append((float("{:.3f}".format(pnt.X)), float("{:.3f}".format(pnt.Y))))
                    newGravityXY.append(gravityXY[::len(gravityXY) - 1])
                    print(newGravityXY)

                    # for each gravity main segment, get the MH_Num from each manhole feature on both ends of the line
                    # e.g : [(868965.236, 859237.169), (868955.144, 858979.073)]
                    for main in newGravityXY:
                        for manhole in manholeXY:
                            if main[0] == manhole[0]:  # check if a manhole exists, if numbers match, good
                                upstream = manhole[1]  # give the MH_Num to the upstream field
                                print(f"This is the upstream manhole. Its number is {upstream}")
                                row[3] = upstream
                            if main[1] == manhole[0]:
                                downstream = manhole[1]  # give the MH_Num to the downstream field
                                print(f"This is the downstream manhole. Its number is {downstream} \n")
                                row[4] = downstream

                    if row[3] is not None and row[4] is not None:
                        row[2] = (str(row[3]) + "-" + str(row[4]))
                        row[5] = selBdn_num
                    if row[3]:
                        if row[4] is None:
                            row[2] = (str(row[3]) + "-" + str(0000))
                            row[5] = selBdn_num
                    # updates with the first and last manhole in list
                    arcpy.AddMessage(f"Gravitymain, OID {row[0]} has been numbered: {row[2]}")
                    pipecount += 1
                ucur2.updateRow(row)
        arcpy.AddMessage(f"Finished numbering {pipecount} gravitymains.")
        del ucur2

        arcpy.SelectLayerByAttribute_management(grvmains, 'CLEAR_SELECTION')


    except():
        arcpy.AddMessage("This basin has no gravity mains to select.")


if __name__ == '__main__':

    # Global Environment settings
    arcpy.SetLogMetadata(False)
    arcpy.SetLogHistory(False)
    arcpy.env.overwriteOutput = True
    arcpy.env.addOutputsToMap = 1
    sys.tracebacklimit = 0

    aprx = arcpy.mp.ArcGISProject('current')
    currentMap = aprx.activeMap
    lyrList = currentMap.listLayers()

    sqlQuery = "OWNEDBY = 1 AND LIFECYCLESTATUS = 'ACTIVE'"

    mh = ()
    grvmains = ()
    lsbnd = ()

    prodLyrs = []
    for each in lyrList:
        if each.isFeatureLayer:
            desc = arcpy.Describe(each)
            fcDB = desc.catalogPath
            if "waterdistribution" or "sewerstormwater" in fcDB:
                keyFC = each.longName
                if "wGISProd.WUD." in fcDB and "Manhole" in keyFC:
                    mh = keyFC

                elif "wGISProd.WUD." in fcDB and "GravityMain" in keyFC:
                    grvmains = keyFC

                elif "wGISProd.WUD." in fcDB and "LiftStationsBoundaries" in keyFC:
                    lsbnd = keyFC

    if mh and grvmains and lsbnd:
        arcpy.AddMessage("Found all layers")
        print("Found all layers")

    elif not mh:
        raise ValueError(
            "The required layer is not in map: 'Manhole'. "
            "Make sure there is a Manhole layer sourced to Production Database. "
            "Remember to change it to a version if needed.")
    elif not grvmains:
        raise ValueError(
            "The required layer is not in map: 'GravityMain'. "
            "Make sure there is a GravityMain layer sourced to Production Database. "
            "Remember to change it to a version if needed.")
    elif not lsbnd:
        raise ValueError(
            "The required layer is not in map: 'LiftStationsBoundaries'. "
            "Make sure there is a LiftStationBoundary layer sourced to Production Database. "
            "Remember to change it to a version if needed.")
    else:
        raise ValueError(
            "None of the required layers are in map: 'Manhole', 'GravityMain', 'LiftStationsBoundary'."
            "Make sure the layers are sourced to Production Database. "
            "Remember to change it to a version if needed.")


    # Check if only one Lift Station Boundary is selected
    selBdn_list = []
    with arcpy.da.SearchCursor(lsbnd, "LS_No") as cursor1:
        for row1 in cursor1:
            selBdn_list.append(row1[0])
        if len(selBdn_list) == 1:
            selBdn_num = row1[0]
            sel_sqlQuery = str("LS = '{}'".format(selBdn_num))
        else:
            raise ValueError("Make sure only one Lift Station Boundary is selected.")


    # setup(mh, grvmains, lsbnd, sqlQuery)
    lsbndPoly, mhOIDList, mhListQuery, grvmainListQuery, grvmainOIDList = setup(mh, grvmains, lsbnd, sqlQuery)
    numberManholes(mhListQuery)
    numberGravityMains(mhListQuery, grvmainListQuery)


