#!/usr/bin/env python

############################################
# Module to prepare the folder structure for processing with gamma
############################################

import os
import sys
import glob
import re

# get all the zip files
from typing import List

zips = [x for x in os.listdir("../data") if x.endswith(".zip")]
# get all the dates
dates = []
for date in zips:
    # match the first date in the zip files
    m = re.match(".*__1SDV_(\d{4})(\d{2})(\d{2})", date)
    d = m.groups()
    d_str = ''.join(d)
    dates.append(d_str)

# make a list for summer and one for winter ??
summer = []
winter = []
for d in dates:
    if int(d[4:6]) in [12,1,2]:
        winter.append(d)
    else:
        summer.append(d)

# print("Winter Dates")
# [print(i) for i in summer]
# print(" ")
# print("Summer Dates")
# [print(i) for i in winter]



# for every date in the summer
date_combs_summer = []
for d in summer:
    # get the year
    year = int(d[0:4])
    for o in summer:
        # for every other date check if the year is the same
        if o != d:
            year_o = int(o[0:4])
            if  year_o == year:
                mas = min(int(d), int(o))
                sl = max(int(d), int(o))
                dir = str(mas) + "_" + str(sl)

                # will produce the double amount
                if not dir in date_combs_summer:
                    date_combs_summer.append(dir)

print("Summer Combinations")
sorted_date_combs_summer = sorted(date_combs_summer)
print(sorted_date_combs_summer)


# for every date in the winter
date_combs_winter = []
for d in winter:
    # get the year
    year = int(d[0:4])
    for o in winter:
        # for every other date check if the year is the same
        if o != d:
            year_o = int(o[0:4])
            if  year_o == year:
                mas = min(int(d), int(o))
                sl = max(int(d), int(o))
                dir = str(mas) + "_" + str(sl)

                # will produce the double amount
                if not dir in date_combs_winter:
                    date_combs_winter.append(dir)


print("Winter Combinations")
sorted_date_combs_winter = sorted(date_combs_winter)
print(sorted_date_combs_winter)

# add them both to one list

#####################################################
# Create Directories
# TODO: Agree on Structure
# data
# |- Summer
#   |- Intensity
#       |-dates....
#   |- Phase
#       |-dates....
# |- Winter
#   |- Intensity
#       |-dates....
#   |- Phase
#       |-dates....


# check if structure not already exists
seasons = ["../data/summer", "../data/winter"]

# mode
modes = ["intensity", "phase"]

# create both if not existent
for s in seasons:
    if not os.path.isdir(s):
        for m in modes:
            # create combination folders
            if "summer" in s:
                if m == "phase":
                        print("==============================")
                        print("Creating Summer Phase directories: ")
                        print("==============================")
                        for d in sorted_date_combs_summer:
                            dirs = os.path.join(s, m, d)
                            print(dirs)
                            #os.makedirs(dirs)
                else:
                    print("==============================")
                    print("Creating Summer Intensity directories: ")
                    print("==============================")
                    for d in summer:
                        dirs = os.path.join(s, m, d)
                        print(dirs)
                        #os.makedirs(dirs)

            else:
                if m == "phase":
                    print("==============================")
                    print("Creating Winter Phase directories: ")
                    print("==============================")
                    for d in sorted_date_combs_winter:
                        dirs = os.path.join(s, m, d)
                        print(dirs)
                        #os.makedirs(dirs)
                else:
                    print("==============================")
                    print("Creating Winter Intesity directories: ")
                    print("==============================")
                    for d in winter:
                        dirs = os.path.join(s, m, d)
                        print(dirs)
                        # os.makedirs(dirs)

    else:
        print("Folder structure already exists")






