"""
Set up the Template Builder for GraniteNet Schedular:

1.  Create new report -> Edit -> Reports Settings -> File name: Template builder....:

Object.SubjectsToPerformOn.Name + " " + Object.Assessment.Reverse + " on " + Object.Started
"""

import os, re
from PyPDF2 import PdfFileMerger
from datetime import datetime


# noinspection PyShadowingNames
def deleteCopies(folderPath):

    print("Deleting duplicate reports. (e.g files with (1), (2),...")

    files = os.listdir(folderPath)
    pattern = re.compile(r"\(\d+\)")
    # unique_files = {}
    for file in files:
        # Check if the file name matches the pattern
        match = pattern.search(file)
        if match:
            # Remove the number in parentheses+number from the file name
            print(file)
            os.remove(os.path.join(folderPath, file))


def formatFile(reportdir):

    print("Reformatting the time and date in file name.")

    timeto24hour = [0, 13, 14, 15, 16, 17, 18, 7, 8, 9, 10, 11, 12]

    # Rename files to new format:  (e.g. 1230050-1230049 Downstream 2054 1034 AM.pdf)

    for filename in os.listdir(reportdir):
        spfilename = filename.split(' ')
        if len(spfilename) == 6:
            fileID, fileDirection, fileDate, fileTime = spfilename[0], spfilename[1], spfilename[3].split('_'), \
                                                        spfilename[4].split('_')
            newfileDate = '{0}{1}{2}'.format(fileDate[2], fileDate[0].zfill(2), fileDate[1].zfill(2))
            newfileTime = [str(timeto24hour[int(fileTime[0])]), fileTime[1]]
            fileTimeFormat = '{0}{1}'.format(newfileTime[0], newfileTime[1])
            if fileDirection == '':
                filenameDirection = 'Downstream'
            elif fileDirection == 'True':
                filenameDirection = 'Upstream'
            else:
                filenameDirection = 'Downstream'
            newfilename = '{0} {1} {2} {3} {4}'.format(fileID, filenameDirection, newfileDate, fileTimeFormat, spfilename[5])
            print("New name of file: {} \n".format(newfilename))
            # if newfilename not in os.listdir(reportdir):  # this line slows the renaming ##########
            #     os.rename(reportdir + filename, reportdir + filename.replace(filename, newfilename))
            try:
                oldName = os.path.join(reportdir, filename)
                newName = os.path.join(reportdir, newfilename)
                os.rename(oldName, newName)
            except FileExistsError:
                continue

        else:
            print("{} format is good".format(filename))


def newestFile(reportdir):

    print("Removing older file if newer one exists.")

    # Create dictionary of all the files:
    fileDict = {}
    for filename in os.listdir(reportdir):
        basefilename = os.path.splitext(filename)[0]
        spfilename = basefilename.split(' ')
        fileID = spfilename[0] + ' ' + spfilename[1]
        if fileID in fileDict:
            fileDict[fileID].append(filename)
        else:
            fileDict[fileID] = [filename]

    keepFileGroup = []
    for key, values in fileDict.items():  # 'list' isn't used here because values are not removed from the dictionary
        # if only 1 report is found for a GravityMain ID
        if len(values) == 1:
            if values not in keepFileGroup:
                keepFileGroup.append(values)
        # if more than 1 report is found for a GravityMain ID
        if len(values) > 1:
            timeValues = [0]
            for each in values:
                spvalues = each.split(' ')
                if len(spvalues) == 5:
                    getDates = [int(x) for x in spvalues if x.isdigit()]
                    if getDates[-2] > timeValues[0]:
                        timeValues[0] = getDates[-2]
            print('Latest date: {0}'.format(timeValues[0]))
            removeOldDates = []
            for each in values:
                if len(each.split(' ')) == 2:
                    valueDate = 0
                else:
                    valueDate = each.split(' ')[-3]
                if valueDate != str(timeValues[0]):
                    print('{} out of date'.format(each))
                    removeOldDates.append(each)
            for value in removeOldDates:
                fileDict[key].remove(value)

            timeValues = [0]
            for each in values:
                spvalues = each.split(' ')
                if len(spvalues) == 5:
                    getTimes = [int(x) for x in spvalues if x.isdigit()]
                    if getTimes[-1] > timeValues[0]:
                        timeValues[0] = getTimes[-1]
            print('Latest time: {0}'.format(timeValues[0]))
            removeOldTimes = []
            for each in values:
                if len(each.split(' ')) == 2:
                    valueTime = 0
                else:
                    valueTime = each.split(' ')[-2]
                if valueTime != str(timeValues[0]):
                    print('{} out of date'.format(each))
                    removeOldTimes.append(each)
            for value in removeOldTimes:
                fileDict[key].remove(value)
            if len(values) == 1:
                keepFileGroup.append(values)

    finalFileGroup = [val for sublist in keepFileGroup for val in sublist]

    for filename in os.listdir(reportdir):
        if filename in finalFileGroup:
            print('{} is most recent'.format(filename))
            continue
        else:
            print('{} is outdated and will be removed'.format(filename))
            os.remove(os.path.join(reportdir, filename))

    for filename in os.listdir(reportdir):
        spfilename = filename.split(' ')
        if len(spfilename) == 5:
            fileID = spfilename[0]
            fileDirection = spfilename[1]
            newfilename = '{0} {1}.pdf'.format(fileID, fileDirection)
            try:
                oldName = os.path.join(reportdir, filename)
                newName = os.path.join(reportdir, newfilename)
                os.rename(oldName, newName)
            except FileExistsError:
                continue


