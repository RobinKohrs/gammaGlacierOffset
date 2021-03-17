#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Import SLCs and DEM to GAMMA software within a given directory structure
#########################################################################
import os
from glob import glob
import zipfile
import re
from functions import *
import argparse

##################
# parse option to work locally or on server
##################

# parse some arguments
parser = argparse.ArgumentParser(description="")
# get positional arguments
parser.add_argument(
    "-s",
    "--step",
    dest="steps",
    help="(input) which step to perform unzip (0), slc-import (1), dem_import (2)",
    default=0,
    nargs="+",
    type=int,
)

parser.add_argument(
    "-p",
    "--print",
    dest="print",
    help="only print cmd call",
    action="store_const",
    const=True,
)

parser.add_argument(
    "-sw",
    "--swaths",
    dest="swaths",
    help="Which swaths to use?",
    nargs="+",
    default=[2],
    type=int,
)
parser.add_argument(
    "-pol",
    "--polarizations",
    dest="pols",
    help="Which polarizations to use?",
    nargs="+",
    default=["vv"],
    type=str,
)


# get dimensions of terminal
r_t, c_t = os.popen("stty size", "r").read().split()
r_t, c_t = int(r_t), int(c_t)

############
# directories
############

dir_data = "../data"
dir_slc = os.path.join(dir_data, "SLC")
dir_dem = os.path.join(dir_data, "DEM")
dem_name = "dem_gamma_wgs84.vrt"

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
        safe = os.path.join(
            dir_data, os.path.splitext(os.path.basename(f))[0] + ".SAFE"
        )
        if not os.path.isdir(safe):
            print(f)
            print("still needs to be extracted")
            zf = zipfile.ZipFile(f)
            uncompressed_size = sum((file.file_size for file in zf.infolist()))
            extraced_size = 0
            print("======")
            print(TGREEN + "Extracting: {}".format(f) + ENDC)
            print("======")
            if not args.print:
                for file in zf.infolist():
                    extraced_size += file.file_size
                    print("{} %".format(extraced_size * 100 / uncompressed_size))
                    zf.extract(file, out_dir)
            else:
                print("....")
        else:
            print(f)
            print("already unzipped")


#########################################
# SLC_Import
#########################################


