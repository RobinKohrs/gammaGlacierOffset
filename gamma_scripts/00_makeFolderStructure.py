#!/usr/bin/env python

############################################
# Module to prepare the folder structure for processing with gamma
############################################

import argparse
from datetime import date

from functions import *

##################
# parse option to work locally or on server
##################

# parse some arguments
parser = argparse.ArgumentParser(description="Decide whether you want to print the folder structur or create it")
# get positional arguments
parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)
args = parser.parse_args()

# parse the arguments in a list
args = parser.parse_args()


def get_directories():
    pass


def make_folder_struc(data_dir="../data",
                      slc_dir="../data/SLC",
                      dem_dir="../data/DEM",
                      dir_tuples="../data/tuples"):
    """
    Function to create the Folder Structure

    :param data_dir: Directory with all the Zip-files
    :param slc_dir: Directory where all "single-date" data will be stored
    :param dem_dir: Directory where all DEM-related data will be stored
    :param tuples_dir: Directory where all "dual-date"-data will be stored
    :return:
    """
    
    zips = [x for x in os.listdir(data_dir) if x.endswith(".zip")]
    # get all the dates
    dates = []
    for d in zips:
        # match the first date in the zip files
        m = re.match(".*__1SDV_(\d{4})(\d{2})(\d{2})", d)
        da = m.groups()
        d_str = ''.join(da)
        dt = date(year=int(d_str[0:4]), month=int(d_str[4:6]), day=int(d_str[6:8]))
        dates.append(dt)
    
    date_combs = []
    for i in dates:
        for j in dates:
            if i != j:
                if abs((i - j).days) < 13:
                    if i < j:
                        main = "".join(str(i).split("-"))
                        second = "".join(str(j).split("-"))
                        tuple = main + "_" + second
                        date_combs.append(tuple)
    
    # this modifies the actual element date_combs
    date_combs.sort()
    
    modes = ["intensity", "fringe"]
    
    # create subdirectory for all files that come in tuples
    tuple_dir = dir_tuples;
    os.makedirs(tuple_dir) if not os.path.isdir(tuple_dir) else print(".....")
    
    # create both if not existent
    for d in date_combs:
        for m in modes:
            dirs = os.path.join(tuple_dir, d, m)
            if args.print:
                print("-----------------------------")
                print("Creating Tuple Directory: {}".format(dirs), end="")
                print("  " + TRED + "<-- Already Exists" + ENDC) if os.path.isdir(dirs) else print()
                print("-----------------------------")
            else:
                print("-----------------------------")
                print("Creating Tuple Directory: {}".format(dirs))
                print("  " + TRED + "<-- Already Exists" + ENDC) if os.path.isdir(dirs) else print()
                print("-----------------------------")
                os.makedirs(dirs) if not os.path.isdir(dirs) else print()
    
    ###########################
    # Create directories for DEM and SLCs
    ###########################
    aux_dirs = [dem_dir, slc_dir]
    for dir in aux_dirs:
        if args.print:
            print("==========")
            print("Creating Directory \n {}".format(dir), end="")
            print("  " + TRED + "<-- Already exists" + ENDC) if os.path.isdir(dir) else print()
            print("==========")
        else:
            print("==========")
            print("Creating Directory \n {}".format(dir))
            print("  " + TRED + "<-- Already exists (not creating)" + ENDC) if os.path.isdir(dir) else print()
            print("==========")
            os.makedirs(dir) if not os.path.isdir(dir) else print()


def main():
    # data_dir, slc_dir, dem_dir, tuples_dir = get_directories()
    make_folder_struc(data_dir="../data",
                      slc_dir="../data/SLC",
                      dem_dir="../data/DEM",
                      dir_tuples="../data/tuples")


if __name__ == "__main__":
    main()
