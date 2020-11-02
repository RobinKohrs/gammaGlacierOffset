#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################
# Window Size Refinement loops
#########################################

import os
import re
import argparse
import sys
import numpy as np
import itertools
from functions import *

# parse some arguments
parser = argparse.ArgumentParser(description="Glacier Offset Tracking in 5 steps")
# get positional arguments
parser.add_argument("-s", "--step", metavar="", dest="steps", help="(1)... (2)...", nargs="+", default=[1],type=int)
parser.add_argument("-p", "--print", metavar="", dest="print", help="only print cmd call", action="store_const", const=True)

args = parser.parse_args()


def main():

    # define directories
    slc_dir = "../data/SLC"
    tuples_dir = "../data/tuples"
    method = "fringe"
    oversampling = 1  # what does that actually mean?

    # specify ending of file to be used as basename giver
    dict = file_dict(slc_dir = slc_dir, ending=".mosaic_slc")

    # loop over the date_combinations
    for datepair in dict.keys():
        date1 = datepair[0:8]
        date2 = datepair[9:17]

        # tuple path
        path_tuple = os.path.join(tuples_dir, datepair)
        path_datepair = os.path.join(tuples_dir, datepair, method)
        print(path_tuple)
        print(path_datepair)
        print(path_tuple)
        print(path_datepair)


    # loop over all the steps
    for step in sorted(args.steps):
        if int(step) == 1:
            # delete .off file if existing, initiate .off file with orbit inforamtion
            initiate_offsets(rslc1_par, rslc2_par, off)
        elif int(step) == 2:
            pass
        elif int(step) == 3:
            pass
        elif int(step) == 4:
            pass
        elif int(step) == 5:
            pass
        else:
            pass

if __name__ == "__main__":
    main()

