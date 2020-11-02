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
import itertools

from functions import *

##################
# parse option to work locally or on server
##################

# parse some arguments
parser = argparse.ArgumentParser(description="Glacier Offset Tracking in 5 steps")
# get positional arguments
parser.add_argument("-s", "--step", dest="steps",
                    help="(input) initiate offset file with parameter file and orbit information (1),"
                         "optimise offsets (2)", default=[1],
                    nargs="+", type=int)

# 1 = Intensity tracking
# 2 = Fringe visibility tracking
# parser.add_argument("-a", "--algorithm", dest="trackingAlgorithm",
#                     help="(Input) Intensity Tracking (1) or Fringe Visibility Tracking (2)",
#                     default=1, type=int)

parser.add_argument("-i", "--iters", dest="i",
                    help="(input) is number of iterations performed as optimisation of the offset [int]",
                    default=3, type=int)

parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)

# get the arguments
global args
args = parser.parse_args()

# algo = args.trackingAlgorithm
#
# if algo == 1:
#     method = "intensity"
# elif algo == 2:
#     method = "fringe"

if args.print == True:
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
method = "intensity"

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

    print("=====")
    print("Creating offset file from SLC parameter file")
    print(TGREEN + method + ENDC)
    print("=====\n")

    sysinput = sys.stdin # save std input
    f = StringIO(override_input) # override input 7x
    sys.stdin = f
    print(sys.stdin)

    cmd1 = f"create_offset {slc1_par} {slc1_par} {off} 1}"

    pg.create_offset(slc1_par, slc2_par, off, "1") if not args.print else print(cmd1)

    f.close()
    sys.stdin = sysinput # bring std input back

    print("=====")
    print("Initiating offsets with precise Sentinel-1 orbit information")
    print(TGREEN + "Orbit Reference Position" + ENDC)
    print("Range:", r_pos)
    print("Azimuth:", az_pos)
    print("=====\n")

    cmd2 = f"init_offset_orbit {slc1_par} {slc2_par} {off} {r_pos} {az_pos}"

    pg.init_offset_orbit(slc1_par, slc2_par, off, r_pos, az_pos) if not args.print else print(cmd2)

    print(f"Full initiation successful. \nOffset file: {off}.")

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
        print(TRED + "QA_temp console output document not readable" + ENDC)

    dict = {"range" : sd_metric[0],
            "azimuth" : sd_metric[1]}
    return (dict)

