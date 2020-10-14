#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Import SLCs and DEM to GAMMA software within a given directory structure
#########################################################################

import os
import datetime as date
from glob import glob
import zipfile
import shutil
import tqdm
import re
import subprocess

# try importing gamma (only works when working on the server) --> So check if working on server
kernel = str(os.system("uname -r"))
print(kernel)
if kernel == "3.10.0-957.el7.x86_64":
    try:
        import py_gamma as pg
    except ImportError as err:
        print("The module `py_gamma` needs to be installed")
else:
    pass

# some colors
TGREEN = '\033[32m'  # Green Text
ENDC = '\033[m'

#########################################
# USER INPUT
#########################################

# directories
dir_data = "../data"
dir_slc = os.path.join(dir_data, "SLC")
dir_dem = os.path.join(dir_data, "DEM")
dem_name = "LMI_Haedarlikan_DEM_16bit_subset.tif"

# arg-parsing arguments
def get_arguments():
    pass

#########################################
# Unzip
#########################################

def S1_zip_finder(dir_data):
    """
    :param : s1dir
    :return:
    """
    safe_zips = glob(os.path.join(dir_data, "*.zip"))
    return safe_zips

def unzip(dir_data, out_dir):
    safe_zips = S1_zip_finder(dir_data)
    for f in safe_zips:
        # check if the unzipped file already exists
        safe = os.path.join(dir_data, os.path.splitext(os.path.basename(f))[0] + ".SAFE")
        if not os.path.isdir(safe):
            print(f)
            print("still needs to be extracted")
            # zf = zipfile.ZipFile(f)
            # uncompressed_size = sum((file.file_size for file in zf.infolist()))
            # extraced_size = 0
            # print("======")
            # print(TGREEN + "Extracting: {}".format(f) + ENDC)
            # print("======")
            # for file in zf.infolist():
            #     extraced_size += file.file_size
            #     print("{} %".format(extraced_size * 100/uncompressed_size))
            #     zf.extract(file, out_dir)
        else:
            print("already unzipped")


#########################################
# SLC_Import
#########################################

def get_dates(dir_data):
    """
    Funtion to exrtact the dates from the zip-filesnames and return them

    :param path to the directory with all the zip files:
    :return : a sorted dictionary in the form {i:('date_1', 'date_2')}
              The keys are numbered for as many pairs of scenes we do have
              The values are tuples holding the two dates as strings
    """

    # get all the dates
    zips = S1_zip_finder(dir_data)

    # get all the dates from the zip_files
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
        if int(d[4:6]) in [12, 1, 2]:
            winter.append(d)
        else:
            summer.append(d)

    # put the two lists into one list
    dates_total = [summer, winter]

    # dictionary that will hold for every interferometric pair the dates
    # dates_pairs = {i:None for i in range(1,11)}
    dates_pairs = []


    for s in dates_total:
        counter = 1
        for d in s:
            #print("Counter: ", counter)
            # get the year for the first one
            year = int(d[0:4])
            for o in s:
                # for every other date check if the year is the same
                if o != d:
                    year_o = int(o[0:4])
                    if year_o == year:
                        mas = min(int(d), int(o))
                        sl = max(int(d), int(o))
                        #dates_pairs[counter] = [str(mas), str(sl)]
                        date_intf = str(mas) + "_" + str(sl)
                        # will produce the double amount
                        if not date_intf in dates_pairs:
                            dates_pairs.append(date_intf)
            counter += 1

    # sort the list
    dates_pairs_sorted = sorted(dates_pairs)
    # make it a dictionary
    dates_dict = {x:None for x in range(1,11)}
    i = 0
    for k in dates_dict:
        dates_dict[k] = (dates_pairs_sorted[i][0:8], dates_pairs_sorted[i][9:17])
        i += 1
    return dates_dict

