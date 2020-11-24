#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################
# Window Size Refinement loops
#########################################

import argparse
import sys
from io import StringIO
import py_gamma as pg

from functions import *

##################
# parse option to work locally or on server
##################

# parse some arguments
parser = argparse.ArgumentParser(description="Glacier Offset Tracking in 5 steps")
# get positional arguments
parser.add_argument("-s", "--step", dest="steps",
                    help="(input) initiate offset file with parameter file and orbit information (1),"
                         "optimise offsets (2)", default=[0],
                    nargs="+", type=int)

parser.add_argument("-w", "--windows", dest="windows",
                    help="(input) bool if multiple patches should be produced or not [defaults False]",
                    action="store_const", const=True)

parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)

parser.add_argument("-t", "--threshold", dest="thresh",
                    help="(input) threshold of cross-correlation which displacements are to be included",
                    default=[0.01], type=float)

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

    cmd1 = f"create_offset {slc1_par} {slc1_par} {off} 1"

    pg.create_offset(slc1_par, slc2_par, off, "1") if not args.print else print(cmd1)

    f.close()
    sys.stdin = sysinput  # bring std input back


def offset_pwr(slc1, slc2, slc1_par, slc2_par, off, reg, qmf, oversampling):
    # optimised by looping! -> in paper!
    patch_rn = 512
    patch_az = patch_rn / 5  # patches to be rectangular
    samples_rn = 16
    samples_az = 50  # many, because of the large water content in the upper area of the scenes

    threshold = args.thresh[0]

    print("=====")
    print(TYEL + "Number Patches/Search Window:" + ENDC)
    print(f"range: {patch_rn}; azimuth: {patch_az}")
    print(TYEL + "Number Samples (evenly distributed over range and azimuth distance):" + ENDC)
    print(f"range: {samples_rn}; azimuth: {samples_az}")
    print("Threshold is set constant at {}".format(threshold))
    print("=====")

    cmd1 = f"offset_pwr {slc1} {slc2} {slc1_par} {slc2_par} {off} {reg} {qmf} {patch_rn} {patch_az} " \
           f"- {oversampling} {samples_rn} {samples_az} {threshold} - - {deramping}"

    cmd2 = f"offset_fit {reg} {qmf} {off} - -"

    if not args.print:
        pg.offset_pwr(slc1, slc2, slc1_par, slc2_par, off, reg, qmf,
                      patch_rn, patch_az, "-", oversampling, samples_rn, samples_az,
                      threshold, "-", "-", deramping)

        print("=====")
        print("Offset fitting")
        print("=====")
        pg.offset_fit(reg, qmf, off, "-", "-")

    else:
        print(cmd1)
        print(cmd2)
        return None


def tracking(slc1, slc2, slc1_par, slc2_par, off, offset, ccp, offset_QA, rmli1_par, ccs):
    # Parameter setting
    
    print("\n")
    print("=====")
    print(TYEL + "Processing with method:" + ENDC)
    print(TYEL + method + ENDC)
    print("=====")
    print("\n")

    if args.windows:
        azwins = [2 ** x for x in range(3, 7)]
        rwins = [x * 5 for x in azwins]  # multilook factor ratio of Sentinel-1
    else:
        rwin = 160
        azwin = 32

    ###### STEPS
    # multilook-faktoren (steps in range & azimuth) = samples!
    rstep = 30
    azstep = 6

    ##### OVERSAMPLING
    oversampling = 1  # no influence on geometry! Not making displacement results better either...

    # mli parameter:
    slc_width = int(awkpy(slc1_par, "range_samples", 2))  # range 30 azimuth 6
    mli_width = int(awkpy(rmli1_par, "range_samples", 2))  # range 30 azimuth 6

    print("Width of SLC:", slc_width)
    print("Width of MLI:", mli_width)
    print("Width of displacement map:", slc_width / rstep)
    print("=====\n")

    # number of offsets
    # range: 827

    # Start and stop lines
    az_start = "-"  # 4000
    az_end = "-"
    r_start = "-"
    r_end = "-"  # 13000

    int_filter = 1  # only when oversample = 1
    threshold = args.thresh[0]

    print("=====")
    print("Offset Tracking")
    print("=====")

    if not args.windows:

        print("Azimuth Window:", azwin)
        print("Range Window:", rwin)

        cmd = f"offset_pwr_tracking {slc1} {slc2} {slc1_par} {slc2_par} {off} {offset} {ccp} {rwin} {azwin} {offset_QA} " \
              f"{oversampling} {threshold} {rstep} {azstep} {r_start} {r_end} {az_start} {az_end} - - " \
              f"{deramping} {int_filter} 0 0 {ccs}"

        if not args.print:
            pg.offset_pwr_tracking(slc1, slc2, slc1_par, slc2_par, off,  # INPUT
                                   offset, ccp, rwin, azwin,
                                   # offs, ccp, r_patch_size, a_patch_size -> from off
                                   offset_QA, oversampling,  # text offsets
                                   threshold,  # threshold -> from off
                                   rstep, azstep, r_start, r_end, az_start, az_end,  # starting and stopping pixel,
                                   "-", "-",  # lanczos interp, bandwidth
                                   deramping, int_filter,
                                   0, 0,  # printing
                                   ccs)  # cross-correlation for each patch
            print("=======")

        else:
            print(cmd)

    else:
        print("using muliple window inputs  . . .")
        for window in zip(azwins, rwins):

            # ask if many window sizes are to be processed or just one

            azwin = window[0]
            rwin = window[1]

            # naming addition for window sizes:
            names_to_change = [offset, ccp, offset_QA]
            names = []

            for name in names_to_change:
                end = name.split(sep=".")[-1]
                front = name.split(sep=".")[0:-1]
                front = ".".join(front)

                full = f"{front}_{azwin}.{end}"
                print(full)
                names.append(full)

            offset_patch = names[0]
            ccp_patch = names[1]
            offset_QA_patch = names[2]

        print("Azimuth Window:", azwin)
        print("Range Window:", rwin)

        cmd = f"offset_pwr_tracking {slc1} {slc2} {slc1_par} {slc2_par} {off} {offset_patch} {ccp_patch} {rwin} {azwin} {offset_QA_patch} " \
              f"{oversampling} {threshold} {rstep} {azstep} {r_start} {r_end} {az_start} {az_end} - - " \
              f"{deramping} {int_filter} 0 0 -"

        if not args.print:
            pg.offset_pwr_tracking(slc1, slc2, slc1_par, slc2_par, off,  # INPUT
                                   offset_patch, ccp_patch, rwin, azwin,
                                   # offs, ccp, r_patch_size, a_patch_size -> from off
                                   offset_QA_patch, oversampling,  # text offsets
                                   threshold,  # threshold -> from off
                                   rstep, azstep, r_start, r_end, az_start, az_end,  # starting and stopping pixel,
                                   "-", "-",  # lanczos interp, bandwidth
                                   deramping, int_filter,
                                   0, 0,  # printing
                                   "-")  # cross-correlation for each patch
            print("=======")

        else:
            print(cmd)


