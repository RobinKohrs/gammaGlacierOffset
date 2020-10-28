#!/usr/bin/env python

############################################
# Module to prepare the folder structure for processing with gamma
############################################

import os
import sys
import glob
import re
import argparse

##################
# parse option to work locally or on server
##################

# parse some arguments
parser = argparse.ArgumentParser(description="Decide whether you want to print the folder structur or create it")
# get positional arguments
parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)
args =parser.parse_args()


# parse the arguments in a list
args = parser.parse_args()

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

# for every date in the summer
date_combs_summer = []
for d in summer:
    # get the year
    year = int(d[0:4])
    for o in summer:
        # for every other date check if the year is the same
        if o != d:
            year_o = int(o[0:4])
            if year_o == year:
                mas = min(int(d), int(o))
                sl = max(int(d), int(o))
                dir = str(mas) + "_" + str(sl)

                # will produce the double amount
                if not dir in date_combs_summer:
                    date_combs_summer.append(dir)

# print("Summer Combinations")
sorted_date_combs_summer = sorted(date_combs_summer)
# print(sorted_date_combs_summer)


# for every date in the winter
date_combs_winter = []
for d in winter:
    # get the year
    year = int(d[0:4])
    for o in winter:
        # for every other date check if the year is the same
        if o != d:
            year_o = int(o[0:4])
            if year_o == year:
                mas = min(int(d), int(o))
                sl = max(int(d), int(o))
                dir = str(mas) + "_" + str(sl)

                # will produce the double amount
                if not dir in date_combs_winter:
                    date_combs_winter.append(dir)


# print("Winter Combinations")
sorted_date_combs_winter = sorted(date_combs_winter)
# print(sorted_date_combs_winter)

# add them both to one list
comb_dates_all = sorted_date_combs_summer + sorted_date_combs_winter
print(comb_dates_all)
print()
print("There are {} pairs".format(len(comb_dates_all)))
print()

# mode
modes = ["intensity", "fringe"]

# create subdirectory for all files that come in tuples
tuple_dir = "../data/tuples"; os.makedirs(tuple_dir) if not os.path.isdir(tuple_dir) else print(".....")

# create both if not existent
for d in comb_dates_all:
    for m in modes:
        dirs = os.path.join(tuple_dir,d, m)
        if args.print:
            print("-----------------------------")
            print("Creating Tuple Directory: {}".format(dirs))
            print("-----------------------------")
        else:
            print("-----------------------------")
            print("Creating Tuple Directory: {}".format(dirs))
            print("-----------------------------")
            os.makedirs(dirs, exist_ok=True)


###########################
# Create directories for DEM and SLCs
###########################
aux_dirs = ["../data/DEM", "../data/SLC"]
for dir in aux_dirs:
    if not os.path.isdir(dir):
        print("==========")
        print("Creating Directory \n {}".format(dir))
        print("==========")
        if args.print:
            os.makedirs(dir, exist_ok=True)
        else:
            pass







