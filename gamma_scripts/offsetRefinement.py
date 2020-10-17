#########################################
# Window Size Refinement loops
#########################################

import os
import re
import sys

if sys.platform == "win32":
    pass
else:
    kernel = str(os.system("uname -r"))
    print(kernel)

    if kernel == "3.10.0-957.el7.x86_64":
        try:
            import py_gamma as pg
            print("py_gamma successfully loaded")
        except ImportError as err:
            print("The module `py_gamma` needs to be installed")
    else:
        print("Kernel not identical")
        import py_gamma as pg

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

tracking_algorithm = 1

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

def reading_QA():
    QA = os.path.join(dir, dates + ".QA")

    print(QA)
    with open(QA) as f:
        lines = f.readlines()
        for i in lines:
            print(i)
        f.close()

    # with open(QA) as f:
    #     lines = f.readlines()
    #     if re.search("width", lines):
    #         dem_width = lines
    #     if re.search("lines", lines):
    #         dem_lines = lines
    #     print("Width: ", dem_width, "\n",
    #           "Lines: ", dem_lines, "\n")
    #     f.close()


def optimise_offsets(slc1, slc2, slc1_par, slc2_par, off):

    reg_offsets = os.path.join(dir, dates + ".reg_offsets")
    qmf_offsets = os.path.join(dir, dates + ".qmf_offsets")
    QA = os.path.join(dir, dates + ".QA")
    if os.path.isfile(QA):
        os.remove(QA)

    QA_temp = os.path.join(dir, dates + ".QA_temp")

    # Metrics static ------
    # Window size <- to be optimised
    patch_rn = 128
    patch_az = 128

    # Number of offset estimates, correlation function window size <- to be optimised
    samples_rn = 32
    samples_az = 32

    # Metrics looping -----
    sizes = [2 ** x for x in range(1, 10)]
    samples = [x ** 2 for x in range(5, 10)]




    oversampling = 2 # what does that actually mean?
    theshold = 0.001 # <- to be optimised

    # Sentinel-1 TOPS acquisitions need to be deramped. (Is this done already in S1_mosaic_TOPS?)
    deramping = 1


    for patch in sizes:
        for sample in samples:
            pass


    pg.offset_pwr(slc1, slc2, slc1_par, slc2_par, off, reg_offsets, qmf_offsets,
                  patch_rn, patch_az, "-", oversampling, samples_rn, samples_az,
                  theshold, "-", "-", deramping)

    # saving console output to file

    # TODO: output is saved in file, not really functional...
    sys.stdout = open(QA, 'w')
    pg.offset_fit(reg_offsets, qmf_offsets, off, "-", "QA")

    # os.remove(QA_temp)


def main():
    # create_offsets(slc1_par, slc2_par)
    # init_offset_orbit(slc1_par, slc2_par, off)
    optimise_offsets(slc1, slc2, slc1_par, slc2_par, off)
    reading_QA()

if __name__ == '__main__':
    main()