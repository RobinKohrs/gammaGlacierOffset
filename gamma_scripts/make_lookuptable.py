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
args =parser.parse_args()





def create_lookup(slc_dir, image="main"):
    # get the necessary files
    # important is to put mosaic in the file ending
    main_mli_slcs_pars = get_files(slc_dir, image=image, file_ending=["mosaic.mli.par"])
    dem_par = [os.path.join(dem_dir, x) for x in os.listdir(dem_dir) if x.endswith(".par") and "DEM" in str.upper(x)][0]
    dem = [os.path.join(dem_dir, x) for x in os.listdir(dem_dir) if x.endswith("DEM")][0]
    for ele in main_mli_slcs_pars:
        identidier = ele[0][0:14]
        mosaic_mli_par = os.path.join(slc_dir, ele[0])
        lookup_table = os.path.join(slc_dir, identidier) + ".lt"
        inc = os.path.join(slc_dir, identidier + ".inc")
        ls_map = os.path.join(slc_dir, "ls_map")
        cmd = f"gc_map {mosaic_mli_par} - {dem_par} {dem} ../data/DEM/EQA_dem.par ../data/DEM/EQA.dem {lookup_table} 0.5 0.5 {inc} - - {ls_map} 8 2"
        os.system(cmd) if not args.print else print(cmd)


def main():
    create_lookup(slc_dir, image="main")


if __name__ == "__main__":
    slc_dir = "../data/SLC"
    dem_dir = "../data/DEM"
    main()
