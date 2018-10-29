#!/usr/bin/python

import arcpy
import os

def creategdb(FileGDB_path,FileGDB_name):

	if not os.path.exists(FileGDB_path + FileGDB_name): 
    		arcpy.CreateFileGDB_management(FileGDB_path, FileGDB_name)
	else:
    		print("FileGDB already exists")
