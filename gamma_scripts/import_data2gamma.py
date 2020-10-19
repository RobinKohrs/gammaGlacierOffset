#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Import SLCs and DEM to GAMMA software within a given directory structure
#########################################################################
import os
from glob import glob
import zipfile
import re
from functions import rec_reg
import argparse

##################
# parse option to work locally or on server
##################

# parse some arguments
parser = argparse.ArgumentParser(description="Decide whether you are executing this locally (-l) or on the server (-s) and which steps to perform")
# get positional arguments
parser.add_argument("-l", "--print", dest="print", help="only print cmd call", action="store_const", const=True)

parser.add_argument("-s", "--step", dest="steps",
                    help="(input) which step to perform unzip (0), slc-import (1), dem_import (2)", default=0,
                    nargs="+", type=int)

parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)


# get the arguments
global args
args = parser.parse_args()
print(args)
if not args.m == "s":
    print("working locally...")
else:
    try:
        import py_gamma as pg
        print("working on the server...")
    except ImportError as err:
        print("Working on the server...")
        print("However the py_gamma-module can not be loaded...")
        print("Make sure its on $PATH? or PYTHONPATH?")
        exit(-1)

#############
# some preparation
#############
TGREEN = '\033[32m'  # Green Text
ENDC = '\033[m'
TRED = "\u001b[41;1m"
TYEL = "\u001b[33;1m"
start_bold = "\033[1m"
end_bold = "\033[0;0m"
start_underline = "\033[4m"
end_underline = "\033[0m"

# get dimensions of terminal
r_t, c_t = os.popen('stty size', 'r').read().split()
r_t, c_t = int(r_t), int(c_t)


############
# directories
############

dir_data = "../data"
dir_slc = os.path.join(dir_data, "SLC")
dir_dem = os.path.join(dir_data, "DEM")
dem_name = "Island_DEM_WGS84.vrt"

#######
# Unzip
#######

def S1_zip_finder(dir_data):
    """
    :param : s1dir
    :return:
    """
    safe_zips = glob(os.path.join(dir_data, "*.zip"))
    return safe_zips

