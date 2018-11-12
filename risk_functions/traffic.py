#!/usr/bin/python

import os
import arcpy

# RJL - 26/10/2018

# ----------------------------------------------------------

# Convert point data to lines

# To Do:
# 26/10/18 - RJL: add relate between incidents & traffic (via join_field)
# 05/11/18 - RJL: Ensure op is in gdb, and temp files are not saved

def ais2traffic(root,datafile_list,join_field,join_order,continent):
	traffic_layers = []
	for f in datafile_list:
		ip_name = os.path.join(root,f)
		if not os.path.exists(ip_name + "_all_lines.shp"):
		# Join points using join_field, by join_oder
			arcpy.PointsToLine_management(ip_name+".shp",ip_name+"_all_lines.shp", join_field,join_order)
			print("1")
		if not os.path.exists(ip_name+"_lyr_CCselect.shp"):
			# Identify lines which cross continent 
			arcpy.MakeFeatureLayer_management(ip_name+"_all_lines.shp",ip_name+"_lyr")   
			print("2")
			arcpy.SelectLayerByLocation_management(ip_name+"_lyr", "INTERSECT", continent,"", "NEW_SELECTION")
			print("3")
			arcpy.CopyFeatures_management(ip_name+"_lyr", ip_name+"_lyr_CCselect.shp")
			print("4")
			# Split these lines (SLOW)
		if not os.path.exists(ip_name+ "_split.shp"):  
			arcpy.SplitLineAtPoint_management(ip_name+"_lyr_CCselect.shp",ip_name+".shp", ip_name+ "_split.shp", "10 Meters") 
			print("5")
			# Select line segments which do not cross continent 
		if not os.path.exists(ip_name + "_splits_offshore.shp"):
			arcpy.MakeFeatureLayer_management(ip_name+ "_split.shp",ip_name + "_splits_lyr")
			print("6")
			arcpy.SelectLayerByLocation_management(ip_name + "_splits_lyr", "INTERSECT",continent,"", "NEW_SELECTION","INVERT")
			print("7")
			#if not os.path.exists(ip_name + "_splits_offshore.shp"):
			arcpy.CopyFeatures_management(ip_name + "_splits_lyr", ip_name + "_splits_offshore")
			print("8")
			# Select offshore ones from all 
		if not os.path.exists(ip_name+"_only_offshore.shp"):  
			arcpy.SelectLayerByLocation_management(ip_name+"_lyr", "INTERSECT", continent,"", "NEW_SELECTION","INVERT")
			print("9")
			arcpy.CopyFeatures_management(ip_name+"_lyr", ip_name +"_only_offshore")
			print("10")
			# Combine these with all lines that do not cross land (multiple ips) - merge to shape file
		if not os.path.exists(ip_name +"_offshore_traffic_lyr.shp"): 
			arcpy.Merge_management([ip_name+"_splits_offshore.shp" , ip_name+"_only_offshore.shp"],ip_name +"_offshore_traffic_lyr")
			# COPY TO GDB
		print("Output traffic files:")
		print(ip_name +"_offshore_traffic_lyr")
		traffic_layers.append(ip_name +"_offshore_traffic_lyr")
		print(traffic_layers)
	return traffic_layers
    # ADD RELATE TO MMSI LINE AND MMSI attack here?

#-------------------------------------------------------------


# TRAFFIC DENSITY (40mins/days_traffic)


#TO DO:
# Carry MMSI number forward.

# ISSUES:
# 09/11/18 - RJL NoneType + float "/" issue.


