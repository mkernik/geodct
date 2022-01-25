# Shapefile Inventory python script

This script creates an inventory of files and field names for shapefiles in a directory, including:
* a list of shapefiles in the directory (ordered alphabetically)
* a list of field names / field types for each shapefile

The lists are written to a text file ("shapefile_fileList.txt") in the directory being examined by the script. The format is based on a [readme template used by the Data Repository for the University of Minnesota](z.umn.edu/readme) (originally developed at [Cornell University](https://data.research.cornell.edu/content/readme))

The script also writes a separate text file ("shapefile_report.txt"), which:  
* checks file extensions to ensure that all required and recommended files are present
* determines whether the shapefiles in the directory have the same spatial reference
* flags shapefiles that are corrupt or cannot be opened

(sample reports)

### Requirements
* Python 3 with the additional python library [gdal](https://gdal.org/)

### How to use
* Download or clone this repository folder to your computer
*


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