def displacements(offset, ccp, ccs, slc1_par, off, disp,
                  disp_real, disp_imag, disp_mag,
                  rmli1_par):
    print("=====")
    print("Displacement calculation")
    print("=====")

    mode = 2  # ground range geometry
    thresh = args.thresh[0]  # or from .off file

    cmd = f"offset_tracking {offset} {ccp} {slc1_par} {off} {disp} - {mode} {thresh} -"
    pg.offset_tracking(offset, ccp, slc1_par, off, disp, "-", mode, thresh, "-") if not args.print else print(cmd)

    width = int(awkpy(rmli1_par, "range_samples", 2))
    print("Width:", width)

    width = 827

    pg.cpx_to_real(disp, disp_real, width, 0) # range displacements
    pg.cpx_to_real(disp, disp_imag, width, 1) # azimuth displacements
    pg.cpx_to_real(disp, disp_mag, width, 3) # both = magnitude

def main():


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

    # specify ending of file to be used as basename giver
    dict = file_dict(slc_dir=slc_dir, ending=".mosaic_slc")
    datepairs = os.listdir(tuples_dir)

    for datepair in datepairs:

        # datepair = "20200911_20200923"
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
        ccs = main_path + ".ccs" # standard deviation of cross-correlation for each path
        disp = main_path + ".disp"
        disp_real = main_path + ".disp.real"
        disp_imag = main_path + ".disp.imag"
        disp_mag = main_path + ".disp.mag"
        offset_QA = main_path + ".offset_QA"


        # fetching SLCs
        # fetching main
        rslcs = [rslc for rslc in os.listdir(tuple) if rslc.endswith(".rslc")]
        rslcs_par = [rslc for rslc in os.listdir(tuple) if rslc.endswith(".rslc.par")]
        rslc1 = [os.path.join(tuple, x) for x in rslcs if date1 in x][0]
        rslc2 = [os.path.join(tuple, x) for x in rslcs if date2 in x][0]
        rslc1_par = [os.path.join(tuple, x) for x in rslcs_par if date1 in x][0]
        rslc2_par = [os.path.join(tuple, x) for x in rslcs_par if date2 in x][0]


        rmli1_par = [os.path.join(tuple, rmli) for rmli in os.listdir(tuple) if rmli.endswith(".rmli.par")][0]

        # looping through steps indicated by input -s, adding possible -> e.g. `-s 1 2 3 4 5`
        for step in sorted(args.steps):
            if int(step) == 1:
                # delete .off file if existing, initiate .off file with orbit inforamtion
                initiate_offsets(rslc1_par, rslc2_par, off)
            elif int(step) == 2:
                # Using moving windows for optimising the polynomial function
                offset_pwr(rslc1, rslc2, rslc1_par, rslc2_par, off, reg, qmf, QA)
            elif int(step) == 3:
                # Offset Tracking algorithm
                tracking(rslc1, rslc2, rslc1_par, rslc2_par, off, offset, ccp, offset_QA, rmli1_par, ccs)
            elif int(step) == 4:
                # Calculating actual displacements
                displacements(offset, ccp, ccs, rslc1_par, off, disp,
                              disp_real, disp_imag, disp_mag,
                              rmli1_par)
            else:
                pass
        # break

if __name__ == '__main__':
    main()
