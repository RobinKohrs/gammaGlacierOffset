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
import numpy as np
from functions import get_files, get_dates, file_dict

##################
# parse option to work locally or on server
##################

# parse some arguments
parser = argparse.ArgumentParser(description="Decide whether you are executing this locally (-l) or on the server (-s) and which steps to perform")
# get positional arguments
parser.add_argument("-m", "--machine", dest="m",
                    help="(input) decide if working locally (l) or on the server (s)", default="s", type=str)

parser.add_argument("-s", "--step", dest="steps",
                    help="(input) initiate offset file with parameter file and orbit information (1),"
                         "optimise offsets (2)", default=[1],
                    nargs="+", type=int)

# 1 = Intensity tracking
# 2 = Fringe visibility tracking
# TODO: tracking method in output file names
parser.add_argument("-a", "--algorithm", dest="trackingAlgorithm",
                    help="(Input) Intensity Tracking (1) or Fringe Visibility Tracking (2)",
                    default=1, type=int)

parser.add_argument("-i", "--iters", dest="i",
                    help="(input) is number of iterations performed as optimisation of the offset [int]",
                    default=3, type=int)

# get the arguments
global args
args = parser.parse_args()


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

deramping = 1 # yes

#########################################
# CREATING OFFSETS (actually belongs to another script
#########################################

def initiate_offsets(slc1_par, slc2_par, off):
    # manual value input needs to be overrun automatically

    override_input = '\n\n\n\n\n\n\n'

    r_pos = 2000 # range position orbit init
    az_pos = 11000 # azimuth position orbit init

    if os.path.isfile(off):
        os.remove(off)
    try:
        print("=====")
        print("Creating offset file from SLC parameter file")
        print("=====\n")
        sysinput = sys.stdin # save std input
        f = StringIO(override_input) # override input 7x
        sys.stdin = f
        print(sys.stdin)

        pg.create_offset(slc1_par, slc2_par, off, args.trackingAlgorithm)

        f.close()
        sys.stdin = sysinput # bring std input back
        print("Offset creation successful\n")

    except:
        print("Creation not failed")

    try:
        print("=====")
        print("Initiating offsets with precise Sentinel-1 orbit information")
        print("=====\n")

        # TODO: why still not reaching beyond init_offset_orbit?
        pg.init_offset_orbit(slc1_par, slc2_par, off, r_pos, az_pos)

        print(f"Full initiation successful. \nOffset file {off} is stored in {slc_dir}.")
    except:
        print("Orbit initialisation failed")


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

def final_offset_fitting(slc1, slc2, slc1_par, slc2_par, off, reg, qmf, QA, oversampling, patches, samples, threshold):

    print("=====")
    print("Final optimisation")
    print("=====\n\n\n")

    # TODO:
    # Read QA.csv
    # grep best run's parameters: patches, samples, threshold
    # rerun step 0, 2
    # run offset_pwr
    # run offset_fit
    # finish

    pg.offset_pwr(slc1, slc2, slc1_par, slc2_par, off, reg_offsets, qmf_offsets,
                  patches, patches, "-", oversampling, samples, samples,
                  threshold, "-", "-", deramping)

    print("=====")
    print("Offset fitting")
    print("=====")
    pg.offset_fit(reg_offsets, qmf_offsets, off, "-", "-")

