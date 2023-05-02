# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 15:31:34 2021
script Name:GeodatabaseToShapefileWarnings.py
input: <geodatabase pathname>
output: text file report "warning_report_[geodatabase_stem]"

description: This script tool examines feature classes in input geodatabases for 
characteristics that could cause problems if it were transformed into a 
shapefile including:
-large file sizes (more than 255 fields or over 2GB)
-field names longer than 10 characters
-string fields longer than 254 characters
-date fields with time values
-NULL values
-BLOB, guid, global id, or raster field types 
-attribute domains or subtypes
-annotation or topology

last modified: May 2023
author: Melinda Kernik
"""

##import necessary modules and return a message if any are not available
try:  
    import arcpy
    import os
    import math
    from string import Template
    from collections import Counter, OrderedDict
    from pathlib import Path
except Exception as e:
    arcpy.AddMessage(str(e))


def GeodatabaseContent (geodatabase):
    """
    Returns information about the contents of a geodatabase with feature classes
    in one dictionary (ordered alphabetically) and all other data types in another.

    Parameters
    ----------
    geodatabase : geodatabase file path

    Returns
    -------
    feature_classes: dictionary of feature classes with name (key), 
        absolute path (value) (Note: annotation layers have been removed)
    other_data_types: dictionary of the non-feature class data layers with 
        layer name (key), type of data (value)
    """
    arcpy.env.workspace = geodatabase

    feature_classes = {}
    other_data_types = {}
    
    #Inspect the data types of the data layers in a geodatabase (ie it's "children")
    #If the layer is a feature class (but not annotation) add it to a dictionary of 
    #feature classes. Otherwise add it to a dictionary with other data types
    desc_gdb = arcpy.Describe(geodatabase)
    for child in desc_gdb.children:
        if child.dataType == "FeatureClass":
            if child.featureType == "Annotation":
                other_data_types[child.name] = "Annotation"
            else:
                feature_classes[child.name] = child.catalogPath
        
        #If there are any FeatureDatasets, inspect their nested data layers
        elif child.dataType == "FeatureDataset":
            desc_fd = arcpy.Describe(child.catalogPath)
            for child_sub in desc_fd.children:
                if child_sub.dataType == "FeatureClass":
                    if child_sub.featureType == "Annotation":
                        other_data_types[child_sub.name] = "Annotation"
                    else:
                        feature_classes[child.name + "/" + child_sub.name] = child_sub.catalogPath
                else:
                    other_data_types[child_sub.name] = child_sub.dataType 
        else:
            other_data_types[child.name] = child.dataType
     
    #return feature classes sorted alphabetically
    return OrderedDict(sorted(feature_classes.items(), key=lambda t: t[0].lower())), other_data_types


def FieldList(feature_classes):
    """ Return a dictionary of field names. This function is used in the script 
    to check that feature classes have fields, but less than 255 (the max 
    allowed in shapefiles).
    
    Parameters
    ----------
    feature_classes: dictionary of feature classes with name (key), 
        absolute path (value)

    Returns
    -------
    field_dict : dictionary with absolute path to a feature class (key): 
        list of field names (value)
    """
       
    field_dict = {}
    for k,v in feature_classes.items():
        field_names = [f.name for f in arcpy.ListFields(v)]
        field_dict[v] = (field_names)
    return field_dict


def get_size(start_path = '.'):
    """"Calculate total size of all files in a directory, including sub-directories."""
    
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


def convert_size(size_bytes):
    """Convert file size in bytes to a more human readable format"""

    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def TruncatedFields (fc):
    """Check for field names that are longer than 10 characters 
    and for field names with the same first 10 characters   

    Parameters
    ----------
    fc : absolute path to the feature class

    Returns
    -------
    trunc_names : dictionary of field names that are longer than 10 characters 
     with full field name (key): first 10 characters of field name (value)
    duplicate_names : list of field names with the same first 10 characters
    """
     
    field_names = arcpy.ListFields(fc)
    trunc_names = {}
    ten_character = []
    duplicate_names = []
    for field in field_names:
        #Skip "shape_length" because it is a field that is generated for all 
        #geodatabase line and polygon feature classes. 
        if field.name.lower() != "shape_length" and len(field.name) >= 10:    
            #Check if shortened field name matches other shortened field names
            if field.name[:10] in trunc_names.values():
                if field.name [:10] not in duplicate_names:
                    duplicate_names.append(field.name[:10])
            #Check if shortened field name matches existing field names
            if field.name[:10] in ten_character:
                if field.name [:10] not in duplicate_names:
                    duplicate_names.append(field.name[:10])
            if len(field.name) == 10:
                ten_character.append(field.name)
            else:
                trunc_names[field.name] = (field.name[:10])
    return trunc_names, duplicate_names