def make_base_paths(dates_pairs):
    """

    :param dates_pairs: a dictionary with the values beeing the dates for each interferometric pair
    :return: a dictionary with the keys beeing the number of the interferometric pair and the
              values beeing the paths of the .SAFE-files
    """

    # create dictionary with keys(number of pair), value(SAFE-PATHS)
    basenames = {x:None for x in range(1,11)}
    # iterate over the dates_pats dictionary
    for i,int_pair in enumerate(dates_pairs, start = 1):
        # becuase the numbering in the dictionary is from 1:10 and not 0:9
        paths = []
        for date in dates_pairs[i]:
            # for ever file (directory) check if the date is in the name
            for file in os.listdir(dir_data):
                # file needs to end with .SAFE
                if file.endswith(".SAFE"):
                    # if file contains the actual date
                    if date in file:
                        # get only the basename
                        paths.append(file)
        basenames[i] = paths
    return basenames

def import_scene(safe_folder, sw = "iw2", pol = "vv", *swaths):
    """

    :param safe_folder: path to the SAFE-folder that is going to be imported
    :param swaths: list os subswaths to import
    :return: None
    """
    if not swaths:

        print("=====")
        print("only importing subswath 2")
        print("=====")

        # finding tiff
        findCMD = 'find {safe_folder} -name "*.tiff" | grep {pol} | grep {sw}'.format(safe_folder=safe_folder, pol=pol,sw=sw)
        out = subprocess.Popen(findCMD, shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = out.communicate()
        tiff = stdout.decode().split()

        # finding annotation file
        findCMD = 'find {safe_folder} -name "s1a-*.xml" | grep {pol} | grep {sw}'.format(safe_folder=safe_folder, pol=pol,
                                                                                      sw=sw)
        out = subprocess.Popen(findCMD, shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = out.communicate()
        ann = stdout.decode().split()

        # find calibration file
        findCMD = 'find {safe_folder} -name "calibration-s1a-*.xml" | grep {pol} | grep {sw}'.format(safe_folder=safe_folder,
                                                                                         pol=pol,
                                                                                         sw=sw)
        out = subprocess.Popen(findCMD, shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = out.communicate()
        cal = stdout.decode().split()

        # find noise file
        findCMD = 'find {safe_folder} -name "noise-s1a-*.xml" | grep {pol} | grep {sw}'.format(safe_folder=safe_folder,
                                                                                         pol=pol,
                                                                                         sw=sw)
        out = subprocess.Popen(findCMD, shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = out.communicate()
        noi = stdout.decode().split()

        # create the .slc and the .slc.par
        slc_name = os.path.splitext(os.path.basename(safe_folder))[0] + ".slc"
        slc_par_name = slc_name + ".par"
        print(TGREEN + "======= Creating: =========" + ENDC)
        print(TGREEN + "{} \n{}".format(slc_name, slc_par_name) + ENDC)



    else:
        print(swaths)



def slc_import(dir_data):
    # dates_pairs = get_dates(dir_data)
    # safe_paths_dir = make_base_paths(dates_pairs)
    import_scene("../data/S1A_IW_SLC__1SDV_20160112T184956_20160112T185023_009465_00DBA0_0436.SAFE")

#########################################
# DEM_Import
#########################################

def dem_import(dir_dem, dem_name):
    """
    Importing national icelandic DEM to GAMMA
    :param dir_dem: Directory containing the unzipped DEM which overlaps with the SLC at least in the areas of interest
    :param dem_name: Full name of the DEM
    :return: None, printing GAMMA output to console
    """

    dem = os.path.join(dir_dem, dem_name)
    out = os.path.join(dir_dem, "DEM")
    out_par = os.path.join(dir_dem, "DEM.par")

    print(out)
    pg.dem_import(dem, out, out_par)

    # TODO: print size of the DEM from par-file
    with open(out_par) as f:
        lines = f.readlines()
        if re.search("width", lines):
            dem_width = lines
        if re.search("lines", lines):
            dem_lines = lines
        print("Width: ", dem_width, "\n",
              "Lines: ", dem_lines, "\n")
        f.close()

def main():

    # TODO: Wenn wir die pfadvariablen oben global definieren, dann brauchen wir sie wahrscheinlich hier unter nicht
    # TODO: Nochmal alsarguemte oder?


    #unzip(dir_data, dir_data)
    slc_import(dir_data)
    #dem_import(dir_dem, "LMI_Haedarlikan_DEM_16bit_subset.tif")


if __name__ == "__main__":
    main()