def optimise_offsets(slc1, slc2, slc1_par, slc2_par, off, reg, qmf, QA, oversampling):

    if os.path.isfile(QA):
        os.remove(QA)

    # Metrics static ------
    patch_rn, patch_az = 128, 128
    samples_rn, samples_az = 32, 32

    # Metrics looping -----
    # Window size <- to be optimised
    patches = [2 ** x for x in range(6, 11)]

    # Number of offset estimates, correlation function window size <- to be optimised
    samples = [x ** 2 for x in range(5, 8)]

    threshold = 0.15  # from user guide
    thresholds = np.arange(0.1, 0.35, 0.05).tolist()
    # round iterative
    for i in enumerate(thresholds):
        thresholds[i[0]] = round(i[1], 2)

    # optimisation_dict = {iter : [rank, sizes, patches]}
    optimisation = {}


    # print loops to run:
    counter = 1
    for i in enumerate(patches):
        for j in enumerate(samples):
            for k in enumerate(thresholds):
                counter +=1

    print("=====")
    print("Number of Iterations to run: {}".format(counter))

    # TODO: ask Robin: loops more sanitised!?
    def looping(maxiter):
        count = 0
        for i, patch in enumerate(patches):
            for j, sample in enumerate(samples):
                for k, thresh in enumerate(thresholds):
                    print(k)

                    print("Offset Optimisation for 'window size', 'samples per window' and 'threshold'")
                    print("Number Patches: {}".format(patch))
                    print("Number Samples: {}".format(sample))
                    print("Threshold is {}".format(thresh))
                    print("=====")

                    pg.offset_pwr(slc1, slc2, slc1_par, slc2_par, off, reg, qmf,
                                  patch, patch, "-", oversampling, sample, sample,
                                  thresh, "-", "-", deramping)

                    # store reference stdout
                    old_stdout = sys.stdout
                    result = StringIO()
                    sys.stdout = result

                    # offset fitting
                    print("=====")
                    print("Offset fitting")
                    pg.offset_fit(reg, qmf, off, "-", "-")
                    print("=====")

                    # Redirect stdout back to screen
                    sys.stdout = old_stdout

                    # return value from stdout to file

                    out = result.getvalue()
                    qa_read = reading_QA(out)
                    # print("Metrics:", qa_read)

                    # update optimisation dictionary
                    optimisation[count] = [patch, sample, thresh, {"metrics" : qa_read}]
                    print(optimisation)

                    count += 1

                    if count == maxiter:
                        print(counter)
                        return optimisation

    # optimisation = {0: [64, 25, 0.1, {'metrics': {'range': '0.1583', 'azimuth': '0.1380'}}], 1: [64, 25, 0.15, {'metrics': {'range': '0.0675', 'azimuth': '0.0995'}}], 2: [64, 25, 0.2, {'metrics': {'range': '0.0679', 'azimuth': '0.1005'}}], 3: [64, 25, 0.25, {'metrics': {'range': '0.0583', 'azimuth': '0.1042'}}], 4: [64, 25, 0.3, {'metrics': {'range': '0.0622', 'azimuth': '0.1122'}}], 5: [64, 36, 0.1, {'metrics': {'range': '0.0740', 'azimuth': '0.1039'}}], 6: [64, 36, 0.15, {'metrics': {'range': '0.0729', 'azimuth': '0.1037'}}], 7: [64, 36, 0.2, {'metrics': {'range': '0.0660', 'azimuth': '0.0929'}}], 8: [64, 36, 0.25, {'metrics': {'range': '0.0579', 'azimuth': '0.0702'}}], 9: [64, 36, 0.3, {'metrics': {'range': '0.0560', 'azimuth': '0.0721'}}], 10: [64, 49, 0.1, {'metrics': {'range': '0.0742', 'azimuth': '0.1511'}}], 11: [64, 49, 0.15, {'metrics': {'range': '0.0739', 'azimuth': '0.1422'}}], 12: [64, 49, 0.2, {'metrics': {'range': '0.0652', 'azimuth': '0.1422'}}], 13: [64, 49, 0.25, {'metrics': {'range': '0.0584', 'azimuth': '0.1443'}}], 14: [64, 49, 0.3, {'metrics': {'range': '0.0566', 'azimuth': '0.1432'}}], 15: [128, 25, 0.1, {'metrics': {'range': '0.0499', 'azimuth': '0.0710'}}], 16: [128, 25, 0.15, {'metrics': {'range': '0.0465', 'azimuth': '0.0714'}}], 17: [128, 25, 0.2, {'metrics': {'range': '0.0452', 'azimuth': '0.0729'}}], 18: [128, 25, 0.25, {'metrics': {'range': '0.0589', 'azimuth': '0.0916'}}], 19: [128, 25, 0.3, {'metrics': {'range': '0.0605', 'azimuth': '0.0925'}}], 20: [128, 36, 0.1, {'metrics': {'range': '0.0442', 'azimuth': '0.0711'}}], 21: [128, 36, 0.15, {'metrics': {'range': '0.0435', 'azimuth': '0.0707'}}], 22: [128, 36, 0.2, {'metrics': {'range': '0.0438', 'azimuth': '0.0711'}}], 23: [128, 36, 0.25, {'metrics': {'range': '0.0410', 'azimuth': '0.0669'}}], 24: [128, 36, 0.3, {'metrics': {'range': '0.0283', 'azimuth': '0.0677'}}], 25: [128, 49, 0.1, {'metrics': {'range': '0.0600', 'azimuth': '0.1045'}}], 26: [128, 49, 0.15, {'metrics': {'range': '0.0573', 'azimuth': '0.1059'}}], 27: [128, 49, 0.2, {'metrics': {'range': '0.0446', 'azimuth': '0.1031'}}], 28: [128, 49, 0.25, {'metrics': {'range': '0.0390', 'azimuth': '0.1031'}}], 29: [128, 49, 0.3, {'metrics': {'range': '0.0392', 'azimuth': '0.1097'}}], 30: [256, 25, 0.1, {'metrics': {'range': '0.0292', 'azimuth': '0.0715'}}], 31: [256, 25, 0.15, {'metrics': {'range': '0.0295', 'azimuth': '0.0677'}}], 32: [256, 25, 0.2, {'metrics': {'range': '0.0300', 'azimuth': '0.0709'}}], 33: [256, 25, 0.25, {'metrics': {'range': '0.0301', 'azimuth': '0.0698'}}], 34: [256, 25, 0.3, {'metrics': {'range': '0.0320', 'azimuth': '0.0595'}}], 35: [256, 36, 0.1, {'metrics': {'range': '0.0310', 'azimuth': '0.0571'}}], 36: [256, 36, 0.15, {'metrics': {'range': '0.0283', 'azimuth': '0.0591'}}], 37: [256, 36, 0.2, {'metrics': {'range': '0.0279', 'azimuth': '0.0541'}}], 38: [256, 36, 0.25, {'metrics': {'range': '0.0227', 'azimuth': '0.0517'}}], 39: [256, 36, 0.3, {'metrics': {'range': '0.0260', 'azimuth': '0.0457'}}], 40: [256, 49, 0.1, {'metrics': {'range': '0.0289', 'azimuth': '0.0654'}}], 41: [256, 49, 0.15, {'metrics': {'range': '0.0225', 'azimuth': '0.0599'}}], 42: [256, 49, 0.2, {'metrics': {'range': '0.0212', 'azimuth': '0.0593'}}], 43: [256, 49, 0.25, {'metrics': {'range': '0.0197', 'azimuth': '0.0564'}}], 44: [256, 49, 0.3, {'metrics': {'range': '0.0228', 'azimuth': '0.0597'}}], 45: [512, 25, 0.1, {'metrics': {'range': '0.0160', 'azimuth': '0.0325'}}], 46: [512, 25, 0.15, {'metrics': {'range': '0.0162', 'azimuth': '0.0324'}}], 47: [512, 25, 0.2, {'metrics': {'range': '0.0148', 'azimuth': '0.0327'}}], 48: [512, 25, 0.25, {'metrics': {'range': '0.0146', 'azimuth': '0.0315'}}], 49: [512, 25, 0.3, {'metrics': {'range': '0.0154', 'azimuth': '0.0337'}}], 50: [512, 36, 0.1, {'metrics': {'range': '0.0177', 'azimuth': '0.0301'}}], 51: [512, 36, 0.15, {'metrics': {'range': '0.0173', 'azimuth': '0.0297'}}], 52: [512, 36, 0.2, {'metrics': {'range': '0.0165', 'azimuth': '0.0274'}}], 53: [512, 36, 0.25, {'metrics': {'range': '0.0154', 'azimuth': '0.0270'}}], 54: [512, 36, 0.3, {'metrics': {'range': '0.0156', 'azimuth': '0.0289'}}], 55: [512, 49, 0.1, {'metrics': {'range': '0.0176', 'azimuth': '0.0314'}}], 56: [512, 49, 0.15, {'metrics': {'range': '0.0143', 'azimuth': '0.0267'}}], 57: [512, 49, 0.2, {'metrics': {'range': '0.0135', 'azimuth': '0.0249'}}], 58: [512, 49, 0.25, {'metrics': {'range': '0.0125', 'azimuth': '0.0251'}}], 59: [512, 49, 0.3, {'metrics': {'range': '0.0097', 'azimuth': '0.0204'}}], 60: [1024, 25, 0.1, {'metrics': {'range': '0.0130', 'azimuth': '0.0152'}}], 61: [1024, 25, 0.15, {'metrics': {'range': '0.0130', 'azimuth': '0.0154'}}], 62: [1024, 25, 0.2, {'metrics': {'range': '0.0133', 'azimuth': '0.0165'}}], 63: [1024, 25, 0.25, {'metrics': {'range': '0.0131', 'azimuth': '0.0163'}}], 64: [1024, 25, 0.3, {'metrics': {'range': '0.0175', 'azimuth': '0.0226'}}], 65: [1024, 36, 0.1, {'metrics': {'range': '0.0132', 'azimuth': '0.0190'}}], 66: [1024, 36, 0.15, {'metrics': {'range': '0.0129', 'azimuth': '0.0189'}}]}

    optimisation = looping(maxiter=args.i)

    # trial zone
    df = pd.DataFrame(optimisation.keys())
    optimisation.values()

    # TODO: Sanatise!
    npatches = []
    nsamples = []
    nthresh = [ ]
    mean = []
    for iters in optimisation.values():
        metr = iters[3].values()
        npatches.append(iters[0])
        nsamples.append(iters[1])
        nthresh.append(iters[2])
        for i in metr:
            lst_metr = list(i.values())

            # calculating mean of metrics
            i.update({"mean": round((float(lst_metr[0]) + float(lst_metr[1])) / 2, 4)})
            mean.append(list(i.values())[2])

    df.insert(1, "mean_sd", mean)
    df.insert(2, "patches", npatches)
    df.insert(3, "samples", nsamples)
    df.insert(4, "threshold", nthresh)
    print(df)

    # sorting
    df = df.sort_values(by=["mean_sd"], ascending=True)
    # write metrics out as csv
    df.to_csv(path_or_buf=QA)

    # grep bestrun arguments
    bestrun = df.iloc[0]
    print("Best run: \n\n", bestrun)

    # run final optimisation (not necessarily)
    # final_offset_fitting(slc1, slc1_par, slc2, slc2_par, off, patches, samples, threshold)