def optimise_offsets(slc1, slc2, slc1_par, slc2_par, off, reg, qmf, QA, oversampling, snr):

    # delete QA file
    if os.path.isfile(QA):
        os.remove(QA)

    # Metrics static ------
    patch_rn, patch_az = 128, 128
    samples_rn, samples_az = 32, 32

    # Metrics looping -----
    # Window size <- to be optimised
    patches = [2 ** x for x in range(7, 11)]

    # Number of offset estimates, correlation function window size <- to be optimised
    samples = [x ** 2 for x in range(8, 12)]

    threshold = 0.15  # from user guide
    # thresholds = np.arange(0.1, 0.3, 0.05).tolist()

    # round iteratively
    # for i in enumerate(thresholds):
    #     thresholds[i[0]] = round(i[1], 2)

    # optimisation_dict = {iter : [rank, sizes, patches]}
    optimisation = {}

    # print number of prospected optimisation iterations
    runs = len(list(itertools.product(*[patches, samples])))
    print("Number of runs:", runs)

    def dataframe_creation(optimisation):
        """
        wrangling optimisation dictionary to dataframe
        """

        # t rial zone
        df = pd.DataFrame(optimisation.keys())
        optimisation.values()

        # TODO: Sanatise!
        npatches = []
        nsamples = []
        nthresh = []
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

        # grep bestrun arguments
        bestrun = df.iloc[0]
        print("Best run: \n\n", bestrun)

        return df

    def looping(maxiter):

        count = 0
        for i, patch in enumerate(patches):
            for j, sample in enumerate(samples):

                print("Offset Optimisation for 'window size', 'samples per window' and 'threshold'")
                print("Number Patches: {}".format(patch))
                print("Number Samples: {}".format(sample))
                print("Threshold is {}".format(threshold))
                print("=====")

                cmd = f"offset_pwr {slc1} {slc2} {slc1_par} {slc2_par} {off} {reg} {qmf} {patch} {patch} " \
                      f"- {oversampling} {sample} {sample} {threshold} - - {deramping}"

                if not args.print:
                    pg.offset_pwr(slc1, slc2, slc1_par, slc2_par, off, reg, qmf,
                          patch, patch, "-", oversampling, sample, sample,
                          threshold, "-", "-", deramping)
                else:
                    print(cmd)
                    return None

                # elif algo == 2:
                #     cmd = f"offset_SLC {slc1} {slc2} {slc1_par} {slc2_par} {off} {reg} {snr} {patch} {patch} " \
                #           f"- {oversampling} {sample} {sample} {threshold}"
                #
                #     if not args.print:
                #         pg.offset_SLC(slc1, slc2, slc1_par, slc2_par, off, reg, snr,
                #                   patch, patch, "-", oversampling,
                #                   sample, sample, threshold, "-")
                #     else:
                #         print(cmd)
                #         return None


                # store reference stdout
                old_stdout = sys.stdout
                result = StringIO()
                sys.stdout = result

                # offset fitting
                print("=====")
                print("Offset fitting")
                print("=====")

                # GAMMA
                pg.offset_fit(reg, qmf, off, "-", "-")

                # Redirect stdout back to screen
                sys.stdout = old_stdout

                # return value from stdout to file

                out = result.getvalue()
                qa_read = reading_QA(out)
                # print("Metrics:", qa_read)

                # update optimisation dictionary
                optimisation[count] = [patch, sample, threshold, {"metrics" : qa_read}]
                print(optimisation)

                # optimisation = {0: [64, 25, 0.1, {'metrics': {'range': '0.1583', 'azimuth': '0.1380'}}], 1: [64, 25, 0.15, {'metrics': {'range': '0.0675', 'azimuth': '0.0995'}}], 2: [64, 25, 0.2, {'metrics': {'range': '0.0679', 'azimuth': '0.1005'}}], 3: [64, 25, 0.25, {'metrics': {'range': '0.0583', 'azimuth': '0.1042'}}], 4: [64, 25, 0.3, {'metrics': {'range': '0.0622', 'azimuth': '0.1122'}}], 5: [64, 36, 0.1, {'metrics': {'range': '0.0740', 'azimuth': '0.1039'}}], 6: [64, 36, 0.15, {'metrics': {'range': '0.0729', 'azimuth': '0.1037'}}], 7: [64, 36, 0.2, {'metrics': {'range': '0.0660', 'azimuth': '0.0929'}}], 8: [64, 36, 0.25, {'metrics': {'range': '0.0579', 'azimuth': '0.0702'}}], 9: [64, 36, 0.3, {'metrics': {'range': '0.0560', 'azimuth': '0.0721'}}], 10: [64, 49, 0.1, {'metrics': {'range': '0.0742', 'azimuth': '0.1511'}}], 11: [64, 49, 0.15, {'metrics': {'range': '0.0739', 'azimuth': '0.1422'}}], 12: [64, 49, 0.2, {'metrics': {'range': '0.0652', 'azimuth': '0.1422'}}], 13: [64, 49, 0.25, {'metrics': {'range': '0.0584', 'azimuth': '0.1443'}}], 14: [64, 49, 0.3, {'metrics': {'range': '0.0566', 'azimuth': '0.1432'}}], 15: [128, 25, 0.1, {'metrics': {'range': '0.0499', 'azimuth': '0.0710'}}], 16: [128, 25, 0.15, {'metrics': {'range': '0.0465', 'azimuth': '0.0714'}}], 17: [128, 25, 0.2, {'metrics': {'range': '0.0452', 'azimuth': '0.0729'}}], 18: [128, 25, 0.25, {'metrics': {'range': '0.0589', 'azimuth': '0.0916'}}], 19: [128, 25, 0.3, {'metrics': {'range': '0.0605', 'azimuth': '0.0925'}}], 20: [128, 36, 0.1, {'metrics': {'range': '0.0442', 'azimuth': '0.0711'}}], 21: [128, 36, 0.15, {'metrics': {'range': '0.0435', 'azimuth': '0.0707'}}], 22: [128, 36, 0.2, {'metrics': {'range': '0.0438', 'azimuth': '0.0711'}}], 23: [128, 36, 0.25, {'metrics': {'range': '0.0410', 'azimuth': '0.0669'}}], 24: [128, 36, 0.3, {'metrics': {'range': '0.0283', 'azimuth': '0.0677'}}], 25: [128, 49, 0.1, {'metrics': {'range': '0.0600', 'azimuth': '0.1045'}}], 26: [128, 49, 0.15, {'metrics': {'range': '0.0573', 'azimuth': '0.1059'}}], 27: [128, 49, 0.2, {'metrics': {'range': '0.0446', 'azimuth': '0.1031'}}], 28: [128, 49, 0.25, {'metrics': {'range': '0.0390', 'azimuth': '0.1031'}}], 29: [128, 49, 0.3, {'metrics': {'range': '0.0392', 'azimuth': '0.1097'}}], 30: [256, 25, 0.1, {'metrics': {'range': '0.0292', 'azimuth': '0.0715'}}], 31: [256, 25, 0.15, {'metrics': {'range': '0.0295', 'azimuth': '0.0677'}}], 32: [256, 25, 0.2, {'metrics': {'range': '0.0300', 'azimuth': '0.0709'}}], 33: [256, 25, 0.25, {'metrics': {'range': '0.0301', 'azimuth': '0.0698'}}], 34: [256, 25, 0.3, {'metrics': {'range': '0.0320', 'azimuth': '0.0595'}}], 35: [256, 36, 0.1, {'metrics': {'range': '0.0310', 'azimuth': '0.0571'}}], 36: [256, 36, 0.15, {'metrics': {'range': '0.0283', 'azimuth': '0.0591'}}], 37: [256, 36, 0.2, {'metrics': {'range': '0.0279', 'azimuth': '0.0541'}}], 38: [256, 36, 0.25, {'metrics': {'range': '0.0227', 'azimuth': '0.0517'}}], 39: [256, 36, 0.3, {'metrics': {'range': '0.0260', 'azimuth': '0.0457'}}], 40: [256, 49, 0.1, {'metrics': {'range': '0.0289', 'azimuth': '0.0654'}}], 41: [256, 49, 0.15, {'metrics': {'range': '0.0225', 'azimuth': '0.0599'}}], 42: [256, 49, 0.2, {'metrics': {'range': '0.0212', 'azimuth': '0.0593'}}], 43: [256, 49, 0.25, {'metrics': {'range': '0.0197', 'azimuth': '0.0564'}}], 44: [256, 49, 0.3, {'metrics': {'range': '0.0228', 'azimuth': '0.0597'}}], 45: [512, 25, 0.1, {'metrics': {'range': '0.0160', 'azimuth': '0.0325'}}], 46: [512, 25, 0.15, {'metrics': {'range': '0.0162', 'azimuth': '0.0324'}}], 47: [512, 25, 0.2, {'metrics': {'range': '0.0148', 'azimuth': '0.0327'}}], 48: [512, 25, 0.25, {'metrics': {'range': '0.0146', 'azimuth': '0.0315'}}], 49: [512, 25, 0.3, {'metrics': {'range': '0.0154', 'azimuth': '0.0337'}}], 50: [512, 36, 0.1, {'metrics': {'range': '0.0177', 'azimuth': '0.0301'}}], 51: [512, 36, 0.15, {'metrics': {'range': '0.0173', 'azimuth': '0.0297'}}], 52: [512, 36, 0.2, {'metrics': {'range': '0.0165', 'azimuth': '0.0274'}}], 53: [512, 36, 0.25, {'metrics': {'range': '0.0154', 'azimuth': '0.0270'}}], 54: [512, 36, 0.3, {'metrics': {'range': '0.0156', 'azimuth': '0.0289'}}], 55: [512, 49, 0.1, {'metrics': {'range': '0.0176', 'azimuth': '0.0314'}}], 56: [512, 49, 0.15, {'metrics': {'range': '0.0143', 'azimuth': '0.0267'}}], 57: [512, 49, 0.2, {'metrics': {'range': '0.0135', 'azimuth': '0.0249'}}], 58: [512, 49, 0.25, {'metrics': {'range': '0.0125', 'azimuth': '0.0251'}}], 59: [512, 49, 0.3, {'metrics': {'range': '0.0097', 'azimuth': '0.0204'}}], 60: [1024, 25, 0.1, {'metrics': {'range': '0.0130', 'azimuth': '0.0152'}}], 61: [1024, 25, 0.15, {'metrics': {'range': '0.0130', 'azimuth': '0.0154'}}], 62: [1024, 25, 0.2, {'metrics': {'range': '0.0133', 'azimuth': '0.0165'}}], 63: [1024, 25, 0.25, {'metrics': {'range': '0.0131', 'azimuth': '0.0163'}}], 64: [1024, 25, 0.3, {'metrics': {'range': '0.0175', 'azimuth': '0.0226'}}], 65: [1024, 36, 0.1, {'metrics': {'range': '0.0132', 'azimuth': '0.0190'}}], 66: [1024, 36, 0.15, {'metrics': {'range': '0.0129', 'azimuth': '0.0189'}}]}
                out = dataframe_creation(optimisation)
                # write metrics out as csv
                out.to_csv(path_or_buf=QA)

                count += 1
                if count == maxiter:
                    return None

    # perform optimisation on patches, samples and threshold (more parameters can be added)
    looping(maxiter=args.i)


