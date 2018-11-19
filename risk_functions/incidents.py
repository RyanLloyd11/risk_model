#!/usr/bin/python

import os
import arcpy

# RJL - 02/11/2018

# -----------------------------------------------------

# Function to take incidents, and calculate incident density

# To do:
# 	 - "if not arcpy.Exists(FileGDB_path + FileGDB_name +"/" + OUT_temp):" -- ArcPy seems to think that file exists when it doesnt...
#        - Test with multiple inputs
#        - Attacks which fall on boundary <PRIORITY>
#        - What attributes are needed for later relates. Relate MMSI with OBJECTID
# NB: This is attack density to date. Could also add in field for particular time. A sum of some of these would allow attack density between X and Y. 




def incident_density(FileGDB_path, FileGDB_name, incidents, GRD):
	out_date = []
	OUT = "incident_density" #+incidents[i][-6:]
	OUT_bydate = "incident_density_all"
	j=0
	if not arcpy.Exists(FileGDB_path + FileGDB_name +"/" + OUT): #+".shp"
		arcpy.CopyFeatures_management (GRD[0], FileGDB_path + FileGDB_name +"/" + OUT)
		arcpy.AddField_management(FileGDB_path + FileGDB_name +"/" + OUT, "incident_dens", "FLOAT","","8","","","NULLABLE","REQUIRED", "")
		arcpy.CalculateField_management(FileGDB_path + FileGDB_name +"/" + OUT,"incident_dens", "0", 'PYTHON3')    
	if not arcpy.Exists(FileGDB_path + FileGDB_name + "/" + OUT_bydate):
		arcpy.CopyFeatures_management (GRD[0], FileGDB_path + FileGDB_name +"/" + OUT_bydate)
		print(OUT_bydate + " created") 

	for i in incidents:
		OUT_temp = "incident_density_"+str(incidents[j][-6:])     # op file for each day 
		out_date.append(FileGDB_path + FileGDB_name +"/" + OUT_temp)
		if arcpy.Exists(FileGDB_path + FileGDB_name +"/" + OUT_temp):
			print(FileGDB_path + FileGDB_name +"/" + OUT_temp)
		if not arcpy.Exists(FileGDB_path + FileGDB_name +"/" + OUT_temp): 
		#if 1 == 1:
			print("I'm working!")	
			fieldMappings = arcpy.FieldMappings()
			fieldMappings.addTable(OUT)
			fieldMappings.addTable(FileGDB_path + FileGDB_name + "/" + incidents[j]+"_shp")
			for field in fieldMappings.fields:
				if field.name not in ["OBJECTID","Shape","TARGET_FID","GRID_ID","incident_dens" ,"SEA_AREA","MMSI","NGA_refer*"]:
					fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
			arcpy.SpatialJoin_analysis(GRD[0], FileGDB_path + FileGDB_name + "/" + incidents[j]+"_shp",OUT_temp,"JOIN_ONE_TO_ONE","KEEP_ALL",fieldMappings,"COMPLETELY_CONTAINS")
			with arcpy.da.UpdateCursor(FileGDB_path + FileGDB_name +"/" + OUT_temp, "SEA_AREA") as cursor: 
        		    # Replace land cells with SEA_AREA = None (avoid X/0 later)
				for row in cursor: 
					if row[0] == 0.0:
						row[0] = None
					cursor.updateRow(row)
        		# km^-2. Density for one particular day
			arcpy.CalculateField_management(FileGDB_path + FileGDB_name +"/" + OUT_temp,"incident_dens", "!SEA_AREA! if !SEA_AREA! == None else (!Join_Count!/(!SEA_AREA!/1e6))", 'PYTHON3') # FOR LAND SEA_AREA= 0  
			# Join incident_density_date to incident_density_all
			arcpy.JoinField_management (FileGDB_path + FileGDB_name + "/" + OUT_bydate, "OBJECTID", FileGDB_path + FileGDB_name + "/" + OUT_temp, "OBJECTID",["incident_dens"])
			# rename inc_all inc_dens field name to include date.
			arcpy.AlterField_management (FileGDB_path + FileGDB_name + "/" + OUT_bydate, "incident_dens", "inc_"+str(incidents[j])[-6:], "inc_"+str(incidents[j])[-6:])
			# join inc_all to inc_dens
			arcpy.JoinField_management (FileGDB_path + FileGDB_name +"/" + OUT, "OBJECTID", FileGDB_path + FileGDB_name + "/" + OUT_bydate, "OBJECTID",["inc_"+str(incidents[j])[-6:]])
			# Calculate updated traf_dens
			temp = "inc_"+str(incidents[j])[-6:]
			calcString = "!incident_dens! + !inc_"+str(incidents[j])[-6:]+"!"
			arcpy.CalculateField_management(FileGDB_path + FileGDB_name +"/" + OUT,"incident_dens", calcString, 'PYTHON3')

			#arcpy.CopyFeatures_management (FileGDB_path + FileGDB_name +"/" + OUT_temp, FileGDB_path + FileGDB_name +"/" + OUT)
		j=j+1
	
	OUT = FileGDB_path + FileGDB_name +"/" + OUT 
	return OUT, out_date

