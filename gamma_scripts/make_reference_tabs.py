#!/usr/bin/env python

######################
#
# Module for for geocoding the dem to rande doppler coordinates
#
######################

import os
from functions import *
import argparse

# parse some arguments
parser = argparse.ArgumentParser(description="")
parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)
args =parser.parse_args()

def geocode():

    main_lts = rec_reg(slc_dir, ".*\.lt$")
    for i in range(len(main_lts)):
        lt = main_lts[i]
        eqa_dem_par = rec_reg(dem_dir, ".*dem.par.*")[0]
        width = int(awkpy(eqa_dem_par, "width", 2))
        print(width)

def main():
    geocode()


if __name__ == "__main__":
    slc_dir = "../data/SLC"
    dem_dir = "../data/DEM"
    main()