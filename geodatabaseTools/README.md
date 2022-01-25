# Geodatabase Data Curation ArcGIS Toolbox

This ArcGIS custom toolbox contains tools intended to help prepare geodatabases for archiving or sharing.

### Requirements

ArcGIS Pro (The tool was built using version 2.9.0)

### How to use
* Download or clone this repository folder to your computer
* Open ArcGIS Pro
* Use the catalog view to connect to a folder containing the toolbox.

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

The results of this inspection are written to a text file ("warning_report_[geodatabase_name]") in the directory where the geodatabase is located.  A section at the top provides a list of feature classes and information about the geodatabase as a whole.  Each valid feature class has a section in the following report with a summary of possible warnings and then details about any issues found.

(sample report)

The tool can process multiple file geodatabases at once. A separate text file report will be created for each geodatabase.

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

(sample report)

The tool can process multiple file geodatabases at once. (The script parameter “geodatabase” is multivalued.)  A separate text file report will be created for each geodatabase. 


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
