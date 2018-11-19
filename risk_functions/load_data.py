#!/usr/bin/python

# THIS IS A MODULE
import pandas
import os
import arcpy

# --------------------------------

# Take list of csv files and create GDBshp fies for each one


def csv2shp(root,file,gdb_path,gdb_name):
	csvpath1 = []
	pts = []
	k = 0
	template ="inc_template"
	arcpy.env.workspace = gdb_path + gdb_name
	print("csv files converted to points:")
	with open(file, "r") as f:
		file_list = f.read().split()
	for f in file_list:
		csvpath1 = os.path.join(root,f)
		pts.append(csvpath1[len(root):csvpath1.find(".")])
		print (f + " >> "+ pts[k])
	#	if not os.path.exists(gdb_path + "/" + pts[k]+".shp"):
		if not arcpy.Exists(gdb_path + gdb_name + "/" + pts[k] + "_shp"): 
		#	print(csvpath1)
		#	print(pts[k])
			A = arcpy.GetCount_management(file)
			if int(A[0]) > 1: 
				arcpy.management.XYTableToPoint(csvpath1,pts[k]+".shp","Longitude","Latitude")
				arcpy.FeatureClassToGeodatabase_conversion(pts[k]+".shp",gdb_path + gdb_name)
			else:
    				if not arcpy.Exists(gdb_path+gdb_name+"/" + template):
        				arcpy.TableToTable_conversion (root+file, gdb_path+gdb_name+"/", template)
    				if not arcpy.Exists(gdb_path + gdb_name+ pts[k] +"_shp"):
        				arcpy.CreateFeatureclass_management (gdb_path + gdb_name, pts[k]+"_shp", "POINT")
        				fields = arcpy.ListFields (gdb_path+gdb_name+"/"+template)
        				A = fields[0:]
        				for field in A:
            					a = field.type
            					if a == "String":
                					a = "Text"
                					arcpy.AddField_management (gdb_path + gdb_name+ pts[k]+"_shp", field.name,a)
            					elif a == "OID":
                					a = "Float"
                					arcpy.AddField_management (gdb_path + gdb_name+ pts[k]+"_shp", field.name,a)
            					else:
               		 				arcpy.AddField_management (gdb_path + gdb_name+ pts[k]+"_shp", field.name,field.type)				

		k=k+1
	return pts


# ---------------------------------
 
def csv2dict(root,file):
	k=0
	global fdict
	with open(file, "r") as f:
		file_list = f.read().split()
		fdict= {}
	for f in file_list:
		A = os.path.join(root,f)	
		fdict[f] = {f: pandas.read_csv(A,low_memory=False, error_bad_lines=False)}
		k=k+1
	return fdict 

# ---------------------------------

# ISSUES:
# - 25/10/18 - RJL: OP not global

# Define a function
def loadais(root,file):
# Fucntion to load in AIS data. RJL - 23/10/2018
	file_list = []
	with open(file, "r") as f:
		file_list = f.read().split()
	for f in file_list:
		A = os.path.join(root,f)
		globals()["data" + str(A[-16:-13])+ "_" + str(A[-12:-4])] =  pandas.read_csv(A,header=None,low_memory=False, error_bad_lines=False)

# --------------------------------

# ISSUES:
# - 25/10/18 - RJL: OP not global    

# Define a function  
def loadincidents(root,file):
# Fucntion to load in incidents data. RJL - 23/10/2018
	file_list = []
	with open(file, "r") as f:
		file_list = f.read().split()
	for f in file_list:
		A = os.path.join(root,f)  
		globals()["incidents_" + str(A[-10:-4])]=  pandas.read_csv(A,header=None,low_memory=False)