def unzip(dir_data, out_dir):

    print()
    print("#" * (c_t // 3) + "   UNZIPPING  " + "#" * (c_t // 3))
    print()

    safe_zips = S1_zip_finder(dir_data)

    for f in safe_zips:
        # check if the unzipped file already exists
        safe = os.path.join(dir_data, os.path.splitext(os.path.basename(f))[0] + ".SAFE")
        if not os.path.isdir(safe):
            print(f)
            print("still needs to be extracted")
            zf = zipfile.ZipFile(f)
            uncompressed_size = sum((file.file_size for file in zf.infolist()))
            extraced_size = 0
            print("======")
            print(TGREEN + "Extracting: {}".format(f) + ENDC)
            print("======")
            for file in zf.infolist():
                extraced_size += file.file_size
                print("{} %".format(extraced_size * 100/uncompressed_size))
                zf.extract(file, out_dir)
        else:
            print(f)
            print("already unzipped")


#########################################
# SLC_Import
#########################################


def import_scene(safe_folder, sw = "iw2", pol = "vv", *swaths):
    """

    :param safe_folder: path to the SAFE-folder that is going to be imported
    :param swaths: list os subswaths to import
    :return: None
    """
    if not swaths:
        print()
        print("#"*(c_t//3) + "   IMPORT SLC  " + "#"*(c_t//3))
        print()
        print("=====")
        print("Only importing subswath 2")
        print("=====")
        print()

        m = re.match(".*__1SDV_(\d{4})(\d{2})(\d{2})", safe_folder)
        d = m.groups()
        date_str = ''.join(d)

        slc = rec_reg(safe_folder, ".*iw2.*-vv-{date}.*\.tiff$".format(date=date_str))[0]
        ann = rec_reg(safe_folder, "^s1a.*iw2.*-vv-{date}.*\.xml".format(date=date_str))[0]
        cal = rec_reg(safe_folder, "^cali.*iw2.*-vv-{date}".format(date=date_str))[0]
        noi = rec_reg(safe_folder, "^noi.*iw2.*-vv-{date}".format(date=date_str))[0]

        print(start_bold + start_underline +"Processing SAFE:\n"+ end_bold + end_underline,
              TYEL + safe_folder + ENDC)
        print()
        print(start_bold + start_underline + "Found the following ancillary files" + end_bold + end_underline)
        print("SLC:\n" + ENDC, slc)
        print("Annotation:\n" + ENDC, ann)
        print("Calibaration:\n" + ENDC, cal)
        print("Noise:\n" + ENDC, noi)
        print()

        # create the .slc and the .slc.par
        # slc_name = os.path.join(dir_slc, os.path.splitext(os.path.basename(safe_folder))[0] + "_" + pol + "_" + sw + ".slc")
        # slc_par_name = slc_name + ".par"
        # slc_tops_name = slc_name + ".tops"
        # print(TGREEN + start_underline + "Creating:" + ENDC + end_underline)
        # print(TGREEN + "{} \n{}\n{}".format(slc_name, slc_par_name, slc_tops_name) + ENDC)

        # create the .slc and the .slc.par
        slc_name = os.path.join(dir_slc,
                                os.path.splitext(os.path.basename(safe_folder))[0] + "_" + pol + "_" + sw + ".slc")
        slc_par_name = slc_name + ".par"
        slc_tops_name = slc_name + ".tops"
        print(TGREEN + start_underline + "Creating:" + ENDC + end_underline)
        print(TGREEN + "{} \n{}\n{}".format(slc_name, slc_par_name, slc_tops_name) + ENDC)

        # execute the pygamma command
        cmd = "par_S1_SLC {slc} {ann} {cal} {noi} {slc_par} {slc_file} {slc_tops_par} - - -".format(slc=slc, ann=ann, cal=cal,
                                                                                           noi=noi, slc_par=slc_par_name,
                                                                                           slc_file=slc_name, slc_tops_par=slc_tops_name)
        
        os.system(cmd) if not args.m == "l" else print(TRED + "working locally. Not calling pygamma" + ENDC)

    else:
        print(swaths)

def slc_import(dir_data, test=True, num_scenes=2):
    safes = [os.path.join(dir_data, x) for x in os.listdir(dir_data) if x.endswith(".SAFE")]
    if test:
        print()
        print(start_bold + start_underline + TRED + "ONLY TESTING THE IMPORT" + ENDC)
        for i, s in enumerate(safes, start=1):
            if i == num_scenes:
                print(TRED + "===== ABORTING ====" + ENDC)
            import_scene(s)
    else:
        for s in safes:
            import_scene(s)

#########################################
# DEM_Import
#########################################

def dem_import(dir_dem, dem_name, test=True):
    """
    Importing national icelandic DEM to GAMMA
    :param dir_dem: Directory containing the unzipped DEM which overlaps with the SLC at least in the areas of interest
    :param dem_name: Full name of the DEM
    :return: None, printing GAMMA output to console
    """

    # TODO: Change CRS to WGS84

    dem = os.path.join(dir_dem, dem_name)
    out = os.path.join(dir_dem, "DEM")
    out_par = os.path.join(dir_dem, "DEM.par")

    print()
    print("#" * (c_t // 3) + "   IMPORTING DEM  " + "#" * (c_t // 3))

    print(start_underline + "Woring with DEM:\n" + end_underline,
          dem)
    print()
    print(TGREEN + start_underline + "Creating DEM-File" + end_underline)
    print(TGREEN + out + ENDC)
    print()
    print(TGREEN + start_underline + "Creating DEM-Parameter-File" + end_underline)
    print(TGREEN + out_par + ENDC)

    if not test:
        pg.dem_import(dem, out, out_par)
    else:
        print(start_bold + start_underline + TRED + "ONLY TESTING THE DEM IMPORT" + ENDC)

def main():
    for step in sorted(args.steps):
        if int(step) == 0:
            unzip(dir_data, dir_data)
        elif int(step) == 1:
            slc_import(dir_data) if not args.m == "s" else slc_import(dir_data, test=False)
        elif int(step) == 2:
            dem_import(dir_dem, dem_name) if not args.m == "s" else dem_import(dir_dem, dem_name, test=False)

if __name__ == "__main__":
    main()
