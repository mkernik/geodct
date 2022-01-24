# Geospatial Data Curation Toolkit

This repository contains a collection of python scripts and ArcGIS tools intended to assist preparing spatial data for archiving or sharing.

## Features

* Batch unzip folders (i.e extract zipped shapefiles)
* Create an inventory of files/fields in shapefiles / geodatabases for readme .txt files
* Check whether the shapefiles in a directory have the same projection and file extensions
* Check whether the layers in a geodatabase have functionality that would be lost or altered if converted into shapefiles

## Requirements

**For general curation tools:**
* Python 3

**For tools dealing with shapefiles:**
* Python 3 with the additional python library [gdal](https://gdal.org/)

**For tools dealing with geodatabases:**
* ArcGIS Pro (tools built with 2.9)

## Author

Melinda Kernik - [University of Minnesota Map Library](https://www.lib.umn.edu/about/staff/melinda-kernik)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgements

* [University of Minnesota Libraries](https://www.lib.umn.edu/)
* [The Data Curation Network](https://datacurationnetwork.org/)
* the Geo4Lib community
