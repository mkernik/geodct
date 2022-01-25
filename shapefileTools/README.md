# Shapefile inventory script

This python script creates an inventory of the shapefiles in a folder, including:
* a list of shapefiles in the folder (ordered alphabetically)
* a list of field names / field types for each shapefile

The script also: 
* checks file extensions to ensure that all required and recommended files are present
* determines whether the shapefiles in the folder have the same spatial reference
* flags shapefiles that are corrupt or cannot be opened

The file list/inventory is written to a text file ("shapefile_fileList.txt"). The format is based on a [readme template used by the Data Repository for the University of Minnesota](z.umn.edu/readme) (originally developed at [Cornell University](https://data.research.cornell.edu/content/readme)) The report on projections and file extension is a separate text file ("shapefile_report.txt").  Both files will be written to the folder that is being examined by the script.

(sample reports)

### Requirements
* Python 3 with the additional python library [gdal](https://gdal.org/)

### How to use
* Download or clone this repository folder to your computer
*


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
