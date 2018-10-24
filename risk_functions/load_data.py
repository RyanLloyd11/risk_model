#!/usr/bin/python

# THIS IS A MODULE
import pandas
import os



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

    
# Define a function  
def loadincidents(root,file):
# Fucntion to load in incidents data. RJL - 23/10/2018
	file_list = []
	with open(file, "r") as f:
		file_list = f.read().split()
	for f in file_list:
		A = os.path.join(root,f)  
		globals()["incidents_" + str(A[-10:-4])]=  pandas.read_csv(A,header=None,low_memory=False)
