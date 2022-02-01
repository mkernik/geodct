# Geospatial Data Curation Toolkit

This repository contains a collection of python scripts and ArcGIS tools to help prepare spatial data for archiving or sharing.

## Features

[generalTools](https://github.com/mkernik/geodct/edit/main/generalTools)
* Batch unzip folders (i.e. extract zipped shapefiles)

[shapefileTools](https://github.com/mkernik/geodct/edit/main/shapefileTools)
* Create an inventory of a folder of shapefiles and their fields for a readme .txt file
* Check whether the shapefiles in a directory have the same projection and file extensions

[geodatabasefileTools](https://github.com/mkernik/geodct/edit/main/geodatabaseTools)
* Create an inventory of data layers/fields in geodatabases for a readme .txt file
* Check whether the layers in a geodatabase have functionality that would be lost or altered if converted into shapefiles

## Requirements

**For general curation tools:**
* [Python 3](https://www.python.org/) (tools built with version 3.7.11)

**For tools dealing with shapefiles:**
* Python 3 with the additional python library [gdal](https://gdal.org/) OR OSGeo4W Shell (available with download of [QGIS](www.qgis.org))

**For tools dealing with geodatabases:**
* ArcGIS Pro (tools built with version 2.9.0)

## Author

Melinda Kernik - [University of Minnesota Borchert Map Library](https://www.lib.umn.edu/about/staff/melinda-kernik)

## License

This project is licensed under Creative Commons Attribution-NonCommercial [(CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/)

## Acknowledgements

* [University of Minnesota Libraries](https://www.lib.umn.edu/)
* [The Data Curation Network](https://datacurationnetwork.org/)
* the Geo4Lib community
