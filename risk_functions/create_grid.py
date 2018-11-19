#!/usr/bin/python

import os
import arcpy

# RJL - 29/10/2018i

# -------------------------------------------

# Create grid using tessllation
# RJL - 02/11/18



def tes_grid(root,gdb,traffic,continent, G_extent, sp_ref, SIZE, SHAPE):

	extent = arcpy.Extent(G_extent[3], G_extent[2], G_extent[1], G_extent[0]) #{XMin}, {YMin}, {XMax}, {YMax}
	GRIDS = []
	for f in traffic:
		OP_NAME = str(f)[len(str(root)):len(str(root))+3]+ str(SIZE) + SHAPE[:2] + "_grid_all"
		OP_NAME2 = str(f)[len(str(root)):len(str(root))+3]+ str(SIZE) + SHAPE[:2] + "_grid_land"
		OP_NAME3 = str(f)[len(str(root)):len(str(root))+3]+ str(SIZE)+ SHAPE[:2] + "_grid_sea"
		if not arcpy.Exists(root+gdb + "/" +OP_NAME):
			# Generate 1st tess
			arcpy.GenerateTessellation_management(root+gdb + "/" +OP_NAME, extent, SHAPE, str(SIZE) + " SquareKilometers", sp_ref)
			arcpy.AddField_management(root+gdb + "/" +OP_NAME, "Crop_A", "FLOAT")
			arcpy.CalculateField_management(root+gdb + "/" +OP_NAME,"Crop_A", "0", 'PYTHON3')

		if not arcpy.Exists(root+gdb + "/" +OP_NAME2):
			# Generate crop tess
			arcpy.Clip_analysis(root+gdb+"/"+OP_NAME, continent, root+gdb+"/"+OP_NAME2)
			arcpy.AddField_management(root+gdb+"/"+OP_NAME2, "Crop_A", "FLOAT")
			arcpy.CalculateField_management(root+gdb+"/"+OP_NAME2,"Crop_A", "!shape.area!", 'PYTHON3')

		if not arcpy.Exists(root+gdb + "/" +OP_NAME3):
			# UPDATE
			arcpy.Update_analysis(root+gdb+"/"+OP_NAME, root+gdb+"/"+OP_NAME2, root+gdb+"/"+OP_NAME3)

			arcpy.AddField_management(root+gdb+"/"+OP_NAME3, "cell_area", "FLOAT")
			arcpy.CalculateField_management(root+gdb+"/"+OP_NAME3,"cell_area", "!shape.area!", 'PYTHON3')
			arcpy.AddField_management(root+gdb+"/"+OP_NAME3, "SEA_AREA", "FLOAT")
			arcpy.CalculateField_management(root+gdb+"/"+OP_NAME3,"SEA_AREA", "!cell_area!-!Crop_A!", 'PYTHON3')
		GRIDS.append(root+gdb+"/"+OP_NAME3)
	return GRIDS
	print("Complete")




# ----------------------------------------------------------

# Create fishnet of squares

	# OBSOLETE #

# ISSUES:
# 29/10/18 - RJL: Does f in createFishnet define base units? arcpy.env.outputCoordinateSystem = coordinate_system
# 29/10/18 - RJL: Naming will not work if fishnet size has a "."
# 02/11/18 - RJL: Merge creates twp entries for onland cells, and !S_AREA!-!shape.area! does not equal 0 for land cells. 

def sq_fishnet(root,gdb, traffic, fn_extent, fishnet_size, continents):
	N = fn_extent[0]
	E = fn_extent[1]
	S = fn_extent[2]
	W = fn_extent[3]
	#arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("GCS_WGS_1984")
	arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(4326)	

	for f in traffic:
		OP_NAME = str(f)[len(str(root)):len(str(root))+3]+ str(fishnet_size[0]) + "_fishnet_tmp"
		OP_NAME2 = str(f)[len(str(root)):len(str(root))+3]+ str(fishnet_size[0]) + "_fishnet_clip"
		OP_NAME3 = str(f)[len(str(root)):len(str(root))+3]+ str(fishnet_size[0]) + "_fishnet_seaarea"
		if not arcpy.Exists(root+gdb+"/" + OP_NAME): 
			arcpy.CreateFishnet_management(root+gdb+"/" + OP_NAME,str(W) +" "+str(S),str(W) +" "+ str(N),fishnet_size[0],fishnet_size[1],"0","0",str(E)+" "+ str(N),"NO_LABELS","","POLYGON")
    			# Create new attribute           
			arcpy.AddField_management(root+gdb+"/"+OP_NAME, "S_AREA", "FLOAT")#,"","5","","","NULLABLE","REQUIRED", "") 
			# Give new attribute shape area value           
			arcpy.CalculateField_management(root+gdb+"/" + OP_NAME,"S_AREA", "!shape.area!")
			# Clip GoG_FN to continents
		if not arcpy.Exists(root + OP_NAME2):
			arcpy.Clip_analysis(root+gdb+"/"+OP_NAME, continents, root+gdb+"/"+OP_NAME2)           
			# Create new field to clipped fishnet 
			arcpy.AddField_management(root+gdb+"/"+OP_NAME2, "SEA_AREA", "FLOAT")#,"","5","","","NULLABLE","REQUIRED", "")    
			# Find Sea Area (difference between clipped)
			arcpy.CalculateField_management(root+gdb+"/"+OP_NAME2,"SEA_AREA", "!S_AREA!-!shape.area!")
			# Add SEA_AREA to first fishnet
			arcpy.AddField_management(root+gdb+"/"+OP_NAME, "SEA_AREA", "FLOAT")#,"","5","","","NULLABLE","REQUIRED", "")
			arcpy.CalculateField_management(root+gdb+"/" + OP_NAME,"SEA_AREA", "!shape.area!")
			# Merge datasets
		if not arcpy.Exists(root + OP_NAME3):
			arcpy.Merge_management([root+gdb+"/"+OP_NAME2,root+gdb+"/"+OP_NAME],root+gdb+"/"+OP_NAME3, "First") 
			print(OP_NAME3+ " created")        
	print("Complete") 
                

