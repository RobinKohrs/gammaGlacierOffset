#!/usr/bin/env python

############################################
# Module to prepare the folder structure for processing with gamma
############################################

import os
import re
import argparse
from functions import *
from datetime import date

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


def get_directories():
    pass

def make_folder_struc(data_dir = "../data",
                      slc_dir = "../data/SLC",
                      dem_dir = "../data/DEM",
                      dir_tuples = "../data/tuples"):

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
                if abs((i-j).days) < 13:
                    if i < j:

                        main = "".join(str(i).split("-"))
                        second = "".join(str(j).split("-"))
                        tuple = main + "_" + second
                        date_combs.append(tuple)

    # this modifies the actual element date_combs
    date_combs.sort()

    # # make a list for summer and one for winter ??
    # summer = []
    # winter = []
    # for d in dates:
    #     if int(d[4:6]) in [12,1,2]:
    #         winter.append(d)
    #     else:
    #         summer.append(d)
    #
    # # for every date in the summer
    # date_combs_summer = []
    # for d in summer:
    #     # get the year
    #     year = int(d[0:4])
    #     for o in summer:
    #         # for every other date check if the year is the same
    #         if o != d:
    #             year_o = int(o[0:4])
    #             if year_o == year:
    #                 mas = min(int(d), int(o))
    #                 sl = max(int(d), int(o))
    #                 dir = str(mas) + "_" + str(sl)
    #
    #                 # will produce the double amount
    #                 if not dir in date_combs_summer:
    #                     date_combs_summer.append(dir)
    #
    # # print("Summer Combinations")
    # sorted_date_combs_summer = sorted(date_combs_summer)
    # # print(sorted_date_combs_summer)
    #
    #
    # # for every date in the winter
    # date_combs_winter = []
    # for d in winter:
    #     # get the year
    #     year = int(d[0:4])
    #     for o in winter:
    #         # for every other date check if the year is the same
    #         if o != d:
    #             year_o = int(o[0:4])
    #             if year_o == year:
    #                 mas = min(int(d), int(o))
    #                 sl = max(int(d), int(o))
    #                 dir = str(mas) + "_" + str(sl)
    #
    #                 # will produce the double amount
    #                 if not dir in date_combs_winter:
    #                     date_combs_winter.append(dir)
    #
    #
    # # print("Winter Combinations")
    # sorted_date_combs_winter = sorted(date_combs_winter)
    # # print(sorted_date_combs_winter)
    #
    # # add them both to one list
    # comb_dates_all = sorted_date_combs_summer + sorted_date_combs_winter
    # print(comb_dates_all)
    # print()
    # print("There are {} pairs".format(len(comb_dates_all)))
    # print()


    modes = ["intensity", "fringe"]

    # create subdirectory for all files that come in tuples
    tuple_dir = dir_tuples; os.makedirs(tuple_dir) if not os.path.isdir(tuple_dir) else print(".....")

    # create both if not existent
    for d in date_combs:
        for m in modes:
            dirs = os.path.join(tuple_dir,d, m)
            if args.print:
                print("-----------------------------")
                print("Creating Tuple Directory: {}".format(dirs),end="")
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
    #data_dir, slc_dir, dem_dir, tuples_dir = get_directories()
    make_folder_struc()



if __name__ == "__main__":
    main()





