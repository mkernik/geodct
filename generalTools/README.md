# Batch unzip script

This python script / tool batch extracts the .zip files in a directory and its subdirectories using the [zipfile python library](https://docs.python.org/3/library/zipfile.html). It also returns a count of the extracted zipped folders.  The tool is available in two formats: a script to be run from the command line and a graphical user interface.

### Requirements
* Python 3 (tool built using Python 3.7)

## How to use

* Download or clone this repository folder to your computer

### Using the graphical user interface

* Find your downloaded UnzipTkinter.py file and double click on it
* The script should open a dialog box that you can use to select a folder of zipped files
* If the dialog box does not appear:
    * open the command prompt and change the working directory to the script location
    * open python and call the script.
      
      **Windows example:** py UnzipTkinter.py
      
      **Mac example:** python UnzipTkinter.py


### From the command line
* Copy the UnzipCommandLine.py script into the folder with zipped files (Or provide an absolute path to the folder when typing in the command)

* Open the Command Prompt (windows) or Terminal (mac).
* Change the working directory to the location of the script

  **Example:** cd path/of/script

* Open Python, call the script, and provide the path of the folder with the zipped files

  **Windows example:** py UnzipCommandLine.py directory/

  **Mac example:** python UnzipCommandLine.py directory

## License

This project is licensed under Creative Commons Attribution-NonCommercial [(CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/) 
