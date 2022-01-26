# Shapefile inventory python script

This python script creates an inventory of the shapefiles in a folder, including:
* a list of shapefiles in the folder (ordered alphabetically)
* a list of field names / field types for each shapefile

The script also: 
* flags shapefiles that are corrupt or cannot be opened
* checks file extensions to ensure that all required and recommended files are present
* determines whether the shapefiles in the folder have the same spatial reference

The file list/inventory is written to a text file ("fileList_[directory_name].txt"). The format is based on a [readme template used by the Data Repository for the University of Minnesota](z.umn.edu/readme) (originally developed at [Cornell University](https://data.research.cornell.edu/content/readme)) The report on projections and file extension is a separate text file ("report_[directory_name].txt").  Both files will be written to the folder that is being examined by the script.

**Sample reports**

[File list](https://github.com/mkernik/geodct/edit/main/sampleReports/fileList_ProjectShapefiles.txt)

[Curation report](https://github.com/mkernik/geodct/edit/main/sampleReports/report_ProjectShapefiles.txt)


## Requirements
* Python 3 with the additional python library [gdal](https://gdal.org/)

## How to use
* Download or clone this repository folder to your computer
* Open the OSGeo4W Shell  (Can be acquired as part of the default installation of the open source tool [QGIS](https://qgis.org/en/site/)) 
* Change the working directory to the location of the script

  **Example:** cd path/of/script
* Call the script and provide the path of the folder with the shapefiles

  **Example:** python shapefileInventory.py C:\Desktop\Shapefiles

If you don't want to use the OSGeo4W Shell, you can also download the gdal library to run from other instances of Python.  

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