def final_fit_offsets(slc1, slc2, slc1_par, slc2_par, off, reg, qmf, QA, oversampling):

    print("=====")
    print("Final optimisation")
    print("=====\n\n")

    # QA = "D:/Projects/gammaGlacierOffset/data/20200911_20200923.QA"
    df = pd.read_csv(QA)

    bestrun = df.iloc[0]
    print("Optimising with the following parameters:")
    print(bestrun)
    print("\n\n")

    patches = bestrun["patches"]
    samples = bestrun["samples"]
    threshold = bestrun["threshold"]

    # GAMMA
    pg.offset_pwr(slc1, slc2, slc1_par, slc2_par, off, reg, qmf,
                  patches, patches, "-", oversampling, samples, samples,
                  threshold, "-", "-", deramping)
    print("=====")
    print("Offset fitting")
    print("=====")

    # GAMMA
    pg.offset_fit(reg, qmf, off, "-", "-")

def tracking(slc1, slc2, slc1_par, slc2_par, off, offset, ccp, oversampling):

    print("=====")
    print("Offset Tracking")
    print("=====")

    # window sizes
    rwin = 205
    azwin = 1024

    # multilook-faktoren
    rstep = 100
    azstep = 20

    # Start and stop lines
    az_start = "-" # 4000
    az_end = "-"
    r_start = "-"
    r_end = "-" # 13000

    int_filter = 1 # only when oversample = 1

    pg.offset_pwr_tracking(slc1, slc2, slc1_par, slc2_par, off, # INPUT
                           offset, ccp, "-", "-", # offs, ccp, r_patch_size, a_patch_size -> from off
                           "-", oversampling, # text offsets
                           "-", # threshold -> from off
                           rstep, azstep, r_start, r_end, az_start, az_end, # starting and stopping pixel,
                           "-", "-", # lanczos interp, bandwidth
                           deramping, int_filter,
                           0, 0, # printing
                           "-") # cross-correlation for each patch

