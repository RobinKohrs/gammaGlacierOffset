#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################
# Window Size Refinement loops
#########################################

import os
import re
import argparse
import sys
from io import StringIO
import numpy as np
import itertools
from functions import *
import subprocess

# parse some arguments
parser = argparse.ArgumentParser(description="Glacier Offset Tracking in 5 steps")
# get positional arguments
parser.add_argument("-s", "--step", metavar="", dest="steps", help="(1)... (2)...", nargs="+", default=[1],type=int)
parser.add_argument("-p", "--print", metavar="", dest="print", help="only print cmd call", action="store_const", const=True)

args = parser.parse_args()

def initiate_offset(slc1_par, slc2_par, off):

    assert os.path.isfile(slc1_par), f"{slc1_par} is not a file"
    assert os.path.isfile(slc1_par), f"{slc2_par} is not a file"

    override_input = '\n\n\n\n\n\n\n'

    r_pos = 2000 # range position orbit init
    az_pos = 11000 # azimuth position orbit init

    if os.path.isfile(off):
        os.remove(off)

    cmd1 = f"create_offset {slc1_par} {slc1_par} {off}"
    import pdb; pdb.set_trace()
    subprocess.run(cmd1, stdout=subprocess.PIPE, shell=True, input=override_input, encoding="ascii") if not args.print else print(cmd1)




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

        # tuple dir path
        path_tuple = os.path.join(tuples_dir, datepair)
        path_method = os.path.join(tuples_dir, datepair, method)

        # define file paths
        coreg_off = os.path.join(path_tuple, datepair + ".off")
        method_off = os.path.join(path_method, datepair + ".off")
        rslc1 = [os.path.join(path_tuple, x) for x in os.listdir(path_tuple) if x.endswith(".rslc") and date1 in x][0]
        rslc1_par = [os.path.join(path_tuple, x) for x in os.listdir(path_tuple) if x.endswith(".rslc.par") and date1 in x][0]
        rslc2 = [os.path.join(path_tuple, x) for x in os.listdir(path_tuple) if x.endswith(".rslc") and date2 in x][0]
        rslc2_par = [os.path.join(path_tuple, x) for x in os.listdir(path_tuple) if x.endswith(".rslc.par") and date2 in x][0]

    # loop over all the steps
    for step in sorted(args.steps):
        if int(step) == 1:
            # delete .off file if existing, initiate .off file with orbit inforamtion
            initiate_offset(rslc1_par, rslc2_par, method_off)
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

