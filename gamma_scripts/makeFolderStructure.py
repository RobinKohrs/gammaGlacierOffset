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

#####################################################
# Create Directories
# TODO: Combine Structure
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
dir_summer = "../data/Summer"
dir_winter = "../data/Winter"

# mode
modes = ["intensity", "phase"]

# create two dictionaries that will hold the year (key) and the date1_date2 (value)
summer_combs = {}
for d in summer:
    y = d[0:4]
    if y not in summer_combs:
        summer_combs[y] = None

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




winter_combs = {}
for d in winter:
    y = d[0:4]
    if y not in summer_combs:
        winter_combs[y] = None

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


# create both if not existent
if not os.path.isdir(dir_summer):
    pass
if not os.path.isdir(dir_winter):
    print("Createing directory \n"
          "{}".format(dir_winter))
    os.makedirs(dir_winter)





