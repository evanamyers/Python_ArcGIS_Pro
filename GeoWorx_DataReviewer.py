"""
This script creates a data reviewer with GeoWorx Checks and is run on entire  "GISdb_wGISProd.OSA.sde"  database.
If there are any errors, an e-mail is sent to whoever is listed below.
"""

contacts = ['emyers@pbcwater.com']


import arcpy, sys, datetime, subprocess, smtplib, re

try:
    from email.message import EmailMessage
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'email'])
finally:
    from email.message import EmailMessage


# variables for datareviewer only
batch_file = "W:\\GIS\Tools\\DataReviewer\\BatchFiles\\Checks_for_GeoWorx.rbj"
production_workspace = "W:\\GIS\\Database Connections\\GISdb_wGISProd.OSA.sde"
datarevDB = "W:\\GIS\\Database Connections\\DataReviewer@GISdb.WUD.sde"
revSessionTable = datarevDB + "\\DataReviewer.WUD.REVSESSIONTABLE"


if arcpy.CheckExtension("Datareviewer") == 'Available':
    print("Data Reviewer is ready for use.")
else:
    arcpy.AddMessage("No Data Reviewer extension available. Canceling data reviewer.")
    print("No Data Reviewer extension available. Canceling data reviewer.")
    sys.exit()


startTime = datetime.datetime.now().replace(microsecond=0)
print("Operation started on {}".format(startTime))

# check out a data reviewer extension license
arcpy.CheckOutExtension("datareviewer")
print("Step 2. Data Reviewer has been checked out.")


# Process: Enable Data Reviewer
arcpy.EnableDataReviewer_Reviewer(datarevDB, 102258, "", "")
print("Step 3. Data Reviewer Enabled.")
arcpy.AddMessage("Data Reviewer Enabled")

# create session
i = datetime.datetime.today()
sessionTime = i.strftime("%Y-%m-%d %I:%M")
Session_Name = ("GeoWorx" + " / " + sessionTime)
print("Step 4. {}, name of session".format(Session_Name))

reviewSession = arcpy.CreateReviewerSession_Reviewer(datarevDB, Session_Name)  # , "", "SESSION"
arcpy.AddMessage("Session {} has been created.".format(Session_Name))
print("Step 5. Session {} has been created.".format(Session_Name))

arcpy.AddMessage("Batch job is starting...")
arcpy.ExecuteReviewerBatchJob_Reviewer(datarevDB, reviewSession, batch_file, production_workspace)

arcpy.CheckInExtension("Datareviewer")

endTime = datetime.datetime.now().replace(microsecond=0)
dur = endTime - startTime
dur = str(dur)
print('Duration: {}'.format(dur))


# Create e-mail if reviewer found errors

try:
    sessionID = re.search(r'\d+', str(reviewSession)).group()
    versionTable = r"W:\GIS\Database Connections\DataReviewer@GISdb.OSA.sde\DataReviewer.WUD.REVTABLEMAIN"
    sqlQuery = "SESSIONID = {}".format(sessionID)
    errorList = []
    with arcpy.da.SearchCursor(versionTable, "SESSIONID", sqlQuery) as cursor:
        for row in cursor:
            errorList.append(row[0])
    errorNum = len(errorList)

    if errorNum != 0:
        #  Send Email when finished
        SMTPserver = '151.132.136.225'
        SMTPport = 25
        # sender = 'GISLIC@pbcwater.com'  # GISLIC server
        sender = 'emyers@pbcwater.com'
        # contacts = ['emyers@pbcwater.com', 'dthorpe@pbcwater.com', 'jdelmastro@pbcwater.com']
        body = 'GeoWorx Data Review completed.'

        msg = EmailMessage()
        msg['Subject'] = "GeoWorx Complete"
        msg['From'] = sender
        msg['To'] = ', '.join(contacts)
        msg.set_content(f"GeoWorx Data Review Complete.  There are {errorNum} errors.")

        print("Sending E-mail to {}".format(contacts))
        with smtplib.SMTP(SMTPserver, SMTPport) as smtp:
            smtp.send_message(msg)

except():
    sys.exit(0)

