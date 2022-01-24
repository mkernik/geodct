# Geodatabase Data Curation ArcGIS Toolbox

This repository contains a collection of python scripts and ArcGIS tools intended to assist preparing geodatabases for archiving or sharing.

### How to use
* Download or clone this repository folder to your computer
* Open ArcGIS Pro
* Use the catalog view to connect to a folder containing the toolbox you want to use.

## GeodatabasetoShapefileWarnings ArcGIS tool script

### Description:
This ArcGIS script tool examines feature classes in input file geodatabases for characteristics and data that would be lost or altered if it were transformed into a shapefile. Checks include:

* field names longer than 10 characters  
* string fields longer than 254 characters  
* date fields with time values  
* NULL values
* BLOB, guid, global id, and raster field types   
* attribute domains or subtypes  
* annotation or topology    

The results of this inspection are written to a text file ("warning_report_[geodatabase_name]") to the directory where the geodatabase is located.  A section at the top provides a list of feature classes and information about the geodatabase as a whole.  Each valid feature class has a section in the report that follows with a summary of possible warnings and then details about any issues found.

The tool can process multiple file geodatabases at once. (The script parameter “geodatabase” is multivalued.)  A separate text file report will be created for each geodatabase.

### Known limitations:
There are some additional issues when converting from geodatabase to shapefile that this script does not currently check for, including:
*geometric networks
*coordinate ID field types
See this resource for [a complete list of differences in functionality](https://desktop.arcgis.com/en/arcmap/latest/manage-data/shapefiles/geoprocessing-considerations-for-shapefile-output.htm).

## Requirements

ArcGIS Pro (tools built with 2.9)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
