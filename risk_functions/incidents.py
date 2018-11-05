#!/usr/bin/python

import os
import arcpy

# RJL - 02/11/2018

# -----------------------------------------------------

# Function to take incidents, and calculate incident density

# To do:
# 	 - NOT SURE THIS IS WIL ALWAYS WORK CORRECTLY (i,j)
#        - Test with multiple inputs
#        - Attacks which fall on boundary
#        - What attributes are needed for later relates
# NB: This is attack density to date. Could also add in field for particular time. A sum of some of these would allow attack density between X and Y. 




def incident_density(FileGDB_path, FileGDB_name, incidents, GRD):
	out_date = []
	OUT = "incident_density" #+incidents[i][-6:]
	j=0
	if not arcpy.Exists(FileGDB_path + FileGDB_name +"/" + OUT): #+".shp"
		arcpy.CopyFeatures_management (GRD[0], FileGDB_path + FileGDB_name +"/" + OUT)
		arcpy.AddField_management(FileGDB_path + FileGDB_name +"/" + OUT, "incident_dens", "FLOAT","","8","","","NULLABLE","REQUIRED", "")
		arcpy.CalculateField_management(FileGDB_path + FileGDB_name +"/" + OUT,"incident_dens", "0", 'PYTHON3')    
     
	for i in incidents:
		OUT_temp = "incident_density_"+str(incidents[j][-6:])     # op file for each day 
		out_date.append(FileGDB_path + FileGDB_name +"/" + OUT_temp)
		if not arcpy.Exists(FileGDB_path + FileGDB_name +"/" + OUT_temp): 
			fieldMappings = arcpy.FieldMappings()
			fieldMappings.addTable(OUT)
			fieldMappings.addTable(FileGDB_path + FileGDB_name + "/" + incidents[j]+"_shp")
			for field in fieldMappings.fields:
				if field.name not in ["OBJECTID","Shape","TARGET_FID","GRID_ID","incident_dens" ,"SEA_AREA","MMSI","NGA_refer*"]:
					fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
    
			arcpy.SpatialJoin_analysis(OUT, FileGDB_path + FileGDB_name + "/" + incidents[j]+"_shp",FileGDB_path + FileGDB_name +"/" + OUT_temp,"JOIN_ONE_TO_ONE","KEEP_ALL",fieldMappings,"COMPLETELY_CONTAINS")
			with arcpy.da.UpdateCursor(FileGDB_path + FileGDB_name +"/" + OUT_temp, "SEA_AREA") as cursor: 
        		    # Replace land cells with SEA_AREA = None (avoid X/0 later)
				for row in cursor: 
					if row[0] == 0.0:
						row[0] = None
					cursor.updateRow(row)
        		# km^-2
			arcpy.CalculateField_management(FileGDB_path + FileGDB_name +"/" + OUT_temp,"incident_dens", "!SEA_AREA! if !SEA_AREA! == None else (!incident_dens! + (!Join_Count!/(!SEA_AREA!/1e6)))", 'PYTHON3') # FOR LAND SEA_AREA= 0  
			arcpy.CopyFeatures_management (FileGDB_path + FileGDB_name +"/" + OUT_temp, FileGDB_path + FileGDB_name +"/" + OUT)
		j=j+1
	
	OUT = FileGDB_path + FileGDB_name +"/" + OUT 
	return OUT, out_date







