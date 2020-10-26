#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################
#
# multilook the master images of the image pairs
#
################################################

import os
from functions import *
import argparse

# parse some arguments
parser = argparse.ArgumentParser(description="")
# get positional arguments
parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)
parser.add_argument("-i", "--image", dest="image", help="multilook main (m, default) or secondary (s)", type=str, default="m")
parser.add_argument("-r", "--range", dest="range",
                    help="(input) looks in range (default = 10)", default=10, type=int)
parser.add_argument("-a", "--azimuth", dest="azimuth",
                    help="(input) looks in azimuth (default = 2)", default=2, type=int)
args = parser.parse_args()

slc_dir = "../data/SLC"

def multilook(slc_dir, image):
    # multilook is necessary on the (non) mosaiced!!! main for each pair
    master_slcs_pars = get_files(slc_dir, image=image, file_ending=[".mosaic_slc", "mosaic_slc.par"])
    for image_pair in master_slcs_pars:
        slc = [os.path.join(slc_dir, x) for x in image_pair if x.endswith(".mosaic_slc")][0]
        slc_par = [os.path.join(slc_dir, x) for x in image_pair if x.endswith(".par")][0]
        mli_name = slc[0:-4] + ".mli"
        mli_par_name = slc[0:-4] + ".mli.par"
        cmd = "multi_look {slc} {slc_par} {mli} {mli_par} {rl} {al}".format(slc=slc,
                                                                            slc_par = slc_par,
                                                                            mli = mli_name,
                                                                            mli_par=mli_par_name,
                                                                            rl = args.range,
                                                                            al = args.azimuth)

        print(cmd) if args.print else os.system(cmd)

def main():
    if args.image == "main" or args.image == "m":
        multilook(slc_dir, image="m")
    else:
        multilook(slc_dir, image="s")

if __name__ == "__main__":
    main()