def traffic_density(inc_d, traffic,GRD, FileGDB_path, FileGDB_name):
	out_date = []
	traf_dens= "traffic_density" 
	traf_all = "traf_all"
	i=0

	if not arcpy.Exists(FileGDB_path + FileGDB_name +"/" + traf_dens): #+".shp"
		arcpy.CopyFeatures_management (GRD[0], FileGDB_path + FileGDB_name +"/" + traf_dens)	
		arcpy.AddField_management(FileGDB_path + FileGDB_name +"/" + traf_dens, "traffic_dens", "FLOAT","","8","","","NULLABLE","REQUIRED", "")
		arcpy.CalculateField_management(FileGDB_path + FileGDB_name +"/" + traf_dens,"traffic_dens", "0", 'PYTHON3')
		print("1")
    
	if not arcpy.Exists(FileGDB_path + FileGDB_name +"/" + traf_all): #+".shp"
		arcpy.CopyFeatures_management (GRD[0], FileGDB_path + FileGDB_name +"/" + traf_all)
		print("1b")
    
	for j in traffic:
		dens_out_d = "traffic_density" +"_"+str(traffic[i])[-29:-21] 
		out_date.append(FileGDB_path + FileGDB_name +"/" + dens_out_d)
		split = "Traffic_split" +"_"+str(traffic[i])[-29:-21]
		if not arcpy.Exists(FileGDB_path + FileGDB_name + "\\" + dens_out_d):
        		# Create traffic gdb and add path length field
        		arcpy.FeatureClassToGeodatabase_conversion(str(traffic[i])+".shp",FileGDB_path + FileGDB_name) #<--- THIS NEEDS TO GO IN TRAFFIC.py MODULE
        		print("2")
        
		if not arcpy.Exists(FileGDB_path + FileGDB_name + "\\" + split):
			# Split up lines by grid (1day of data = 27mins) # THIS MIGHT BE QUICKER IF WE STRIP ATTRIBUTES DOWN TO JUST ID&SHAPE, AND THEN ADD AFTER
			arcpy.Intersect_analysis ([GRD[0],FileGDB_path + FileGDB_name + "\\" + str(traffic[i])[-36:]], FileGDB_path + FileGDB_name + "\\" + split, "ALL", "", "INPUT")
			print("3a")
        
            		# Create length of each line in km. 
			arcpy.AddField_management(FileGDB_path + FileGDB_name + "\\" +  split, "path_len", "FLOAT","",9,"","","NULLABLE","REQUIRED","")
			arcpy.CalculateField_management(FileGDB_path + FileGDB_name + "\\" +  split,"path_len", '!shape.length@kilometers!', 'PYTHON3')
			print("4")  

		if not arcpy.Exists(FileGDB_path + FileGDB_name + "\\" + dens_out_d):
			print("5")
			# Spatial join for lines within grid
			fieldmappings = arcpy.FieldMappings()
			fieldmappings.addTable(GRD[0])
			fieldmappings.addTable(FileGDB_path + FileGDB_name + "\\" + split)
			path_lenFieldIndex = fieldmappings.findFieldMapIndex("path_len")
			fieldmap = fieldmappings.getFieldMap(path_lenFieldIndex)
			field = fieldmap.outputField
			field.name = "sum_path_len"
			field.aliasName = "sum_path_len"
			fieldmap.outputField = field
			fieldmap.mergeRule = "sum"
			fieldmappings.replaceFieldMap(path_lenFieldIndex, fieldmap)
   
            		# Find length of lines within cells
			arcpy.SpatialJoin_analysis (GRD[0], FileGDB_path + FileGDB_name + "\\" + split, FileGDB_path + FileGDB_name + "\\" + dens_out_d, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "CONTAINS", "", "")
			arcpy.AddField_management(FileGDB_path + FileGDB_name +"/" + dens_out_d, "traffic_dens", "FLOAT","","8","","","NULLABLE","REQUIRED", "")
			arcpy.CalculateField_management(FileGDB_path + FileGDB_name +"/" + dens_out_d,"traffic_dens", "0", 'PYTHON3')
			arcpy.CalculateField_management(FileGDB_path + FileGDB_name +"/" + dens_out_d,"SEA_AREA", "None if !SEA_AREA! == 0 else !SEA_AREA!", 'PYTHON3')
			arcpy.CalculateField_management(FileGDB_path + FileGDB_name +"/" + dens_out_d,"sum_path_len", "0 if !sum_path_len! == None else !sum_path_len!", 'PYTHON3')
			arcpy.CalculateField_management(FileGDB_path + FileGDB_name +"/" + dens_out_d,"sum_path_len", "None if !SEA_AREA! == None else !sum_path_len!", 'PYTHON3')   
			print("5a")
        
			# Divide by SEA_AREA/1e6 (km^2) (for ones with sea area)
			arcpy.CalculateField_management(FileGDB_path + FileGDB_name +"/" + dens_out_d,"traffic_dens", "None if !SEA_AREA! == None else (!traffic_dens! + (!sum_path_len!/(!SEA_AREA!/1e6)))", 'PYTHON3')
        
        
			# Update traffic_dens with traf_dens_date
			#fieldMappings = arcpy.FieldMappings()
			#fieldMappings.addTable(FileGDB_path + FileGDB_name +"/" + dens_out_d)
            		#for field in fieldMappings.fields:
           		#    if field.name not in ["OBJECTID","Shape","GRID_ID","traffic_dens","SEA_AREA","MMSI","path_len"]:
           		#        fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
            
            		# Join traf_date to traf_all	
			arcpy.JoinField_management (FileGDB_path + FileGDB_name + "\\" + traf_all, "OBJECTID", FileGDB_path + FileGDB_name + "\\" + dens_out_d, "OBJECTID",["traffic_dens"])
           
            		# rename traff_all traffic_dens field name to include date.
			arcpy.AlterField_management (FileGDB_path + FileGDB_name + "\\" + traf_all, "traffic_dens", "traf_"+str(traffic[i])[-29:-21], "traf_"+str(traffic[i])[-29:-21])          
            
            		# join traff_all to traf_dens
			arcpy.JoinField_management (FileGDB_path + FileGDB_name +"/" + traf_dens, "OBJECTID", FileGDB_path + FileGDB_name + "\\" + traf_all, "OBJECTID",["traf_"+str(traffic[i])[-29:-21]])
            
            		# Calculate updated traf_dens
			temp = "traf_"+str(traffic[i])[-29:-21]
			calcString = "!traffic_dens! + !traf_"+str(traffic[i])[-29:-21]+"!"
			arcpy.CalculateField_management(FileGDB_path + FileGDB_name +"/" + traf_dens,"traffic_dens", calcString, 'PYTHON3')
                                                                                  
            		# tidy up fields within traf_dens
			arcpy.DeleteField_management (FileGDB_path + FileGDB_name +"/" + traf_dens, ["cell_area", "Crop_A",temp])
                
			print("5b")
		i=i+1
    
    
	Traf_dens = FileGDB_path + FileGDB_name +"/" + traf_dens
	print(Traf_dens)
	print("done") 
	return Traf_dens, out_date
            




