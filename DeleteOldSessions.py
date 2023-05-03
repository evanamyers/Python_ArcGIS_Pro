"""
This script will only delete sessions that are created through the "AsBuiltDataReviewer" script tool or sessions that
follow the same time and date format as the tool's.

Sessions that are more than a month old will be deleted.


"""

import arcpy, sys
from datetime import datetime, timedelta
from dateutil.parser import *


datarevDB = "W:\\GIS\\Database Connections\\DataReviewer@GISdb.WUD.sde"
revSessionTable = datarevDB + "\\DataReviewer.WUD.REVSESSIONTABLE"


arcpy.env.workspace = datarevDB


if arcpy.CheckExtension("Datareviewer") == 'Available':
    startTime = datetime.now().replace(microsecond=0)
    print("Operation started on {}".format(startTime))
    print("Data Reviewer is ready for use.")

else:
    arcpy.AddMessage("No Data Reviewer extension available. Canceling data reviewer.")
    print("No Data Reviewer extension available. Canceling data reviewer.")
    sys.exit()


ot = datetime.today() - timedelta(days=30)
oldTime = ot.strftime("%Y-%m-%d %I:%M")
print(f"Old if past this date: {oldTime}")


oldSessions = []
with arcpy.da.SearchCursor(revSessionTable, ["SESSIONNAME", "SESSIONID"]) as cursor:
    for row in cursor:
        addSession = 'Session ' + str(row[1]) + ' : ' + row[0]
        session = str(addSession).split(' / ')
        try:
            sessionTime = parse(session[1], fuzzy=False)
            if sessionTime < ot:
                if row not in oldSessions:
                    oldSessions.append(' / '.join(session))
        except IndexError:
            continue
print(oldSessions)

sessionsList = ';'.join(oldSessions)

arcpy.DeleteReviewerSession_Reviewer(reviewer_workspace=datarevDB, session=sessionsList)


# check out a data reviewer extension license
arcpy.CheckOutExtension("datareviewer")
print("Step 2. Data Reviewer has been checked out.")


i = datetime.today()
sessionTime = i.strftime("%Y-%m-%d %I:%M")