def StringFieldLength (fc):
    """Check for string fields that have more than 254 characters
  
    Parameters
    ----------
    fc : absolute path to the feature class

    Returns
    -------
    string_fields : list of string fields with maximum character limits greater
        than 254
    longFieldsDict : dictionary of string fields that actually contain text
        longer than 254 characters with field name(key): number of rows with
        long text in that field (value) 
    """

    field_names = arcpy.ListFields(fc)
    
    string_fields = []
    longFieldsDict = {}
    for field in field_names:
        if format(field.type) == "String" and int(format(field.length)) > 254:
            string_fields.append(field.name)
            #If the field has a string format and is longer than 254 characters,
            #search through each row of the field to see whether any of the values
            #are actually longer than 254 characters
            with arcpy.da.SearchCursor(fc, field.name) as cursor:  
                longFields = []
                for row in cursor:  
                    if row[0] != None and len(row[0]) > 254:
                        longFields.append(row[0])                       
            if longFields:
                longFieldsDict[field.name] = longFields
            del cursor  
    return string_fields, longFieldsDict




def DateFieldLength (fc):
    """Check for date fields that have specific time values (hours minutes 
        seconds that are not 00:00:00)
  
    Parameters
    ----------
    fc : absolute path to the feature class

    Returns
    -------
    date_fields : dictionary of date fields storing times (H:M:S) with 
        field name(key): number of rows with specific times (not 00:00:00) 
        in that field (value).
    """

    field_names = arcpy.ListFields(fc)
    
    date_fields = {}
    for field in field_names:
        #If the field has a date format, search its rows to see whether 
        #any have a time value other than None or 00:00:00 
        if format(field.type) == "Date":
            with arcpy.da.SearchCursor(fc, field.name) as cursor:  
                timeField = []
                for row in cursor:  
                    if row[0] != None:
                        row = str(row[0]).split(" ").pop(1)
                        if row != "00:00:00":
                            timeField.append(row[0])
                        #break
                if timeField:
                    date_fields[field.name] = len(timeField)
            del cursor

    return date_fields

    
def NULL_values(fc):    
    """Check fields for NULL values. 

    Parameters
    ----------
    fc : absolute path to the feature class

    Returns
    -------
    NULL_fields : list of fields that contain NULL values
    """
    field_names = arcpy.ListFields(fc)
    NULL_fields = {}
    
    for field in field_names:
        #Skip over "Raster" field types because they cause errors
        if format(field.type) != "Raster":
            with arcpy.da.SearchCursor(fc, field.name) as cursor:  
                for row in cursor:  
                    if row[0] == None:
                        NULL_fields[field.name] = field.type
                        break     
            del cursor
       
    return NULL_fields


def unsupportedFieldTypes (fc):
    """Check for geodatabase field type options that aren't supported in 
        shapefiles (BLOB, guid, global id, and raster)

    Parameters
    ----------
    fc : absolute path to the feature class

    Returns
    -------
    unsupported_fields : a dictionary of unsupported fields with 
        field name (key): field type (value)
    """
    unsupported_types = ["Blob", "Guid", "GlobalID", "Raster"]
    unsupported_fields = {}
    fields = arcpy.ListFields(fc)
    for field in fields:
        if field.type in unsupported_types:
            unsupported_fields[field.name] = field.type
    return unsupported_fields


