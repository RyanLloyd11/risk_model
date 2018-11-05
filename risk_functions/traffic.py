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