def import_scene(safe_folder):
    """

    :param safe_folder: path to the SAFE-folder that is going to be imported
    :param swaths: list os subswaths to import
    :return: None
    """

    # which subswaths to import?
    if len(args.swaths) == 1:
        if args.swaths[0] == 1:
            sw = ["iw1"]
        elif args.swaths[0] == 2:
            sw = ["iw2"]
        else:
            sw = ["iw3"]

    elif len(args.swaths) == 2:
        if 1 in args.swaths and 2 in args.swaths:
            sw = ["iw1", "iw2"]
        elif 3 in args.swaths and 2 in args.swaths:
            sw = ["iw3", "iw2"]
        else:
            sw = ["iw3", "iw1"]
    else:
        sw = ["iw1", "iw2", "iw3"]

    # get pol TODO: make work for more polarizations?
    pol = args.pols

    if len(sw) == 1 and len(pol) == 1:
        print()
        print("#" * (c_t // 3) + "   IMPORT SLC  " + "#" * (c_t // 3))
        print()
        print("=====")
        print("Only importing subswath {}".format(sw[0]))
        print("=====")
        print(safe_folder)

        m = re.match(".*__1SDV_(\d{4})(\d{2})(\d{2})", safe_folder)
        d = m.groups()
        date_str = "".join(d)

        slc = rec_reg(
            safe_folder,
            ".*{sw}.*-{pol}-{date}.*\.tiff$".format(
                sw=sw[0], pol=pol[0], date=date_str
            ),
        )[0]
        ann = rec_reg(
            safe_folder,
            "^s1[ab].*{sw}.*-{pol}-{date}.*\.xml".format(
                sw=sw[0], pol=pol[0], date=date_str
            ),
        )[0]
        cal = rec_reg(
            safe_folder,
            "^cali.*{sw}.*-{pol}-{date}".format(sw=sw[0], pol=pol[0], date=date_str),
        )[0]
        noi = rec_reg(
            safe_folder,
            "^noi.*{sw}.*-{pol}-{date}".format(sw=sw[0], pol=pol[0], date=date_str),
        )[0]

        print(
            start_bold
            + start_underline
            + "Processing SAFE:\n"
            + end_bold
            + end_underline,
            TYEL + safe_folder + ENDC,
        )
        print()
        print(
            start_bold
            + start_underline
            + "Found the following ancillary files"
            + end_bold
            + end_underline
        )
        print("SLC:\n" + ENDC, slc)
        print("Annotation:\n" + ENDC, ann)
        print("Calibaration:\n" + ENDC, cal)
        print("Noise:\n" + ENDC, noi)
        print()

        # create the .slc and the .slc.par
        slc_name = os.path.join(dir_slc, date_str + "_" + pol[0] + "_" + sw[0] + ".slc")
        slc_par_name = slc_name + ".par"
        slc_tops_par = slc_name + ".tops_par"

        print(TGREEN + start_underline + "Creating:" + ENDC + end_underline)
        print(
            TGREEN + "{} \n{}\n{}".format(slc_name, slc_par_name, slc_tops_par) + ENDC
        )

        # execute the pygamma command
        cmd = "par_S1_SLC {slc} {ann} {cal} {noi} {slc_par} {slc_file} {slc_tops_par} - - -".format(
            slc=slc,
            ann=ann,
            cal=cal,
            noi=noi,
            slc_par=slc_par_name,
            slc_file=slc_name,
            slc_tops_par=slc_tops_par,
        )
        # check if the file is not already extracted
        if not os.path.isfile(slc_name):
            os.system(cmd) if not args.print else print(
                TRED + "working locally. Not calling pygamma" + ENDC
            )
        else:
            print("SLCs are already extracted")


def slc_import(dir_data, test=True, num_scenes=2):
    safes = [
        os.path.join(dir_data, x) for x in os.listdir(dir_data) if x.endswith(".SAFE")
    ]
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

    print(start_underline + "Woring with DEM:\n" + end_underline, dem)
    print()
    print(TGREEN + start_underline + "Creating DEM-File" + end_underline)
    print(TGREEN + out + ENDC)
    print()
    print(TGREEN + start_underline + "Creating DEM-Parameter-File" + end_underline)
    print(TGREEN + out_par + ENDC)

    if not args.print:
        # check if the output already exists
        if not os.path.isfile(out) or not os.path.isfile(out_par):
            pg.dem_import(dem, out, out_par)
        else:
            print("DEM is already extracted")
    else:
        print(
            start_bold + start_underline + TRED + "ONLY TESTING THE DEM IMPORT" + ENDC
        )


def main():

    # get the arguments
    args = parser.parse_args()
    if args.print:
        print("working locally...")
    else:
        try:
            import py_gamma as pg

            print("working on the server...")
            # only giving the option between doing one at a time or all
            # If ONE --> choese one
            if len(args.steps) == 1:
                if 0 in args.steps:
                    unzip(dir_data, dir_data)
                elif 1 in args.steps:
                    slc_import(dir_data) if args.print else slc_import(
                        dir_data, test=False
                    )
                elif 2 in args.steps:
                    dem_import(dir_dem, dem_name) if not args.print else dem_import(
                        dir_dem, dem_name, test=False
                    )

                # if the len of the argumets provided to -s is > 1 (independent of what it is) it will make all three steps
                else:
                    unzip(dir_data, dir_data)
                    slc_import(dir_data) if args.print else slc_import(
                        dir_data, test=False
                    )
                    dem_import(dir_dem, dem_name) if not args.print else dem_import(
                        dir_dem, dem_name, test=False
                    )

        except ImportError as err:
            print("Trying to import gamma")
            print("However the py_gamma-module can not be loaded...")
            print("Make sure its on $PATH? or PYTHONPATH?")
            exit(-1)


if __name__ == "__main__":
    main()