def combinePDF(reportdir):

    print("Combining PDF reports if an Upstream and Downstream one exists for same PipeID.")

    fileDict = {}
    for filename in os.listdir(reportdir):
        spfilename = filename.split(' ')
        fileID = spfilename[0]
        if fileID in fileDict:
            fileDict[fileID].append(filename)
        else:
            fileDict[fileID] = [filename]

    os.chdir(reportdir)

    for key, values in list(fileDict.items()):  # "list" is used because values are removed from the dictionary
        direc = ['Downstream.pdf', 'Upstream.pdf', 'Bidirectional.pdf']
        if len(values) == 2:
            if not any(direc[2] in x for x in values):
                pdfList = []
                for pdf in values:
                    if pdf not in pdfList:
                        pdfPath = os.path.join(reportdir, pdf)
                        if pdfPath not in pdfList:
                            pdfList.append(pdfPath)
                try:
                    merger = PdfFileMerger()
                    for each in pdfList:
                        merger.append(each)
                    merger.write(key + ' Bidirectional.pdf')
                    merger.close()
                    for pdf in pdfList:
                        print(pdf)
                        os.remove(pdf)
                except():
                    pass
            elif any(direc[2] in x for x in values):
                pdfList = []
                for pdf in values:
                    if pdf not in pdfList:
                        pdfPath = os.path.join(reportdir, pdf)
                        if pdfPath not in pdfList:
                            pdfList.append(pdfPath)
                for file in pdfList:
                    if 'Bidirectional.pdf' in file:
                        print('Removing "Bidirectional" file to make new one')
                        os.remove(file)

        elif len(values) == 3:
            for each in values:
                if 'Downstream' and 'Upstream' and 'Bidirectional' in each:
                    pdfList = []
                    for pdf in values:
                        if pdf not in pdfList:
                            pdfPath = os.path.join(reportdir, pdf)
                            if pdfPath not in pdfList:
                                pdfList.append(pdfPath)
                    for file in pdfList:
                        if 'Bidirectional.pdf' in file:
                            print('Removing "Bidirectional" file to make new one')
                            os.remove(file)
                            pdfList.remove(file)
                    try:
                        merger = PdfFileMerger()
                        for each1 in pdfList:
                            merger.append(each1)
                        merger.write(key + ' Bidirectional.pdf')
                        merger.close()
                        for pdf in pdfList:
                            # print(pdf)
                            os.remove(pdf)
                    except():
                        pass


if __name__ == '__main__':

    # folderPath = r'W:\GIS\WORKING FILES\EM Working Files\Python Projects\rename files test\yes'
    folderPath = 'W:\\GIS\\Reports\\GNet Mainline Inspections\\'
    os.chdir(folderPath)

    startTime = datetime.now()

    deleteCopies(folderPath)
    formatFile(folderPath)
    newestFile(folderPath)
    combinePDF(folderPath)
    print("Code completion time: {}".format(datetime.now() - startTime))
