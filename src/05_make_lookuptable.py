#!/usr/bin/env python

######################
#
# Module for creating a lookuptable for each interferometric pair
#
######################
#

import os
from functions import *
import argparse

# parse some arguments
parser = argparse.ArgumentParser(description="")
parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)
args = parser.parse_args()


def create_lookup(slc_dir, r_oversampling, az_oversampling, image="main"):
    # get the necessary files

    # important is to put mosaic in the file ending
    main_mli_slcs_pars = get_files(slc_dir, image=image, file_ending=["mosaic.mli.par"])

    # the dem and the dem parameter file must not be in the loop
    dem_par = [os.path.join(dem_dir, x) for x in os.listdir(dem_dir) if x.endswith(".par") and "DEM" in str.upper(x) and "EQA" not in x][0]
    dem = [os.path.join(dem_dir, x) for x in os.listdir(dem_dir) if x.endswith("DEM") and "EQA" not in x][0]

    # every main_mli is the mosaiced, multilooked slc for the master
    for main_mli in main_mli_slcs_pars:
        # identifier is as always (not even close to always yet) date_pol_swath
        identifier = main_mli[0][0:15]

        # EQA DEM
        eqa = os.path.join(dem_dir, identifier + ".EQA_dem")
        eqa_par = os.path.join(dem_dir, identifier + ".EQA_dem.par")

        # make the full path to the mosaiced, multilooked slc
        mosaic_mli_par = os.path.join(slc_dir, main_mli[0])
        # create the path for the lookup table
        lookup_table = os.path.join(dem_dir, identifier) + ".lt"
        # local incidence angle and ls_map file
        inc = os.path.join(dem_dir, identifier + ".inc")
        ls_map = os.path.join(dem_dir, "ls_map")

        # build the cmd
        cmd = f"gc_map {mosaic_mli_par} - {dem_par} {dem} {eqa_par} {eqa} {lookup_table} {r_oversampling} {az_oversampling} {inc} - - {ls_map} 8 2"
        os.system(cmd) if not args.print else print(cmd)


def main():
    r_oversampling = "-"
    az_oversampling = "-"
    create_lookup(slc_dir, r_oversampling, az_oversampling, image="main")


if __name__ == "__main__":
    slc_dir = "../data/SLC"
    dem_dir = "../data/DEM"
    main()
