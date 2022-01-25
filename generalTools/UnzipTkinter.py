"""
Created on Fri Dec 17 13:03:18 2021
script name: UzipTkinter.py
input: path to directory with zipped folders provided through a graphical interface
outputs: unzipped folders
description: The tool batch unzips files in a directory and its subdirectories. 
It also returns a count of extracted zipped folders.
last modified: January 2022
author: Melinda Kernik

Tkinter GUI interface built using a template in an exercise provided by the Linkedin 
Learning course "Building Tools with Python"  
"""

import os
import zipfile
import tkinter

def show_error(text): 
    tkinter.messagebox.showerror('Error', text)

def show_results(text):
    tkinter.messagebox.showinfo("Results", text)
   
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
                    #print ('Working on: ', f)
                    outDir = os.path.join(root, f[:-4])
                    if not os.path.isdir(outDir):
                        os.mkdir(outDir)
                    else:
                        #show_error ('%s has already been extracted or there is 
                        #a folder with the same name in this folder: ' % (f))
                        continue
        
                    with zipfile.ZipFile(inFile,'r') as z:
                        z.extractall(outDir)
                    #show_results ('%s was successfully extracted.' % (f))
                    created_zips += 1
                except Exception as e:
                    show_error("Could not process the zipped file: %s (%s)." % (f, e))
                    #continue
    if created_zips == 0:
        show_error ("There are no recognized zipped files in the selected directory or all of the zipped files have already been extracted from:  %s" % (inputDir))
    else:
        show_results ('Processed %s zipped files from %s or its subfolders!' % (str(created_zips), inputDir))


# Create the Tkinter interface.
app = tkinter.Tk()
app.geometry('450x250')
app.title("Batch Unzip")

# Open the file picker and send the selected files to the extract_all() function.
def clicked():
    t = tkinter.filedialog.askdirectory()
    extract_all(t)

# Create the window header.
header = tkinter.Label(app, text="Welcome to Batch Unzip!", fg="blue", font=("Cabin", 24))
header.pack(side="top", ipady=20)

# Add the descriptive text.
text = tkinter.Label(app, text="Select a folder that contains zipped files. \n The app will extract files into unzipped folders of the same name. \n  Note: The tool will also extract zipped files in subdirectories. \n \n \n")
text.pack()

# Draw the button that opens the file picker.
open_folder = tkinter.Button(app, text="Choose folder...", command=clicked)
open_folder.pack(ipady=2, fill="x")

# Initialize Tk window.
app.mainloop()