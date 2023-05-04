# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 12:04:03 2022
script name: geodatabaseInventory.py
input: <geodatabase pathname(s)>
output: text file report "fileList_[geodatabase_stem].txt"

description: This script creates an inventory of data layers in a geodatabase,
including a summary of the number of layers, list of data layer names by type, 
and a list of field names for any feature classes and tables. The field name 
list includes details about subtypes and attribute domains if they have been 
defined.  The format is based on a readme template used at the Data Repository 
for the University of Minnesota.

last modified: January 2022
author: Melinda Kernik
"""

##import necessary modules and return a message if any are not available
try:  
    import arcpy
    import os
    from datetime import datetime
    from collections import Counter, OrderedDict
    from pathlib import Path
except Exception as e:
    arcpy.AddMessage(str(e))


def GeodatabaseContentFull (geodatabase):
    """Return information about the contents of a geodatabase. The major
    data layer types (feature class, raster, table, relationship, annotation, 
    and feature dataset) are grouped in separate dictionaries. The less common 
    data layer types are grouped in another dictionary.

    Parameters
    ----------
    geodatabase : geodatabase file path

    Returns
    -------
    Alphabetically ordered dictionaries for different data types with 
    layer name (key) and additional properties (values).
    feature_classes: list - [feature type (e.g. simple, annotation), shape type (point, polyline, polygon)] 
    rasters: list - [number of raster bands, compression type, raster format]
    tables: data type (ie. "Table")
    relationships: cardinality (eg. OnetoOne, OnetoMany, ManytoMany)
    annotation: list - [feature type (e.g. simple, annotation), shape type (point, polyline, polygon)] 
    other_types: data type
    feature_datasets: dictionary of component data layers - data layer name (key): 
        addtional properties (value). Properties are the same as the list above except that the first
        value in every list is the data type.
    """
    arcpy.env.workspace = geodatabase
    
    #Inspect the data types of the data layers in a geodatabase (ie it's "children" and "grandchildren") 
    feature_classes = {}
    rasters ={}
    tables = {}
    relationships = {}
    annotation = {}
    feature_datasets = {}
    other_types = {}
    
    desc_gdb = arcpy.Describe(geodatabase)
    for child in desc_gdb.children:    
        if child.dataType == "FeatureClass":
            if child.featureType == "Annotation":
                annotation[child.name] = [child.featureType, child.shapeType] 
            else:
                feature_classes[child.name] = [child.featureType, child.shapeType]
        elif child.dataType == "RasterDataset":
            #if child.bandCount == 1:
            #additional raster band properties: https://pro.arcgis.com/en/pro-app/latest/arcpy/functions/raster-band-properties.htm    
            rasters[child.name] = [child.bandCount, child.compressionType, child.format]
        elif child.dataType == "Table":
            tables[child.name] = child.dataType
        elif child.dataType == "RelationshipClass":
            relationships[child.name] = child.cardinality
        elif child.dataType == "FeatureDataset":
            sub_properties = {}
            desc_fd = arcpy.Describe(child.catalogPath)
            for grandchild in desc_fd.children:
                if grandchild.dataType == "FeatureClass":
                    sub_properties [grandchild.name] = [grandchild.dataType, grandchild.featureType, grandchild.shapeType]
                elif grandchild.dataType == "RasterDataset":
                    sub_properties[grandchild.name] = [grandchild.dataType, grandchild.bandCount, grandchild.compressionType, grandchild.format]
                elif grandchild.dataType == "RelationshipClass":
                    sub_properties [grandchild.name] = [grandchild.dataType, grandchild.cardinality]
                elif grandchild.dataType == "Topology":
                        sub_properties [grandchild.name] = [grandchild.dataType, grandchild.featureClassNames]
                else:
                    sub_properties[grandchild.name] = [grandchild.dataType]
            feature_datasets[child.name] = sub_properties
        else:
            other_types[child.name] = child.dataType
            
    return OrderedDict(sorted(feature_classes.items())), OrderedDict(sorted(rasters.items())), OrderedDict(sorted(tables.items())), OrderedDict(sorted(relationships.items())), OrderedDict(sorted(annotation.items())), OrderedDict(sorted(feature_datasets.items())), OrderedDict(sorted(other_types.items()))

    

def FieldList(feature_classes_full):
    """Return a dictionary of field names for each feature class and table,
    grouped by data type (options: standalone feature classes, standalone tables, 
    and feature datasets (one for each dataset).
    
    Parameters
    ----------
    feature_classes_full: dictionary of feature classes with name (key), 
        [data type, absolute path, dataset (if relevant)] (value)

    Returns
    -------
    features_fields : dictionary with data type (key):
        dictionary of data layers of that data type - absolute path (key): 
        list of (field names, field type) (value)
    """
       
    fc_fields = {}
    table_fields = {}
    features_fields = {}
    for k,v in feature_classes_full.items():
        field_names = [(f.name, f.type) for f in arcpy.ListFields(v[1])]
        if v[0] == "standalone_fc":
            fc_fields[v[1]] = (field_names)
        if v[0] == "table":
            table_fields[v[1]] = (field_names)
        if v[0] == "featureDataset_fc":
            #If this is the first data layer from within a feature dataset, add
            #a new key:value pair
            if v[2] not in features_fields.keys():
                features_fields[v[2]] = {v[1]: (field_names)}
            #If there is already a key for the feature dataset in the dictionary
            #update the value
            else:
                datasets = features_fields[v[2]]
                datasets[v[1]] = (field_names)
                features_fields.update({v[2]:datasets})
    
    #combine the dictionaries of different data types together
    if fc_fields:
        features_fields["Standalone feature classes"] = fc_fields
    
    if table_fields:
        features_fields["Standalone tables"] = table_fields
            
    return features_fields



def AttributeDomains (fc):
    """Check feature class or table for fields formatted with attribute domains.
    Note this function doesn't seem to work for feature classes with subtypes.

    Parameters
    ----------
    fc : absolute path to the feature class or table

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

    
def AttributeDomainInfo (geodatabase):
    """Return all attribute domains in the geodatabase

    Parameters
    ----------
    geodatabase : geodatabase file path

    Returns
    -------
    gdb_domains : dictionary with domain name (key): domain values (value)

    """
    domains = arcpy.da.ListDomains(geodatabase)
    gdb_domains = {}
    for domain in domains:
        if domain.domainType == 'CodedValue':
            sorted_codedValues = OrderedDict(sorted(domain.codedValues.items()))
            gdb_domains[domain.name] = ['CodedValue', sorted_codedValues]
        if domain.domainType == 'Range':
            gdb_domains[domain.name] = ['Range', domain.range]
    return gdb_domains

     
def SubtypeInfo(fc):
    """Return which field in a feature class or table has
    subtypes defined (if any) as well as the properties of those subtypes.
    
    Parameters
    ----------
    fc : absolute path to the feature class or table

    Returns
    -------
    subtype_field : the name of the field that has subtypes defined
    subtype_all : list of subtype properties.  Each subtype has a dictionary in 
        with keys "Code", "Name", and "Fields" (a list of fields that have 
        a default value assigned (field name, default value)).  
    """
    subtypes = arcpy.da.ListSubtypes(fc)
    
    subtype_all = []
    for stcode, stdict in sorted(list(subtypes.items())):
        subtype_info = {}
        subtype_info["Code"] = stcode
        #Check whether a subtype field has been defined for the feature class
        for stkey in list(stdict.keys()):
            if stkey == 'SubtypeField':
                subtype_field = stdict[stkey]
        #If there are subtypes, collect their default properties
        if subtype_field:
            for stkey in list(stdict.keys()):
                if stkey == "Name":
                    subtype_info["Name"] = stdict[stkey]
                if stkey == 'FieldValues':
                    default_fields = []
                    fields = stdict[stkey]
                    for field, fieldvals in list(fields.items()):
                        if fieldvals[0] is not None:
                            default_fields.append((field, fieldvals[0]))
            subtype_info["Fields"] = default_fields
        else:
            continue
        subtype_all.append(subtype_info)
    
    return subtype_field, subtype_all

#########

###Get path to geodatabase or multiple geodatabases
for gdb in arcpy.GetParameterAsText(0).split(";"):
    geodatabase = gdb
       
    #Make sure the path to the geodatabase exists.  Stop the script if the directory cannot be found.
    if os.path.isdir(geodatabase):
        pass
    else:
        arcpy.AddMessage("Cannot access the geodatabase: " + geodatabase + ". Please check the file path. No report will be generated. ")
        continue

    #Take inventory of the geodatabase layers and attribute domains
    feature_classes, rasters, tables, relationships, annotation, feature_datasets, other_types = GeodatabaseContentFull(geodatabase)
    gdb_domains = AttributeDomainInfo(geodatabase)

    #If there are no data layers, stop the script.
    contents = [feature_classes, rasters, tables, relationships, annotation, feature_datasets, other_types]   
 
    if any(contents):
        arcpy.AddMessage ("Creating inventory for " + Path(geodatabase).stem) 
        pass
    else:
        arcpy.AddMessage ("The script found no data layers for " + Path(geodatabase).stem + ". The geodatabase may be empty or corrupted. No report will be generated.")
        continue

    #Open a text file in which to write the file inventory and add a header
    fileList_path = os.path.dirname(geodatabase) + "/fileList_" + Path(geodatabase).stem + ".txt"
    f = open(fileList_path ,'w') 
    f.write ("This report was generated for " + Path(geodatabase).stem + ".gdb on "+ str(datetime.now().strftime("%Y-%m-%d")) + "\n\n")

    #Write a summary of the data types present in the geodatabse
    f.write ("********************************************\nSummary\n" + "********************************************\n\n")
    f.write("The geodatabase includes the following data layers: \n")

    if feature_classes:
        f.write("  " + str(len(feature_classes)) + " Feature Class(es)\n")
    if rasters:
        f.write("  " + str(len(rasters)) + " Raster(s)\n")
    if tables:
        f.write("  " + str(len(tables)) + " Table(s)\n")
    if annotation:
        f.write("  " + str(len(annotation)) + " Annotation layer(s)\n")
    if relationships:
        f.write("  " + str(len(relationships)) + " Relationship layer(s)\n")
    if other_types:
        for k,v in Counter(other_types.values()).items():
            f.write("  " + str(v) +" "+ k + " layer(s)\n")
    if feature_datasets:
        f.write("  " + str(len(feature_datasets)) + " Feature Dataset(s) containing:\n")
        merge_dict = {k: v for d in feature_datasets.values() for k, v in d.items()}
        fd_type = [dataType[0] for dataType in merge_dict.values()]
        for k,v in Counter(fd_type).items():
            f.write("\t" + str(v) + " " + k + " layer(s)\n")
    f.write("\n\n")


    #Write an inventory of geodatabase items and their fields. Formatting reflects 
    #a readme template used by several academic data repositories including the 
    #Data Repository at the University of Minnesota (DRUM)
    
    f.write ("********************************************\nGeodatabase content list\n" + "********************************************\n\n")
    
    if feature_classes: 
        f.write("Feature classes:\n\n")
        for k, v in feature_classes.items():
            f.write ("\tData layer: " +  k +" (" + feature_classes[k][1] + ")\n\tShort description:\n\n")
    
    if rasters:
        f.write("Rasters:\n\n")
        for k, v in rasters.items():
            f.write ("\tData layer: " +  k +" (" + str(rasters[k][0]) + "-band)\n\tShort description:\n\n")
    
    if tables:
        f.write("Tables:\n\n")
        for k, v in tables.items():
            f.write ("\tData layer: " +  k +" (Table)\n\tShort description:\n\n")
    
    if annotation: 
        f.write("Annotation:\n\n")
        for k, v in annotation.items():
            f.write ("\tData layer: " +  k +" (Annotation)\n\tShort description:\n\n")
    
    if other_types or relationships:
        f.write("Other layer types:\n\n")
        if other_types:
            for k, v in other_types.items(): 
                f.write ("\tData layer: " +  k +" (" + other_types[k] + ")\n\tShort description:\n\n")
        
        if relationships:
            for k, v in relationships.items(): 
                f.write ("\tData layer: " +  k + " (" + v + " relationship)\n\tShort description:\n\n")

    if feature_datasets: 
        f.write("Feature Datasets:\n\n")
        for dataset, content in feature_datasets.items():
            f.write("  Collection: " + dataset + "\n")
            fd = OrderedDict(sorted(content.items()))
            for k, v in fd.items():
                if v[0] == "FeatureClass":
                    if v[1] == "Annotation": 
                        f.write ("\tData layer: " +  k +" (Annotation)\n\t\tShort description:\n\n")
                    else:
                        f.write ("\tData layer: " +  k +" (" + v[2] + ")\n\t\tShort description:\n\n")
        
                elif v[0] == "RasterDataset":
                    f.write ("\tData layer: " +  k +" (" + str(v[1]) + "-band)\n\t\tShort description:\n\n")
        
                elif v[0] == "Topology":
                    f.write ("\tData layer: " +  k +" (topological relationship between " + v[1][0] + " and " + v[1][1] + ")\n\t\tShort description:\n\n")
    
                elif v[0] == "RelationshipClass":
                    f.write ("\tData layer: " +  k +" (" + v[1] + " relationship)\n\t\tShort description:\n\n")
                
                else:
                    f.write ("\tData layer: " +  k +" (" + fd[k][0] + ")\n\tShort description:\n\n")


    #Make a dictionary with all data layers that have fields (ie. feature classes 
    #and tables - including those within feature datasets). 
    #layer name (key), [data type, absolute path, dataset (if relevant)] (value)  
    #data type options: standalone feature classes, standalone tables, and 
    #feature datasets (one for each dataset)  
    
    feature_classes_full = {}
    if feature_classes:
        for fc in feature_classes.keys():
            feature_classes_full[fc] = ["standalone_fc", (geodatabase + "/" + fc)]
    if tables:
        for table in tables.keys():
            feature_classes_full[table] = ["table", (geodatabase +  "/"  + table)]
    
    if feature_datasets:
        for dataset, content in feature_datasets.items():
            for layer, properties in content.items():
                if properties[0] == "FeatureClass" or properties[0] == "Table":
                    #Skip getting fields for annotation layers but add to the
                    #annotation layer list. (it controls whether info about where to
                    #find information about annotation field definitions is 
                    #written to the report))
                    if properties[1] == "Annotation":
                        annotation[layer] = dataset
                        pass
                    else:
                        feature_classes_full[layer] = ["featureDataset_fc", (geodatabase + "/" + dataset + "/"  + layer), dataset]


    features_fields = FieldList (feature_classes_full)

    #Write a list of fields for data layers (when relevant)
    if features_fields:
        f.write("\n\n********************************************\nField List\n" + "********************************************\n")
    
        for collection, features in features_fields.items():
            #If there is more than one grouping of data (ie. feature classes, tables, 
            #specific feature datasets), write the name of the collection
            if len(features_fields) > 1:
                f.write("\n------------------------------------------------------------------------\n" + collection + "\n------------------------------------------------------------------------\n\n")
            #For each data layer count the number of features/rows, number of 
            #fields, and write a list of those fields/field types
            for k,v in features.items():
                f.write("-----------------------------------------\nDATA-SPECIFIC INFORMATION FOR: " + Path(k).stem + "\n-----------------------------------------\n")
                
                #Get information about subtypes and domains used by the feature class
                subtype_field, subtype_all = SubtypeInfo(k)
                domain_fields = AttributeDomains(k)
                
                f.write("A. Number of features:  %s" % str(arcpy.GetCount_management(k)) + "\n")
                f.write("B. Number of fields: " + str(len(features[k])) + "\n")       
                f.write("C. Field list\n")
                try:
                    for i, field in enumerate(features[k], start=1):
                        #if there are subtypes, write information about the code 
                        #and associated default field values
                        if subtype_field:
                            if field[0] == subtype_field:
                                f.write ("\t" + str(i) + ". Name: " + field[0] + " ("+ field[1] + ")\n\tDescription: [Subtypes]\n")
                                for code in subtype_all:
                                    for key in code.keys():
                                        if key == "Code":
                                            f.write("\t\tCode: " + str(code[key]) + "\n")
                                        if key == "Name":
                                            f.write("\t\tName: " + code[key] + "\n")
                                        if key == "Fields":
                                            f.write("\t\tDefault field values:\n")
                                            for tup in code[key]:
                                                f.write("\t\t\t" + tup[0] + ": " + str(tup[1]) + "\n")
                                    f.write("\n")
                        #if there are attribute domains defined, write the coded or range values.
                        if field[0] in domain_fields.keys():
                            domain_name = domain_fields[field[0]]
                            f.write ("\t" + str(i) + ". Name: " + field[0] + "\n\tDescription:\n")
                            if gdb_domains[domain_name][0] == "CodedValue":
                                coded_values = gdb_domains[domain_name][1]
                                for val, desc in coded_values.items():
                                    if str(val) != str(desc):
                                        f.write("\t\t" + str(val) + ": " + str(desc) + "\n")
                                    else:
                                        f.write("\t\t" + str(val) + "\n")
                            if gdb_domains[domain_name][0] == "Range":
                                minmax = gdb_domains[domain_name][1]
                                f.write("\t\tMin: " + str(minmax[0]) + "\n\t\tMax: " + str(minmax[1]) + "\n")
                            f.write("\n")
                        
                        if field[0] != subtype_field and field[0] not in domain_fields:
                            f.write ("\t" + str(i) + ". Name: " + field[0] + " ("+ field[1] + ")\n\tDescription:\n\n")
                            
                except Exception as e:
                    arcpy.AddMessage("Error writing the fields for " + Path(k).stem + " (" + str(e) + ")")
                    pass
        
        #Annotation layers have not been included in the field list because information about their meaning has been documented elsewhere. 
        if annotation:
            f.write("-----------------------------------------\n***For definitions of annotation layer fields, see ESRI support documents (https://support.esri.com/en/technical-article/000008390)***\n")
    
    else:
        pass
    
    f.close()
    
arcpy.AddMessage("Script completed!")