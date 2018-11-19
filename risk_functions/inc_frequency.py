#!/usr/bin/python

import os
import arcpy

# RJL - 15/11/2018

# -------------------------------------------

# Calculate incident frequency 
# RJL - 15/11/18



# To Do:
# 15/11/2018 - RJL: Some capability to say what date(s) this is for.
# 15/11/2018 - RJL: A time series capability would be nice...


def inc_freq(traf, inc, GRD,FileGDB_path, FileGDB_name, FREQ):

	#FREQ = "\"" + str(output) + "\""
	if arcpy.Exists(FileGDB_path + FileGDB_name +"/" + FREQ):
                arcpy.DeleteField_management (FileGDB_path + FileGDB_name +"/" + FREQ, [traffic_dens, incident_dens,incident_freq])
	if not arcpy.Exists(FileGDB_path + FileGDB_name +"/" + FREQ):
		arcpy.CopyFeatures_management (GRD[0], FileGDB_path + FileGDB_name +"/" + FREQ)
	
	arcpy.JoinField_management (FileGDB_path + FileGDB_name +"/" + FREQ, "OBJECTID", traf, "OBJECTID",["traffic_dens"])
	arcpy.JoinField_management (FileGDB_path + FileGDB_name +"/" + FREQ, "OBJECTID", inc, "OBJECTID",["incident_dens"])
	arcpy.AddField_management(FileGDB_path + FileGDB_name +"/" + FREQ, "incident_freq", "FLOAT","","8","","","NULLABLE","REQUIRED", "")
	arcpy.CalculateField_management(FileGDB_path + FileGDB_name +"/" + FREQ,"incident_freq", "0 if !traffic_dens! == 0 else !incident_dens!/!traffic_dens!", 'PYTHON3')
	print(FREQ + " created")

