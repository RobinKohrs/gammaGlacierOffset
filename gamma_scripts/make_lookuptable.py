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
    main_slcs_pars = get_files(slc_dir, image=image, file_ending=["mosaic.mli.par"])
    for ele in main_slcs_pars:
        # should return a list of lists with only one entry
        for mas in ele:
            mosaic_mli_par = os.path.join(slc_dir, mas)
            dem_par = [os.path.join(dem_dir,x) for x in os.listdir(dem_dir) if x.endswith(".par") and "DEM" in str.upper(x)]
            print(dem_par)








def main():
    create_lookup(slc_dir, image="main")


if __name__ == "__main__":
    slc_dir = "../data/SLC"
    dem_dir = "../data/DEM"
    main()
