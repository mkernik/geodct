# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 13:03:18 2021
script name: UzipCommandLine.py
input: path to directory with zipped folders
outputs: unzipped folders
description: The script batch unzips files in a directory and its subdirectories. It also returns a count of extracted zipped folders.
last modified: January 2022
author: Melinda Kernik
"""

import sys
import os
import zipfile

args = sys.argv


def checkPath (inputDir):
    """Check for a valid folder path and quit if not available"""
    if os.path.exists(os.path.abspath(inputDir)):
        print ("Processing files in: %s..." % (os.path.abspath(inputDir))) 
    else:
        print ("The directory does not exist or is not a recognized path. (%s)" % (os.path.abspath(inputDir)))
        quit()
    
def extract_all(inputDir):
    
    """Extract zipped files within the selected directory and its subdirectories
    and count the number of extracted files
    """
    
    created_zips = 0
    for root, dirs, files in os.walk(inputDir):
        for f in files:
            if f.endswith('.zip'):
                try:
                    inFile = os.path.join(root, f)
                    print ('Working on: ', f)
                    outDir = os.path.join(root, f[:-4])
                    if not os.path.isdir(outDir):
                        os.mkdir(outDir)
                    else:
                        print (f, ' has already been extracted or there is a folder with the same name in this folder: ')
                        continue
        
                    with zipfile.ZipFile(inFile,'r') as z:
                        z.extractall(outDir)
                    print (f,' was successfully extracted.')
                    created_zips += 1
                except Exception as e:
                    print("Could not process the zipped file: %s (%s)." % (f, e))
                    #continue
    if created_zips == 0:
        print ("There are no recognized zipped files in the selected directory or all of the zipped files have already been extracted from:  %s" % (inputDir))
    else:
        print ('Processed %s zipped files from %s or its subfolders!' % (str(created_zips), inputDir))

if __name__ == "__main__":
    checkPath(args[1])
    extract_all(args[1])



