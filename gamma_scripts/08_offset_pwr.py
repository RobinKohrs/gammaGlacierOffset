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

parser.add_argument("-i", "--iters", dest="i",
                    help="(input) is number of iterations performed as optimisation of the offset [int]",
                    default=3, type=int)

parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)

# get the arguments
global args
args = parser.parse_args()

if args.print:
    print("working locally...")
else:
    try:
        import py_gamma as pg
        print("\nGAMMA successfully installed")
    except ImportError as err:
        print("Working on the server...")
        print("However the py_gamma-module can not be loaded...")
        print("Make sure its on $PATH? or PYTHONPATH?")
        exit(-1)

#########################################
# USER INPUT
#########################################

deramping = 1  # yes
method = "intensity"

#########################################
# CREATING OFFSETS (actually belongs to another script
#########################################

def initiate_offsets(slc1_par, slc2_par, off):
    # manual value input needs to be overrun automatically

    override_input = '\n\n\n\n\n\n\n'

    r_pos = 2000  # range position orbit init
    az_pos = 11000  # azimuth position orbit init

    if os.path.isfile(off):
        os.remove(off)

    print("=====")
    print("Creating offset file from SLC parameter file")
    print(TGREEN + method + ENDC)
    print("=====\n")

    sysinput = sys.stdin  # save std input
    f = StringIO(override_input)  # override input 7x
    sys.stdin = f
    print(sys.stdin)

    cmd1 = f"create_offset {slc1_par} {slc1_par} {off} 1"

    pg.create_offset(slc1_par, slc2_par, off, "1") if not args.print else print(cmd1)

    f.close()
    sys.stdin = sysinput  # bring std input back


    # print("=====")
    # print("Initiating offsets with precise Sentinel-1 orbit information")
    # print(TGREEN + "Orbit Reference Position" + ENDC)
    # print("Range:", r_pos)
    # print("Azimuth:", az_pos)
    # print("=====\n")
    #
    # cmd2 = f"init_offset_orbit {slc1_par} {slc2_par} {off} {r_pos} {az_pos}"
    #
    # pg.init_offset_orbit(slc1_par, slc2_par, off, r_pos, az_pos) if not args.print else print(cmd2)
    #
    # print(f"Full initiation successful. \nOffset file: {off}.")


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

    dict = {"range": sd_metric[0],
            "azimuth": sd_metric[1]}
    return (dict)


def optimise_offsets(slc1, slc2, slc1_par, slc2_par, off, reg, qmf, QA, oversampling):
    # delete QA file
    if os.path.isfile(QA):
        os.remove(QA)

    # Metrics static ------
    patch_rn, patch_az = 512, 102
    samples_rn, samples_az = 18, 50

    # Metrics looping -----
    # Window size <- to be optimised
    patches = [2 ** x for x in range(7, 11)]
    patches = [512]

    # Number of offset estimates, correlation function window size <- to be optimised
    samples = [x ** 2 for x in range(8, 12)]
    samples = [64]

    threshold = 0.01  # from user guide
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

                print("Offset Optimisation for 'window size' & 'samples per window'")
                print("Number Patches: {}".format(patch))
                print("Number Samples: {}".format(sample))
                print("Threshold is constant at {}".format(threshold))
                print("=====")

                cmd1 = f"offset_pwr {slc1} {slc2} {slc1_par} {slc2_par} {off} {reg} {qmf} {patch_rn} {patch_az} " \
                      f"- {oversampling} {samples_rn} {samples_az} {threshold} - - {deramping}"

                cmd2 = f"offset_fit {reg} {qmf} {off} - -"

                if not args.print:
                    pg.offset_pwr(slc1, slc2, slc1_par, slc2_par, off, reg, qmf,
                                  patch_rn, patch_az, "-", oversampling, samples_rn, samples_az,
                                  threshold, "-", "-", deramping)
                else:
                    print(cmd1)
                    print(cmd2)
                    return None

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
                optimisation[count] = [patch, sample, threshold, {"metrics": qa_read}]
                print(optimisation)

                out = dataframe_creation(optimisation)
                # write metrics out as csv
                out.to_csv(path_or_buf=QA)

                count += 1
                if count == maxiter:
                    return None

    # perform optimisation on patches, samples and threshold (more parameters can be added)
    looping(maxiter=args.i)


