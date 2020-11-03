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

    override_input='\n\n\n\n\n\n\n'

    r_pos = 2000 # range position orbit init
    az_pos = 11000 # azimuth position orbit init

    if os.path.isfile(off):
        os.remove(off)

    # CREATE OFFSET
    cmd1 = f"create_offset {slc1_par} {slc1_par} {off}"
    subprocess.run(cmd1, stdout=subprocess.PIPE, shell=True, input=override_input, encoding="ascii") if not args.print else print(cmd1)

    # INIT OFFSET ORBIT
    # cmd2 = f"init_offset_orbit {slc1_par} {slc2_par} {off} {r_pos} {az_pos}"
    # subprocess.run(cmd2, stdout=subprocess.PIPE, shell=True) if not args.print else print(cmd2)

    return None

def enhance_offsets(slc1, slc1_par, slc2, slc2_par, off, out_cpx_offset_estimates,
                    out_snr, out_offset_txt):
    """
    This will run offset_SLC. Some of the output paramteres are defined in the function call. The other will be more
    flexible within the function


    input parameters for offset_slc
    SLC-1     (input) single-look complex image 1 (reference)
    SLC-2     (input) single-look complex image 2
    SLC1_par  (input) SLC-1 ISP image parameter file
    SLC2_par  (input) SLC-2 ISP image parameter file
    OFF_par   (input) ISP offset/interferogram parameter file
    offs      (output) offset estimates (fcomplex)
    snr       (output) offset estimation SNR (float)
    rwin      search window size (range pixels, (enter - for default from offset parameter file))
    azwin     search window size (azimuth lines, (enter - for default from offset parameter file))
    offsets   (output) range and azimuth offsets and SNR data in text format, enter - for no output
    n_ovr     SLC oversampling factor (integer 2**N (1,2,4) default = 2)
    nr        number of offset estimates in range direction (enter - for default from offset parameter file)
    naz       number of offset estimates in azimuth direction (enter - for default from offset parameter file)
    thres     offset estimation quality threshold (enter - for default from offset parameter file)
    ISZ       search chip interferogram size (in non-oversampled pixels, default=16)
    pflag     print flag (0:print offset summary  default=1:print all offset data)

    """

    # range window
    rwin = 10 #TODO: No idea, bust bust be smaller than the patchsize (which also should be small for fringe visibility??!!)
    azwin = 2

    # number of oversampling
    n_over = "-"
    nr = "-"
    naz = "-"
    thres = "-"
    ISZ = "-" # defaults to 16 and should be small, but can we maybe make bigger?
    pflag = 1


    cmd1 = f"offset_SLC {slc1} {slc2} {slc1_par} {slc2_par} {off} {out_cpx_offset_estimates} " \
           f"{out_snr} {rwin} {azwin} {out_offset_txt} {n_over} {nr} {naz} {thres} {ISZ} {pflag}"

    out = subprocess.run(cmd1, stdout=subprocess.PIPE, shell=True) if not args.print else print(cmd1)

    # write output to file
    f = os.path.join(os.path.dirname(slc1), "fringe", "output_offset_slc.txt")
    with open(f, "w") as src:
        src.write(out.stdout.decode("UTF-8"))



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

        # paths for offset_SLC
        out_cpx_offset_estimates = os.path.join(path_method,"cpx_offset.off")
        out_snr = os.path.join(path_method, datepair + ".snr")
        out_offsets_text = os.path.join(path_method, "cpx_offset.txt")

        # loop over all the steps
        for step in sorted(args.steps):
            if int(step) == 1:
                # delete .off file if existing, initiate .off file with orbit inforamtion
                # here the method off will be crated
                initiate_offset(rslc1_par, rslc2_par, method_off)
                # here it will be updated
                enhance_offsets(rslc1, rslc1_par, rslc2, rslc2_par, method_off, out_cpx_offset_estimates,
                                out_snr, out_offsets_text)
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