def displacements(offset, ccp, slc1_par, off, disp,
                  disp_real, disp_imag, disp_ints,
                  out, rmli1, rmli1_par):

    print("=====")
    print("Displacement calculation")
    print("=====")

    mode = 2 # ground range geometry
    thresh = "-"
    pg.offset_tracking(offset, ccp, slc1_par, off, disp, "-",
                       mode, thresh, "-")

    width = int(awkpy(rmli1_par, "range_samples", 2))
    print(width)
    width = width / 10

    # TODO: converting real, imaginary and magnitude to raster maps:
    pg.cpx_to_real(disp, disp_real, width, 0) #
    pg.cpx_to_real(disp, disp_imag, width, 1)
    pg.cpx_to_real(disp, disp_ints, width, 2)

    pg.raspwr(disp_real, width, "-", "-", "-", "-", "-", "-", "-", out)


def main():

    print("\n")
    print("=====")
    print(TYEL + "Processing with method:" + ENDC)
    print(TYEL + method + ENDC)
    print("=====")
    print("\n")

    # TODO: Add -p argument for every step
    # TODO: Init_offset_orbit bei auch koregistrierte SLCs?
    # TODO: Significance of oversampling factors

    # Folder Structure:
    #     | DEM
    #     | SLC
    #     | tuples
    #         | date1_date2
    #              | intensity
    #              | phase
    #         | date3_date4
    #              | intensity
    #              | phase
    #
    # writing to offset files to /tuples/date1_date2/intensity (-a 1 -> Intensity Tracking),
    #                            /tuples/date1_date2/phase (-a 2 -> Fringe Visibility Tracking)

    # USER INPUT #######################
    slc_dir = "../data/SLC"
    tuples_dir = "../data/tuples"
    oversampling = 1  # what does that actually mean?

    # specify ending of file to be used as basename giver
    dict = file_dict(slc_dir = slc_dir, ending=".mosaic_slc")

    # print(dict)
    # dict = {'20200911_20200923': {'20200911': ['20200911_vv_iw2.slc', '20200911_vv_iw2.slc.par'], '20200923': ['20200923_vv_iw2.slc.par', '20200923_vv_iw2.slc']}}

    for datepair in dict:
        date1 = datepair[0:8]
        date2 = datepair[9:17]

        print(date2)
        # concat path
        main_path = os.path.join(tuples_dir, datepair)
        path_datepair = os.path.join(tuples_dir, datepair, method)

        QA = os.path.join(path_datepair, datepair + ".QA")
        off = os.path.join(path_datepair, datepair + ".off")
        reg = os.path.join(path_datepair, datepair + ".reg")
        qmf = os.path.join(path_datepair, datepair + ".qmf")
        snr = os.path.join(path_datepair, datepair + ".snr")
        offset = os.path.join(path_datepair, datepair + ".offset")
        ccp = os.path.join(path_datepair, datepair + ".ccp") # cross-correlation for each patch
        disp = os.path.join(path_datepair, datepair + ".disp")
        disp_real = os.path.join(path_datepair, datepair + ".disp_real")
        disp_imag = os.path.join(path_datepair, datepair + ".disp_imag")
        disp_ints = os.path.join(path_datepair, datepair + ".disp_ints")
        out = os.path.join(path_datepair, datepair + ".temp_displacement_map.tif")

        # fetching SLCs
        # fetching main
        rslcs = [rslc for rslc in os.listdir(main_path) if rslc.endswith(".rslc")]
        rslcs_par = [rslc for rslc in os.listdir(main_path) if rslc.endswith(".rslc.par")]
        rslc1 = [os.path.join(main_path, x) for x in rslcs if date1 in x][0]
        rslc2 = [os.path.join(main_path, x) for x in rslcs if date2 in x][0]
        rslc1_par = [os.path.join(main_path, x) for x in rslcs_par if date1 in x][0]
        rslc2_par = [os.path.join(main_path, x) for x in rslcs_par if date2 in x][0]

        rmli1 = [os.path.join(main_path, rmli) for rmli in os.listdir(main_path) if rmli.endswith(".rmli")][0]
        rmli1_par = [os.path.join(main_path, rmli) for rmli in os.listdir(main_path) if rmli.endswith(".rmli.par")][0]

        # looping through steps indicated by input -s, adding possible -> e.g. `-s 1 2 3 4 5`
        for step in sorted(args.steps):
            if int(step) == 1:
                # delete .off file if existing, initiate .off file with orbit inforamtion
                initiate_offsets(rslc1_par, rslc2_par, off)
            elif int(step) == 2:
                # Optimise parameters patch size, sample number and threshold
                optimise_offsets(rslc1, rslc2, rslc1_par, rslc2_par, off, reg, qmf, QA, oversampling, snr)
            elif int(step) == 3:
                # Fitting .off file with best result from optimisation procedure
                final_fit_offsets(rslc1, rslc2, rslc1_par, rslc2_par, off, reg, qmf, QA, oversampling)
            elif int(step) == 4:
                # Offset Tracking algorithm
                tracking(rslc1, rslc2, rslc1_par, rslc2_par, off, offset, ccp, oversampling)
            elif int(step) == 5:
                displacements(offset, ccp, rslc1_par, off, disp,
                              disp_real, disp_imag, disp_ints,
                              out, rmli1, rmli1_par)
            else:
                pass

if __name__ == '__main__':
    main()