def final_fit_offsets(slc1, slc2, slc1_par, slc2_par, off, reg, qmf, QA, oversampling):

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
    cmd1 = f"offset_pwr {slc1} {slc2} {slc1_par} {slc2_par} {off} {reg} {qmf} {patches} {patches} - {oversampling} " \
          f"{samples} {samples} {threshold} - - {deramping}"
    cmd2 = f"offset_fit {reg} {qmf} {off} - -"
    if not args.print:
        # final offset estimation
        print("=====")
        print("Final optimisation")
        print("=====\n\n")

        pg.offset_pwr(slc1, slc2, slc1_par, slc2_par, off, reg, qmf,
                  patches, patches, "-", oversampling, samples, samples,
                  threshold, "-", "-", deramping)

        # final fitting
        print("=====")
        print("Offset fitting")
        print("=====")

        pg.offset_fit(reg, qmf, off, "-", "-")
    else:
        print(cmd1)
        print(cmd2)

def tracking(slc1, slc2, slc1_par, slc2_par, off, offset, ccp, offset_QA, rmli1_par):
    # Parameter setting

    # window sizes in multi-look ratio, determines computation speed massively
    rwin = 320
    azwin = 64

    # multilook-faktoren (steps in range & azimuth) = samples!
    rstep = 60
    azstep = 12
    oversampling = 2 # hopefully leverages the step sizes before to 30m resolution afterall

    # mli parameter:
    mli_width = int(awkpy(rmli1_par, "range_samples", 2)) # range 10 azimuth 2
    mli_lines = int(awkpy(rmli1_par, "azimuth_lines", 2))

    # number of offsets
    # range: 827

    # Start and stop lines
    az_start = "-"  # 4000
    az_end = "-"
    r_start = "-"
    r_end = "-"  # 13000

    int_filter = 1  # only when oversample = 1
    threshold = 0.1

    print("=====")
    print("Offset Tracking")
    print("=====")

    cmd = f"offset_pwr_tracking {slc1} {slc2} {slc1_par} {slc2_par} {off} {offset} {ccp} {rwin} {azwin} {offset_QA} " \
          f"{oversampling} {threshold} {rstep} {azstep} {r_start} {r_end} {az_start} {az_end} - - " \
          f"{deramping} {int_filter} 0 0 -"

    if not args.print:
        pg.offset_pwr_tracking(slc1, slc2, slc1_par, slc2_par, off,  # INPUT
                           offset, ccp, rwin, azwin,  # offs, ccp, r_patch_size, a_patch_size -> from off
                           offset_QA, oversampling,  # text offsets
                           threshold,  # threshold -> from off
                           rstep, azstep, r_start, r_end, az_start, az_end,  # starting and stopping pixel,
                           "-", "-",  # lanczos interp, bandwidth
                           deramping, int_filter,
                           0, 0,  # printing
                           "-")  # cross-correlation for each patch
        print("=======")
        print("Width of displacement map:", mli_width/rstep)
        print("Wdith of MLI:", )
    else:
        print(cmd)


