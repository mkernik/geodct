# Geodatabase Data Curation ArcGIS Toolbox

This ArcGIS custom toolbox contains tools intended to help prepare geodatabases for archiving or sharing.

### Requirements

ArcGIS Pro (tools built using version 2.9.0)

### How to use
* Download or clone this repository folder to your computer
* Open ArcGIS Pro
* Use the catalog view to connect to the folder containing the toolbox
* Double click on the tool you would like to use
* Browse for and select your desired geodatabase(s)
* Click on the "Run" button and check the "View Details" windows for any error messages
* When the script completes, check the folder with the geodatabase(s) for the reports

## GeodatabasetoShapefileWarnings ArcGIS tool script

### Description:
This ArcGIS script tool examines feature classes in input file geodatabases for characteristics and data that would be lost or altered if it were transformed into a shapefile. Checks include:

* large files (feature classes with more than 255 fields or over 2GB) 
* field names longer than 10 characters  
* string fields longer than 254 characters  
* date fields with time values  
* NULL values
* BLOB, guid, global id, and raster field types   
* attribute domains or subtypes  
* annotation or topology    

The results of this inspection are written to a text file ("warning_report_[geodatabase_name]") in the directory where the geodatabase is located.  A section at the top provides a list of feature classes and information about the geodatabase as a whole. The following report has a section for each valid feature classes that returned a warning, with a summary of possible warnings and then more details about issues found.

The tool can process multiple file geodatabases at once. A separate text file report will be created for each geodatabase.

**Sample report**

[Warning report](https://github.com/mkernik/geodct/blob/main/sampleReports/warning_report_GeodatabaseToTransform.txt)

### Known limitations:
There are some additional issues when converting from geodatabase to shapefile that this script does not currently check for, including:
* geometric networks
* coordinate ID field types

See this resource for [a complete list of differences in functionality](https://desktop.arcgis.com/en/arcmap/latest/manage-data/shapefiles/geoprocessing-considerations-for-shapefile-output.htm).


## Geodatabase Inventory ArcGIS tool script

### Description:
This ArcGIS script tool takes inventory of data layers in a geodatabase.  It creates a file list, including: 
* a summary of the number of data layers of different types
* a list of data layers grouped by type (then ordered alphabetically)
* a list of field names for any feature classes and tables 

The results of this inspection are written to a text file ("fileList_[geodatabase_name].txt") in the directory where the geodatabase is located.  The format is based on a [readme template used by the Data Repository for the University of Minnesota](z.umn.edu/readme) (originally developed at [Cornell University](https://data.research.cornell.edu/content/readme)) 

The tool can process multiple file geodatabases at once. (The script parameter “geodatabase” is multivalued.)  A separate text file report will be created for each geodatabase.

**Sample report**

[File list](https://github.com/mkernik/geodct/main/sampleReports/fileList_METRO_PARKS_TRAILS_v1_2.txt)


## License

This project is licensed under Creative Commons Attribution-NonCommercial [(CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/) 
