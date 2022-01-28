# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 10:31:46 2022
script name:shapefileInventory.py
input: <directory path>
output: two text file reports "fileList_[directory_name].txt" and "report_[directory_name].txt"

description: This script creates an inventory of files and field names for
shapefiles in a folder.
It also:
-checks file extensions to ensure that all required and recommended files
    are present
-determines whether the shapefiles have the same spatial reference
-flags shapefiles that are corrupt or cannot be opened

last modified: January 2022

@author: Melinda Kernik
inspiration from a script shared by Kim Durante for a 2017 FOSS4G geospatial metadata workshop
"""

##import necessary modules and return a message if any are not available
try:
    import os
    import sys
    #import math
    from osgeo import ogr
    from datetime import datetime
    from pathlib import Path
    from collections import Counter

except Exception as e:
    print(e)


def listShapefiles(inputDirectory):
    """Create a dictionary of shapefiles in a folder. The function looks for
    '.shp' extensions; if that file is missing, the script will not notice other
    shapefile components.

     Parameters
     ----------
     inputDirectory : path to folder with shapefiles

     Returns
     -------
     shp_files : dictionary with shapefile stem (key): list of component
         file extensions (value)
    """
    os.chdir(inputDirectory)
    entries = Path.cwd()


    shps = []
    shp_files = {}

    for entry in entries.iterdir():
        if entry.suffix == ".shp":
            shps.append(entry.stem)

    for shp in shps:
        sub_files = []
        for entry in entries.iterdir():
            #written this way to also match with ".shp.xml" files
            if entry.stem == shp or entry.stem == shp + ".shp":
                sub_files.append((entry.suffix).lower())
        sub_files.sort()
        shp_files[shp] = sub_files
    return shp_files


def componentCheck(fileList):
    """Check a list of file extensions against the required and recommended
    files that make up a shapefile.

    Parameters
    ----------
    fileList : list of shapefile file extensions

    Returns
    -------
    required : list of missing required files (if any)
    recommended : list of missing recommended files (if any)
    file_details : (string) description of missing required or recommended
        files for use in the curation report

    """
    required_exts = [".shp", ".dbf", ".shx",]
    recommended_exts = [".prj", ".xml"]

    required = list(set(required_exts) - set(fileList))
    recommended = list(set(recommended_exts) - set(fileList))

    file_details = ""
    if required:
        file_details = file_details + "Missing required file(s):" + str(*required) + "\n"
    if recommended:
        file_details = file_details + "Missing recommended file(s)\n"
        if ".prj" in recommended:
            file_details = file_details + " .prj (coordinate system/projection information)\n"
        if ".xml" in recommended:
            file_details = file_details + " .shp.xml (metadata)\n"
        file_details = file_details + "\n"
    if not required and not recommended:
        file_details = file_details + "All required and recommended files are present."

    return required, recommended, file_details


def fieldsInfo (dataSource):
    """Return information about the geometry type and fields of a shapefile. If
    the function is unable to access the requested information it will return an
    empty list instead.

    Parameters
    ----------
    dataSource : an object creating by opening a shp file with the ogr library

    Returns
    -------
    fieldDetails : (list) [
        shapefile geometry type[0],
        number of features[1],
        number of fields[2],
        field list[3] -- tuples with (field name[0], field type[1])]
    """

    fields = []
    fieldDetails = []
    try:
        for lyr in dataSource:
            lyr_defn = lyr.GetLayerDefn()
            for i in range(lyr_defn.GetFieldCount()):
                field_defn = lyr_defn.GetFieldDefn(i)
                fields.append((field_defn.GetName(), field_defn.GetFieldTypeName(field_defn.GetType())))
        fieldDetails = [str(ogr.GeometryTypeToName(lyr.GetGeomType())), str(lyr.GetFeatureCount()), str(len(fields)), fields]
    except:
        pass
    return fieldDetails


def srsDetails(dataSource):
    """Return information about the coordinate system/projection of a shapefile.
    If the function is unable to access the requested information it will return
    an empty string instead.

    Parameters
    ----------
    dataSource : an object creating by opening a shp file with the ogr library

    Returns
    -------
    srsInfo : (string) the projection name or geographic coordinate system
    (if the shapefile is not projected), followed by the EPSG code (if available)

    """
    srsInfo = ""
    try:
        for lyr in dataSource:
            srs = lyr.GetSpatialRef()
            if srs.GetAttrValue('projcs'):
                srsInfo = srsInfo + srs.GetAttrValue('projcs')
            else:
                srsInfo = srsInfo + srs.GetAttrValue('geogcs')
            if srs.GetAttrValue("AUTHORITY"):
                srsInfo = srsInfo + " -- " + srs.GetAttrValue("AUTHORITY",0) + ": " + srs.GetAttrValue("AUTHORITY",1)
    except:
        pass
    return srsInfo


def sameDictValues (dictionary):
    """Return whether all of the values in a dictionary are the same """

    same = True

    # extract one value from the dictionary to compare to the others
    test_val = list(dictionary.values())[0]

    #if any of the values do not match, change the boolean value to False
    for key in dictionary:
        if dictionary[key] != test_val:
            same = False
            break
    return same


def listToString(li):
    """Convert a list to a string, adding commas between list elements"""

    str1 = ", "

    return (str1.join(li))


def stringToList(string):
    """Convert a string to a list, splitting using commas and removing spaces"""

    li = list((string.replace(" ", "")).split(","))
    return li


# def convert_size(size_bytes):
#     """Convert file size in bytes to a more human readable format"""

#     if size_bytes == 0:
#         return "0B"
#     size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
#     i = int(math.floor(math.log(size_bytes, 1024)))
#     p = math.pow(1024, i)
#     s = round(size_bytes / p, 2)
#     return "%s %s" % (s, size_name[i])


#Main
args = sys.argv

#Set a directory/folder
inputDirectory = args[1]

#Check that the folder exists.  If not, stop the script
if os.path.isdir(inputDirectory):
    pass
else:
    print("Cannot access the folder: " + inputDirectory + ". Please check the file path. No report will be generated. ")
    raise SystemExit(0)

#Create a dictionary of shapefiles in the folder with file name (key): extensions (value)
shp_files = listShapefiles(inputDirectory)
print ("This folder has " + str(len(shp_files)) + " shapefiles.")

#If there are no shapefiles (ie. ".shp" files) in the folder, stop the script
if not shp_files:
    print ("Did not find any shapefiles in the folder: " + inputDirectory + ". No report will be generated.")
    raise SystemExit(0)

#Create empty dictionaries and lists to store information about the shapefiles
shp_fields = {}
projection = {}
no_projection = []
missing_required = {}
broken_shp = []

#If a shapefile is missing required files, add it to a dictionary of problematic
#shapefiles and remove it from the main list
for shp in list(shp_files.keys()):
    essential = []
    if ".shx" not in shp_files[shp]:
        essential.append(".shx")
    if ".dbf" not in shp_files[shp]:
        essential.append(".dbf")
    if essential:
        missing_required[shp] = essential
        shp_files.pop(shp)
        print ("Missing required files for: " + shp)
        continue

#Loop through the valid shapefiles, opening them and gathering information
    path = inputDirectory + "/" + shp + ".shp"
    dataSource = ogr.Open(path)

    #If unable to open a shapefile, remove it from the main list
    if dataSource is None:
        print ("Could not open " + shp + ". It may be corrupt.")
        broken_shp.append(shp)
        shp_files.pop(shp)
        continue

    #Collect information about the fields
    else:
        fieldsDetails = fieldsInfo(dataSource)
        if fieldsDetails:
            shp_fields [shp] = fieldsDetails
        else:
            print ("Unable to obtain information about fields for " + shp + ".  It may be corrupt.")
            if shp not in broken_shp:
                broken_shp.append(shp)
            pass

    #Collect information about the spatial reference. If there isn't one,
    #(ie. no .prj file or it is incorrectly formatted), add it to a no_projection list
        srsInfo = srsDetails(dataSource)
        if srsInfo:
            projection[shp] = srsInfo
        else:
            no_projection.append(shp)
            pass

#Write an inventory of shapefiles and their fields. Formatting reflects a readme
#template used by several academic data repositories including the Data Repository
#at the University of Minnesota (DRUM)
if shp_fields:
    fileList_path = inputDirectory + "/fileList_" + Path(inputDirectory).stem + ".txt"
    f = open(fileList_path ,'w')
    f.write ("Input folder: "+ inputDirectory + "\n")
    f.write ("Date: "+ datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "\n\n")

    f.write ("File List" + "\n")
    #List each shapefile in the folder with geometry type and associated file extensions
    for i, shp in enumerate(shp_files, start=1):
        f.write ("\t" + str(i) + ". Filename: " + shp + " (" + shp_fields[shp][0] + ") (")
        for x in range(len(shp_files[shp])):
            f.write (shp_files[shp][x] + " ")
        f.write (")\n\tShort description:\n\n" )

    #List the fields in each shapefile (+ number of features and field type)
    for shp in shp_fields:
        f.write("-----------------------------------------\nDATA-SPECIFIC INFORMATION FOR: " + shp + "\n-----------------------------------------\n")
        f.write("A. Number of features:  %s" % shp_fields[shp][1] + "\n")
        f.write("B. Number of fields: " + shp_fields[shp][2] + "\n")
        f.write("C. Field list\n")
        for i, field in enumerate(shp_fields[shp][3], start=1):
            f.write ("\t" + str(i) + ". Name: " + field[0] + " (" + field[1] + ")\n\tDescription:\n\n")

    f.close()

else:
    print ("There are no shapefiles with valid fields in this folder. No file list will be created.")


#Write a report about corrupt/broken shapefiles, file extensions, and
#coordinate systems/projections
report_path = inputDirectory + "/report_" + Path(inputDirectory).stem + ".txt"
f = open(report_path ,'w')
f.write ("Input folder: "+ inputDirectory + "\n")
f.write ("Date: "+ datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "\n\n")

#List how many valid shapefiles are in the folder as well as any that can't
#be opened
f.write("This folder has " + str(len(shp_files)) + " valid shapefiles.\n\n")

if missing_required:
    f.write("The following shapefile(s) are missing required files and cannot be opened:\n")
    for k,v in missing_required.items():
        f.write(k + " (" + listToString(v) +")\n")
    f.write("\n")

corrupt = list(set(broken_shp) - set(missing_required))
if corrupt:
    f.write("The following shapefile(s) have the required files, but cannot be opened and may be corrupt:\n")
    for shp in corrupt:
        f.write(shp + "\n")
    f.write("\n")


#Compare and inventory file extensions of shapefiles in the folder
f.write("------\nFile Extensions\n------\n\n")

#Check if shapefiles have the same set of file extensions
if shp_files:
    #If shapefiles in the folder have the same set of files, report
    #what they are and whether all recommended and required values are present
    if sameDictValues(shp_files):
        extensions = list(shp_files.values())[0]
        if len(shp_files) == 1:
            f.write("The shapefile in this folder includes the files: ")
        else:
            f.write("The shapefiles in this folder have the same component files: ")
        for ext in extensions:
            f.write(ext + " ")
        f.write("\n")
        required, recommended, file_details = componentCheck(extensions)
        f.write(file_details + "\n")

    #If the shapefiles do not have the same set of files, find which set is most
    #common. Check whether all recommended and required values are present.
    else:
        f.write("The shapefiles in this folder do not have the same component files.\n\n")
        all_values = [listToString(list) for list in shp_files.values()]
        most_common = Counter(all_values).most_common(1)[0]
        f.write ("The most common set of files is: " + most_common[0] + "\n")
        required, recommended, file_details = componentCheck(stringToList(most_common[0]))
        f.write(file_details)
        f.write("\n" + str(most_common[1]) + " shapefile(s) with this set.\n")
        ##Uncomment this section to print a list of shapefiles with the most common set of files.
        # for key in shp_files:
        #     if listToString(shp_files[key]) == most_common[0]:
        #         f.write(key + "\n")
        f.write("\n")

        #Compare all other sets of files to the most common grouping. Identify
        #files that are "missing" or "extra" as compared to the most common grouping
        #Report these along with the shapefiles that have these less common sets
        #of files
        for exts, num in Counter(all_values).items():
            if exts != most_common[0]:
                extra = list(set(stringToList(exts)) - set(stringToList(most_common[0])))
                missing =  list(set(stringToList(most_common[0])) - set(stringToList(exts)))
                if missing and not extra:
                    f.write(str(num) + " shapefile(s) with " + str(len(missing)) + " missing file(s): " + listToString(missing) +"\n")
                elif extra and not missing:
                    f.write(str(num) + " shapefile(s) with " + str(len(extra)) + " additional file(s):" + listToString(extra) + "\n")
                elif extra and missing:
                    f.write (str(num) + " shapefile(s) with " + str(len(missing)) + " missing file(s) (" + listToString(missing) + ") and "+ str(len(extra)) + " additional file(s) (" + listToString(extra) + ")\n")
                for key in shp_files:
                        if listToString(shp_files[key]) == exts:
                            f.write(key + "\n")
                f.write("\n")

f.write("------\nProjections\n------\n\n")

#Check if any of the shapefiles have spatial reference
if projection:
    #If shapefiles in the folder have the same spatial reference, report it.
    if sameDictValues(projection):
        srsDetails = list(projection.values())[0]
        if len(shp_files) == 1:
            f.write("The shapefile in this folder is in the coordinate system/projection:\n" + srsDetails + "\n\n")
        else:
            f.write("The shapefiles in this folder are in the same coordinate system/projection:\n" + srsDetails + "\n\n")

    #If the shapefiles do not have the same spatial reference, find which is most
    #common and report it.
    else:
        f.write("The shapefiles in this folder are not in the same coordinate system/projection.\n\n")
        all_values = [listToString(list) for list in shp_files.values()]
        most_common_prj = Counter(projection.values()).most_common(1)[0]
        f.write("The most common coordinate system/projection is: " + most_common_prj[0] + ("\n" + str(most_common_prj[1]) + " shapefile(s) have this spatial reference.\n\n"))

        #Report the number of shapefiles with other spatial references and list them
        for proj, num in Counter(projection.values()).items():
            if proj != most_common_prj[0]:
                f.write((str(num) + " shapefile(s) with the coordinate system/projection: " + proj + "\n"))
                for k, v in projection.items():
                    if projection[k] == proj:
                        f.write(k + "\n")
                f.write("\n")

#Report shapefiles with no spatial reference.
if no_projection:
    if len(no_projection) == len(shp_files):
        f.write("The spatial reference has not been defined for the shapefile(s) in this folder.\n")
    else:
        f.write("The spatial reference is not defined for the following shapefiles:\n")
        for s in no_projection:
            f.write(s + "\n")
f.write("\n")


## Uncomment (along with the convert_size function) to list the sum file size of
## each shapefile's component parts.

# f.write("------\nFile List\n------\n\n")
# for shp in shp_files:
#     shape_size = 0
#     for item in shp_files[shp]:
#         path = inputDirectory + "/" + shp + item
#         shape_size += os.path.getsize(path)
#     f.write(shp + ": " + convert_size(shape_size) + "\n")

print ("Script complete!")

f.close()