def main():

    # INPUT
    slc_dir =  "../data/test_offset/perf"

    oversampling = 2  # what does that actually mean?

    # optional overview printing
    files = get_files(slc_dir = slc_dir, image = "m", file_ending=".slc.par")
    # print(files)
    dates = get_dates(slc_dir = slc_dir)
    # print(dates)

    # create file dict:
    dict = file_dict(slc_dir = slc_dir)
    print(dict)

    # dict = {'20200911_20200923': {'20200911': ['20200911_vv_iw2.slc', '20200911_vv_iw2.slc.par'], '20200923': ['20200923_vv_iw2.slc.par', '20200923_vv_iw2.slc']}}

    for datepair in dict:
        QA = os.path.join(slc_dir, datepair + ".QA")
        off = os.path.join(slc_dir, datepair + ".off")
        reg = os.path.join(slc_dir, datepair + ".reg")
        qmf = os.path.join(slc_dir, datepair + ".qmf")

        for i, slc_files in enumerate(dict[datepair].values()):
            # print(a)
            if i == 0:
                # main_slc = os.path.join(slc_dir, slc_files.endswith(".slc"))
                slc1 = [os.path.join(slc_dir, slc) for slc in slc_files if slc.endswith((".slc"))][0]
                slc1_par = [os.path.join(slc_dir, slc) for slc in slc_files if slc.endswith((".slc.par"))][0]
                print(slc1)
            elif i == 1:
                slc2 = [os.path.join(slc_dir, slc) for slc in slc_files if slc.endswith((".slc"))][0]
                slc2_par = [os.path.join(slc_dir, slc) for slc in slc_files if slc.endswith((".slc.par"))][0]
                print(slc2)

        for step in sorted(args.steps):
            if int(step) == 1:
                initiate_offsets(slc1_par, slc2_par, off)
            elif int(step) == 2:
                optimise_offsets(slc1, slc2, slc1_par, slc2_par, off, reg, qmf, QA, oversampling)
            elif int(step) == 3:
                final_offset_fitting()
            else:
                pass

if __name__ == '__main__':
    main()