def AttributeDomains (fc):
    """Check for fields formatted with attribute domains

    Parameters
    ----------
    fc : absolute path to the feature class

    Returns
    -------
    domain_fields : list of fields that contain attribute domains
    """
    
    field_names = arcpy.ListFields(fc)
    domain_fields = {}
    for field in field_names:
        if len(field.domain) > 0:
            domain_fields[format(field.name)] = format(field.domain)
    return domain_fields


def SubtypeFields(fc):
    """Check for fields formatted with subtypes
    
    Parameters
    ----------
    fc : absolute path to the feature class
    
    Returns
    -------
    subtype_fields : list of fields that contain subtypes

    """
    subtypes = arcpy.da.ListSubtypes(fc)
    subtype_fields = []
    #For fields that don't have subtypes, "SubtypeField" is undefined. If it is
    #defined, add the field name to the list of subtype fields.
    for stcode, stdict in list(subtypes.items()):      
        for stkey in list(stdict.keys()):
            if stkey == 'SubtypeField':
                if stdict[stkey]:
                    if stdict[stkey] not in subtype_fields:
                        subtype_fields.append(stdict[stkey])
                else:
                    pass
            
    return subtype_fields


def FeaturesExist (feature_classes):
    """ Check whether there are any feature classes in the geodatabase and if
    those features classes have fields

    Parameters
    ----------
    fcs : list of feature classes in the geodatabase

    Returns
    -------
    bool
        True: If there are any feature classes with fields
        False: If there are no feature classes in the list or if none of the 
        feature classes have fields 

    """
    if feature_classes:
        for name, fc in feature_classes.items():
            field_names = [f.name for f in arcpy.ListFields(fc)]
            if any(field_names):
                return True
            else:
                return False
    else:
        return False
   

