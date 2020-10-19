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
import pandas as pd

##################
# parse option to work locally or on server
##################

# parse some arguments
parser = argparse.ArgumentParser(description="Decide whether you are executing this locally (-l) or on the server (-s) and which steps to perform")
# get positional arguments
parser.add_argument("-m", "--machine", dest="m",
                    help="(input) decide if working locally (0) or on the server (1)", default="l", type=str)

parser.add_argument("-s", "--step", dest="steps",
                    help="(input) which step to perform unzip (0), slc-import (1), dem_import (2)", default=0,
                    nargs="+", type=int)


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

#########################################
# USER INPUT
#########################################

date1 = "20160112"
date2 = "20160124"
dates = date1 + "_" + date2

dir = "../data/test"

slc1 = os.path.join(dir, "20160112.db.slc")
slc1_par = os.path.join(dir, "20160112.db.slc.par")
slc2 = os.path.join(dir, "20160124.db.slc")
slc2_par = os.path.join(dir, "20160124.db.slc.par")

off = os.path.join(dir, dates + ".off")

# 1 = Intensity tracking
# 2 = Fringe visibility tracking
tracking_algorithm = 1
# tracking_algorithm = 2


#########################################
# CREATIN OFFSETS (actually belongs to another script
#########################################

def delete_offsets():
    os.remove(off)


def create_offsets(slc1, slc2):
    print("Offset file: {}\n".format(off))

    if os.path.isfile(off):
        os.remove(off)
    try:
        print("=====")
        print("Initiating offset file from SLC parameter file")
        print("=====")
        pg.create_offset(slc1, slc2, off, tracking_algorithm)

    except:
        print("not successful")


def init_offset_orbit(slc1_par, slc2_par, off):
    print("Offset file: {}\n".format(off))

    try:
        print("=====")
        print("Initiating offsets with precise Sentinel-1 orbit information")
        print("=====")
        pg.init_offset_orbit(slc1_par, slc2_par, off)

    except:
        print("Not successful")

def reading_QA(QA):

    # read IO output QA_temp
    lines = QA.split(sep="\n")

    # strip white space and \n
    lst = [x.strip() for x in lines]

    # grep measurement statement (first match)
    for line in lst:
        if re.match("^final\smodel", line) is not None:
            statement = line
    # print(statement)

    # grep range & azimuth model fit standard deviation
    try:
        sd_metric = re.findall("\d.\d*", statement)
    except:
        print("QA_temp console output document not readable")

    dict = {"range" : sd_metric[0],
            "azimuth" : sd_metric[1]}
    return (dict)


def optimise_offsets(slc1, slc2, slc1_par, slc2_par, off):
    reg_offsets = os.path.join(dir, dates + ".reg_offsets")
    qmf_offsets = os.path.join(dir, dates + ".qmf_offsets")
    QA = os.path.join(dir, dates + ".QA")

    # Metrics static ------
    # Window size <- to be optimised
    patch_rn = 128
    patch_az = 128

    # Number of offset estimates, correlation function window size <- to be optimised
    samples_rn = 32
    samples_az = 32

    # Metrics looping -----
    patches = [2 ** x for x in range(1, 10)]
    samples = [x ** 2 for x in range(5, 10)]

    threshold = 0.001  # <- to be optimised

    # Sentinel-1 TOPS acquisitions need to be deramped. (Is this done already in S1_mosaic_TOPS?)
    deramping = 1
    oversampling = 2  # what does that actually mean?

    # optimisation_dict = {iter : [rank, sizes, patches]}
    optimisation = {}

    counter = 1
    for i in enumerate(patches):
        for j in enumerate(samples):

            iter_i = i[0]
            iter_j = j[0]

            print("=====")
            print("Initiating offsets with precise Sentinel-1 orbit information")
            print("Number Patches: {}".format(i[1]))
            print("Number Samples: {}".format(j[1]))
            print("Threshold is {}".format(threshold))
            print("=====")

            pg.offset_pwr(slc1, slc2, slc1_par, slc2_par, off, reg_offsets, qmf_offsets,
                          patches[iter_i], patches[iter_i], "-", oversampling, samples[iter_j], samples[iter_j],
                          threshold, "-", "-", deramping)

            # store reference stdout
            old_stdout = sys.stdout
            # Init
            result = StringIO()
            sys.stdout = result

            # offset fitting
            print("=====")
            print("Offset fitting")
            pg.offset_fit(reg_offsets, qmf_offsets, off, "-", "-")
            print("=====")

            # Redirect stdout back to screen
            sys.stdout = old_stdout

            # return value from stdout to file

            out = result.getvalue()
            qa_read = reading_QA(out)
            print("Metrics:", qa_read)

            # update optimisation dictionary
            optimisation[counter] = [patches[iter_i], samples[iter_j], {"metrics" : qa_read}]
            print(optimisation)

            counter += 1

    # trial zone
    df = pd.DataFrame(optimisation.keys())
    optimisation.values()

    npatches = []
    nsamples = []
    mean = []
    for iters in optimisation.values():
        metr = iters[2].values()
        npatches.append(iters[0])
        nsamples.append(iters[1])
        for i in metr:
            lst_metr = list(i.values())

            # calculating mean of metrics
            i.update({"mean": round((float(lst_metr[0]) + float(lst_metr[1])) / 2, 4)})
            mean.append(list(i.values())[2])

    df.insert(1, "mean_sd", mean)
    df.insert(2, "patches", npatches)
    df.insert(3, "samples", nsamples)
    print(df)

    # write metrics out as csv
    df.to_csv(path_or_buf=QA)

    # TODO: rank results

def main():

    print(args.steps)
    for step in sorted(args.steps):
        if int(step) == 0:
            create_offsets(slc1_par, slc2_par)
        elif int(step) == 1:
            init_offset_orbit(slc1_par, slc2_par, off)
        elif int(step) == 2:
            optimise_offsets(slc1, slc2, slc1_par, slc2_par, off)

if __name__ == '__main__':
    main()
