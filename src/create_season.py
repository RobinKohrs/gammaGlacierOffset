#!/usr/bin/env python

###################################
#  script to initiate the processing of the timeseries 
###################################

import shutil
import os
import sys
import glob
import getpass
import subprocess

# get the userinput
# usr=input("Your USGS Username: ")
# passwd=getpass.getpass("Your USGS Password: ")
print("\n")
print(TGREEN + "Starting the to setup the seasons-project" + ENDC)

# grab the download timeseries file
download_dir = [x for x in os.listdir("../") if "download" in x][0]
path = os.path.join("../", download_dir)
file=[os.path.join(path, x) for x in os.listdir(path) if "2020" in x][0]

# create the data dir
datadir = "../data"
if not os.path.isdir(datadir):
    print("Create the data directory")
    os.makedirs(datadir)
else:
    print("data directory already exists")

# move the download file in the data directory
shutil.copy(src = file, dst=datadir)
file_dst = os.path.join(datadir, "2020_download.py")

print("Now you have to move to the ../data directory and run the python file that will download the data from ASF\n")