###Get path to geodatabase or multiple geodatabases
for gdb in arcpy.GetParameterAsText(0).split(";"):
    
    #Set up a counter for number of features checked, number of warnings found, and a warning summary list
    count = 0
    warning_count = 0 
    warning_list = []
    no_features =[]
    
    arcpy.AddMessage("Processing:" + gdb)
    geodatabase = gdb

    #Make sure the path to the geodatabase exists.  Stop the script if the directory cannot be found.
    if os.path.isdir(geodatabase):
        pass
    else:
        arcpy.AddMessage("Cannot access the geodatabase: " + Path(geodatabase).stem + ". Please check the file path. No report will be generated. ")
        continue
    
    #Set the path for the warning report
    report_path = os.path.dirname(geodatabase) + "/warning_report_" + Path(geodatabase).stem + ".txt"
    
        
    #Inspect the content of the geodatabase.
    feature_classes, other_data_types = GeodatabaseContent(geodatabase)
    
    #If none of the data layers are feature classes or there are no data layers, stop the script. 
    if feature_classes:
        #print (feature_classes.keys())
        pass
    elif other_data_types:
        arcpy.AddMessage ("There are data layers in " + Path(geodatabase).stem + " but none of them are feature classes. No report will be generated.")
        continue
    else:
        arcpy.AddMessage ("The script found no data layers in " + Path(geodatabase).stem + ". The geodatabase may be empty or corrupted. No report will be generated.")
        continue


    #Check if there are any valid feature classes in the geodatabase (items in the dictionary with field name values). If not, stop the script.
    if FeaturesExist(feature_classes):
        pass
    else:
        arcpy.AddMessage ("There are no valid feature classes in " + Path(geodatabase).stem + "! No report will be generated.")
        continue
    
    
    #Open a text file in which to write the warning report and add a header
    f = open(report_path,"w") 
    f.write("**********************************************\n\nThe geodatabase includes the following feature classes:\n")

    #Write a list of the feature classes in the geodatabase.  If a feature class has no fields (is empty or corrupt), note that and remove it from the list of feature classes
    field_dict = FieldList(feature_classes)
    for name, fc in feature_classes.items():
        if field_dict[fc]:
            f.write( "  " + name + "\n")
        else:
            arcpy.AddMessage ("The feature class (" + name + ") has no fields! It may be corrupt or empty and will be skipped by the rest of the script")
            f.write(fc + " ***Empty or corrupt feature class - not included in report below ***")
            feature_classes.pop(name)

    #Write a list of other types of data included in the geodatabase, including warnings if there are any annotation or topology layers             
    if other_data_types:
        f.write("\nIt also contains " + str(len(other_data_types)) + " other data layers, including: \n")
        for k,v in Counter(other_data_types.values()).items():
            if k == "Table":
                f.write("  " + str(v) + " table(s)\n")
            elif k == "RasterDataset":
                f.write("  " + str(v) + " raster(s)\n")
            elif k == "Topology":
                f.write("  " + str(v) + " topology layer(s) **WARNING: Functionality is lost when converting topology layers into shapefiles**\n")
                warning_count +=1
                warning_list.append("Topology")
            elif k == "Annotation":
                f.write("  " + str(v) + " annotation layer(s) **WARNING: Functionality is lost when converting annotation layers into shapefiles**\n")
                warning_count +=1
                warning_list.append("Annotation")
            else:
                f.write("  " + str(v) + " " + k + " layer(s)\n" )
    

    #Check the file size of the geodatabase and report it in a human-readable format. Add a warning if it is larger than 2GB.
    gdb_size = get_size(geodatabase)
    if gdb_size > 2147483648:
        f.write("\nWARNING: There is a 2GB size limit for any shapefile component file. The overall file size of the geodatabase is " + convert_size(gdb_size) + ". Check to see whether any of the components within the geodatabase exceed 2GB before transforming or data will be lost!")
        warning_count +=1
        warning_list.append("Overall file size")
    else:
        f.write("\nThe file size of the geodatabase is " + convert_size(gdb_size) + ".\n")

    f.write("\n ********************************************** \n\n\n")
    
    #Loop through the feature classes, creating a summary dictionary with the name 
    #of the potential issue (key): warning status (value)--> "Warning", "Ok", or 
    #"Not determined." If a warning is generated, append a more detailed description of
    #the issue and affected fields to the end of the "details" string. Once all
    #potential issues have been checked, write the summary and details (if any) to
    #a text file report.
    
    for name, fc in feature_classes.items():
        warning = False
        count += 1
        summary_dict = {}
        summary_dict ["name"] = name
        details = "\nMore detailed description of warnings:"
        
    ###Data loss
        #Check that the number of fields in the feature class does not exceed 255
        if field_dict[fc]:
            if len(field_dict[fc]) > 255:
                warning = True
                warning_list.append("Number of fields")
                summary_dict["field_number"] = "Warning"
                details = details + "\n\nWARNING: The maximum number of fields a shapefiles can have is 255. If this limit is exceeded only the first 255 fields will be used. There are " + str(len(field_dict[fc])) + " fields.\n"
            else:
                summary_dict["field_number"] = "Ok"
        else:
            arcpy.AddMessage ("WARNING: The feature class (" + name + ") has no fields!" )
            summary_dict["field_number"] = "No fields exist"
        
        
        #Check for field names that are longer than 10 characters and for 
        #field names with the same first 10 characters
        try:
            trunc_names, duplicate_names = TruncatedFields(fc)
            if trunc_names: 
                warning = True
                warning_list.append("Field name character length")
                summary_dict["short_names"] = "Warning"
                details = details + "\n\nWARNING: Shapefile field names cannot be longer than 10 characters. Only the first 10 characters will be used for field names that exceed this length. \n\nThere are " + str(len(trunc_names)) + " field names that will be truncated:\n"
                for field in trunc_names:
                    details = details + "  " + field + ",   truncated field name: " + field[:10] + "\n"
                if duplicate_names:
                    warning_list.append("Multiple fields with the same shortened name")
                    details = details + (" \nWARNING: Multiple fields will have the same shortened name: \n")
                    for field in duplicate_names:
                        details = details + "  " + field +"\n"
            else:
                summary_dict["short_names"] = "Ok"
        except Exception as e:
            summary_dict["short_names"] = "Not determined"
            arcpy.AddMessage  ("Could not run TruncatedFields function for " + name + " (" + str(e) + ")")
        
    
        #Check for string fields that have more than 254 characters
        try:
            string_fields, long_fields_dict = StringFieldLength(fc)             
            if long_fields_dict: 
                warning = True
                warning_list.append("String field length")
                summary_dict["long_fields"] = "Warning"
                details = details + "\n\nWARNING: Shapefile text/string fields are limited to 254 characters. Only the first 254 characters will be use for text fields that exceed this length. \n\nThere are " + str(len(long_fields_dict)) + " fields in which data will be lost:\n"
                for key, value in long_fields_dict.items():
                    details = details + "  " + key + " contains " + str(len(long_fields_dict[key])) + " rows whose string field length exceeds 254 characters.\n"
            # elif string_fields:
            #     summary_dict["string_fields"] = "Partial Warning"  
            #     details = details + "\nWARNING: There are" + str(len(string_fields)) + " where the maximum character limit exceeds 254 characters. None of the fields contain values exceeding this length, but after conversion the fields will be limited to 254 characters."
            else:
                summary_dict["long_fields"] = "Ok"
        except Exception as e:
            summary_dict["long_fields"] = "Not determined"
            arcpy.AddMessage  ("Could not run StringFieldLength function for " + name + " (" + str(e) + ")")
        
        #Check for date fields that have specific time values (hours minutes 
        #seconds that are not 00:00:00)
        try:
            date_fields = DateFieldLength(fc)           
            if date_fields:
                warning = True
                warning_list.append("Date fields with time")
                summary_dict["date_fields"] = "Warning"
                details = details + "\n\nWARNING: Shapefile date fields can hold only dates (MM/DD/YYYY), not time (H:M:S).\n\nData will be lost in " + str(len(date_fields)) + " field(s):\n"
                for key, value in date_fields.items():
                    details = details + "  " + key + " (" + str(date_fields[key]) + " rows)\n"
            else:
                summary_dict["date_fields"] = "Ok"
        except Exception as e:
            summary_dict["date_fields"] = "Not determined"
            arcpy.AddMessage  ("Could not run DateFieldLength function for " + name + " (" + str(e) + ")")
        

        ###Values changed
        #Check for fields with NULL values.
        try:
            NULL_fields = NULL_values(fc)
            if NULL_fields: 
                warning = True
                warning_list.append("Null values")
                summary_dict["null_values"] = "Warning"
                details = details + "\n\nWARNING: Null values are not supported in shapefiles. They will be converted to other values depending on the field type (string -->'', dates --> '0', etc). \n\nThere are NULL values in " + str(len(NULL_fields)) + " field(s):\n"
                for k,v in NULL_fields.items():
                    details = details + "  "+ k +" ("+ v + ")"+"\n"
            else:
                summary_dict["null_values"] = "Ok"
        except Exception as e:
            summary_dict["null_values"] = "Not determined"
            arcpy.AddMessage  ("Could not run NULL_values function for " + name + " (" + str(e) + ")")

        #Check for geodatabase field type options that are not supported in shapefile
        try:
            unsupported_fields = unsupportedFieldTypes (fc)
            if unsupported_fields:
                warning = True
                warning_list.append("Unsupported field types")
                summary_dict["unsupported_fields"] = "Warning"
                unsupported_types = {"Blob": " BLOB field(s) - BLOB fields will be removed if the feature class is converted to shapefile:\n", 
                                     "Raster": " raster field - The field will be removed if the feature class is converted to shapefile:\n",
                                     "Guid": " guid field(s) - These fields will be converted to text and lose functionality:\n", 
                                     "GlobalID":" global id field -The field will be converted to text and lose functionality:\n" , 
                                     }
                details = details + "\n\nWARNING Shapefiles do not support blob, guid, global ID, or raster field types.\n\n" + str(len(unsupported_fields)) + " field(s) will be impacted:\n"
                for fieldtype in unsupported_types.keys(): 
                    if fieldtype in unsupported_fields.values():       
                        uns_fields = [key for key, value in unsupported_fields.items() if value == fieldtype]
                        details = details + str(len(uns_fields)) + unsupported_types[fieldtype]
                        for field in uns_fields:
                            details = details + "  " + field + "\n"
            else:
                summary_dict["unsupported_fields"] = "Ok"
        except Exception as e:
            summary_dict["unsupported_types"] = "Not determined"
            arcpy.AddMessage  ("Could not run unsupportedFieldTypes function for " + name + " (" + str(e) + ")")
    


    ###Functionality loss    
        #Check for fields formatted with attribute domains
        try:
            domain_fields = AttributeDomains(fc)
            if domain_fields: 
                warning = True
                warning_list.append("Attribute domains")
                summary_dict["attribute_domain"] = "Warning"
                details = details + "\n\nWARNING: Attribute domains are not supported in shapefiles.\n\nThere are " + str(len(domain_fields)) + " fields with attribute domains:\n"
                for key, value in domain_fields.items():
                    details = details + "  Field name: " + key + "   Domain: " + value + "\n"
            else:
                summary_dict["attribute_domain"] = "Ok"
        except Exception as e:
            summary_dict["attribute_domain"] = "Not determined"
            arcpy.AddMessage  ("Could not run AttributeDomains function for " + name + " (" + str(e) + ")")
        
    
        #Check for fields formatted with subtypes
        try:
            subtype_fields = SubtypeFields(fc)
            if subtype_fields: 
                warning = True
                warning_list.append("Subtypes")
                summary_dict["subtype_fields"] = "Warning"
                details = details + "\n\nWARNING: Subtypes are not supported in shapefiles.\n\n"+ str(len(subtype_fields)) + " field(s) has subtypes:\n"
                for subtype in subtype_fields:
                    details = details + "  Field name: " + subtype + "\n"
            else:
                summary_dict["subtype_fields"] = "Ok"
        except Exception as e:
            summary_dict["subtype_fields"] = "Not determined"
            arcpy.AddMessage  ("Could not run SubtypeFields function for " + name + " (" + str(e) + ")")
        
        
        #Check that features are present. Since this does not cause data or functionality loss upon conversion to shapefile,
        #Saves featureless layers to a separate list to be included in the summary but not the layer specific warnings
        try:
           #arcpy.GetCount_management returns type "Result", declare field type to identify match
            if str(arcpy.GetCount_management(fc)) == str(0):
               no_features.append(name)
        except Exception as e:
            arcpy.AddMessage  ("Could not determine number of features for " + name + " (" + str(e) + ")")
        
            
        #Write a summary of the warnings about the feature class 
        #Potential issue = "Warning"; No issue found = "Ok"; Unable to run the function = "Not determined."
        if warning == True:
            warning_count += 1
            report_template = Template("-------------------------------\nSummary of warnings for ${name}:\n-------------------------------\n  Number of fields: ${field_number}\n  Field name character length: ${short_names}\n  String field length: ${long_fields}\n  Date fields with time: ${date_fields}\n  NULL values: ${null_values}\n  Unsupported field types: ${unsupported_fields}\n  Attribute domains: ${attribute_domain}\n  Subtypes: ${subtype_fields}\n")
            summary = report_template.substitute(summary_dict)    
            f.write(summary)
            f.write("\n")
    
 
            #If any of the issues in the summary dictionary have a warning, write the 
            #details string to the report. 
            try:
                if any([True for k,v in summary_dict.items() if v == "Warning"]):
                    f.write(details) 
            except Exception as e:
                arcpy.AddMessage  ("Could not write details for " + name + " to the report. There may be unicode characters in the field names. (" + str(e) + ")")
                f.write("\nCould not write more detailed warnings to the report. Check the tool results window for errors.")
            f.write("\n\n\n")
    
    #Write a summary of warnings for the geodatabase as a whole
    f.write("**********************************************\nSummary\n\nTotal feature classes checked: " + str(count) + "\nFeature classes with warnings: " + str(warning_count) + "\n\n")
    if warning_list:
        f.write("Warnings Found\n")
        c = Counter(warning_list)
        for value, count in c.most_common():
            f.write(value + " : " + str(count) +"\n")
    if no_features:
        f.write("\nThe following feature classes have no features:\n")
        for layer in no_features:
            f.write("  "+ layer +"\n")
        f.write("Note: Conversion to shapefile will not be affected by a lack of features.")
    
    f.write("\n\n**********************************************\n\n")
    f.close()

arcpy.AddMessage("Script complete!")