def displacements(offset, ccp, slc1_par, off, disp,
                  disp_real, disp_imag, disp_ints,
                  out, rmli1, rmli1_par):
    print("=====")
    print("Displacement calculation")
    print("=====")

    mode = 2  # ground range geometry
    thresh = "-" # -> from .off file

    cmd = f"offset_tracking {offset} {ccp} {slc1_par} {off} {disp} - {mode} {thresh} -"

    pg.offset_tracking(offset, ccp, slc1_par, off, disp, "-", mode, thresh, "-") if not args.print else print(cmd)

    width = int(awkpy(rmli1_par, "range_samples", 2))
    width = 620
    print("Width:", width)

    # TODO: converting real, imaginary and magnitude to raster maps:
    pg.cpx_to_real(disp, disp_real, width, 0)  #
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
    tuples_dir = "../data/tuples/"
    oversampling = 2  # what does that actually mean? Is this to be set globally?

    # specify ending of file to be used as basename giver
    dict = file_dict(slc_dir=slc_dir, ending=".mosaic_slc")

    # print(dict)
    # dict = {'20200911_20200923': {'20200911': ['20200911_vv_iw2.slc', '20200911_vv_iw2.slc.par'], '20200923': ['20200923_vv_iw2.slc.par', '20200923_vv_iw2.slc']}}

    for datepair in dict:

        datepair = "20200911_20200923"
        date1 = datepair[0:8]
        date2 = datepair[9:17]

        # concat path
        tuple = os.path.join(tuples_dir, datepair)
        main_path = os.path.join(tuples_dir, datepair, method, datepair)

        # file all inside the datepair tuple and in the method folder "intensity"
        QA = main_path + ".QA"
        off = main_path + ".off"
        reg = main_path + ".reg"
        qmf = main_path + ".qmf"
        offset = main_path + ".offset"
        ccp = main_path + ".ccp"  # cross-correlation for each patch
        disp = main_path + ".disp"
        disp_real = main_path + ".disp_real"
        disp_imag = main_path + ".disp_imag"
        disp_ints = main_path + ".disp_ints"
        out = main_path + ".temp_displacement_map.tif"
        offset_QA = main_path + ".offset_QA"

        # fetching SLCs
        # fetching main
        rslcs = [rslc for rslc in os.listdir(tuple) if rslc.endswith(".rslc")]
        rslcs_par = [rslc for rslc in os.listdir(tuple) if rslc.endswith(".rslc.par")]
        rslc1 = [os.path.join(tuple, x) for x in rslcs if date1 in x][0]
        rslc2 = [os.path.join(tuple, x) for x in rslcs if date2 in x][0]
        rslc1_par = [os.path.join(tuple, x) for x in rslcs_par if date1 in x][0]
        rslc2_par = [os.path.join(tuple, x) for x in rslcs_par if date2 in x][0]

        rmli1 = [os.path.join(tuple, rmli) for rmli in os.listdir(tuple) if rmli.endswith(".rmli")][0]
        rmli1_par = [os.path.join(tuple, rmli) for rmli in os.listdir(tuple) if rmli.endswith(".rmli.par")][0]

        # looping through steps indicated by input -s, adding possible -> e.g. `-s 1 2 3 4 5`
        for step in sorted(args.steps):
            if int(step) == 1:
                # delete .off file if existing, initiate .off file with orbit inforamtion
                initiate_offsets(rslc1_par, rslc2_par, off)
            elif int(step) == 2:
                # Optimise parameters patch size, sample number and threshold
                optimise_offsets(rslc1, rslc2, rslc1_par, rslc2_par, off, reg, qmf, QA, oversampling)
            elif int(step) == 3:
                # Fitting .off file with best result from optimisation procedure
                final_fit_offsets(rslc1, rslc2, rslc1_par, rslc2_par, off, reg, qmf, QA, oversampling)
            elif int(step) == 4:
                # Offset Tracking algorithm
                tracking(rslc1, rslc2, rslc1_par, rslc2_par, off, offset, ccp, offset_QA, rmli1_par)
            elif int(step) == 5:
                displacements(offset, ccp, rslc1_par, off, disp,
                              disp_real, disp_imag, disp_ints,
                              out, rmli1, rmli1_par)
            else:
                pass
        break

if __name__ == '__main__':
    main()
