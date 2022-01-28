# Batch unzip script

This python script / tool batch extracts the .zip files in a directory and its subdirectories using the [zipfile python library](https://docs.python.org/3/library/zipfile.html). It also returns a count of the extracted zipped folders.  The tool available in two formats: a script to be run from the command line and a graphical user interface.

### Requirements
* Python 3 (tool built using Python 3.7.11)

## How to use

* Download or clone this repository folder to your computer

### Select folder using the graphical user interface (UnzipTkinter.py)

* Open the Command Prompt (windows) or Terminal (mac).
* Change the working directory to the location of the script

  **Example:** cd path/of/script

* Open python and call the script.
      
  **Windows example:** py UnzipTkinter.py
      
  **Mac example:** python UnzipTkinter.py

* Use the dialog box to choose a folder of zipped files.

*** If you are using macOS 12 Monterey or later, there is a [known issue](https://www.python.org/download/mac/tcltk/) that may affect the GUI tool. ***


### Select folder with the command line (UnzipCommandLine.py)
* Copy the UnzipCommandLine.py script into the folder with zipped files (or provide an absolute path to the folder when typing in the command)

* Open the Command Prompt (windows) or Terminal (mac).
* Change the working directory to the location of the script

  **Example:** cd path/of/script

* Open Python, call the script, and provide the path of the folder with the zipped files

  **Windows example:** py UnzipCommandLine.py directory/

  **Mac example:** python UnzipCommandLine.py directory

## License

This project is licensed under Creative Commons Attribution [(CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) 
