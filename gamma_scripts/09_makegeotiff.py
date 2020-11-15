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
import itertools
from functions import *
import subprocess



def get_all_files(dir):

    # all top_level_directories
    all_dirs = os.listdir(dir)
    all_files = []

    # for all top level directories
    for j in all_dirs:

        # build the full path
        full_path = os.path.join(dir, j)

        # if its a directory
        if os.path.isdir(full_path):
            all_files = all_files + get_all_files(full_path)
        else:
            all_files.append(full_path)

    return all_files


def geocode_back(list_of_files):

    """
    input parameters:
  data_in       (input) data file (format as specified by format_flag parameter)
  width_in      width of input data file
  lookup_table  (input) lookup table containing pairs of real-valued input data coordinates
  data_out      (output) output data file
  width_out     width of gc_map lookup table, output file has the same width
  nlines_out    number of lines of output data file (enter - or 0 for default: number of lines in gc_map)
  interp_mode   interpolation mode (enter - for default)
                  0: nearest-neighbor
                  1: bicubic spline (default)
                  2: bicubic-log spline, interpolates log(data)
                  3: bicubic-sqrt spline, interpolates sqrt(data)
                  4: B-spline interpolation (default B-spline degree: 5)
                  5: B-spline interpolation sqrt(x) (default B-spline degree: 5)
                  6: Lanczos interpolation (default Lanczos function order: 5)
                  7: Lanczos interpolation sqrt(x) (default Lanczos function order: 5)
                NOTE: log and sqrt interpolation modes should only be used with non-negative data!
  dtype         input/output data type (enter - for default)
                  0: FLOAT (default)
                  1: FCOMPLEX
                  2: SUN/BMP/TIFF 8 or 24-bit raster image
                  3: UNSIGNED CHAR
                  4: SHORT
                  5: DOUBLE
  lr_in         input  SUN/BMP/TIFF raster image flipped left/right (enter - for default: 1: not flipped (default), -1: flipped)
  lr_out        output SUN/BMP/TIFF raster image flipped left/right (enter - for default: 1: not flipped (default), -1: flipped)
  order         Lanczos function order or B-spline degree (2->9) (enter - default: 5)
  e_flag        extrapolation flag (enter - for default)
                  0: do not extragpolate (default)
                  1: extrapolate up to 0.5 pixels beyond input edges

    """

    for f in list_of_files:

        # find mli width
        f_basepath_list = os.path.dirname(f).split("/")[:-1]
        basepath_strings = "/".join(f_basepath_list)
        date = basepath_strings.split("/")[-1]
        date_main = date[0:8]
        mli = [os.path.join(basepath_strings,x) for x in os.listdir(basepath_strings) if date_main in x and x.endswith(".rmli.par")][0]

        # in dem PDF S1_tracking nehmen sie die gleichen width_out width_in, die sie in geocode
        # verwenden um das DEM in die slant-range mli geometrie zu bringen
        # ich glaube, da wir für die Erstellung des MLI, als auch für range-steps u. azimuth-steps die gleiche Auflösung verwenden
        # (30,60) sind die Input-Width (bestimmt durch die range/az steps) und die output-widht (bestimmt durch die MLI-breite und HÖHE)
        # gleich

        # die Input-breite denke ich können wir aus dem .off-file nehmen?!

        # die output breite und höhe
        with open(mli, "r") as src:
            lines = [line for line in src.readlines()]
            for i in lines:
                w = re.search("^range_samples:\s*(\d*)", i)
                if w is not None:
                    width_mli = w.group(1)

                h = re.search("^azimuth_lines:\s*(\d*)", i)
                if h is not None:
                    height_mli = h.group(1)

        # find lookup table
        dem_dir = "../data/DEM/"
        lt = [file for file in os.listdir(dem_dir) if date_main in file and file.endswith(".lt")][0]

        # data out
        data_out = os.path.join(f + ".geo")







def main():

    # directories for all two data dependent files
    tuple_dir = "../data/tuples/"

    # make a list of all fildes
    all_files = get_all_files(tuple_dir)

    # filter the files you want
    file_endings = [".imag", ".real", ".mag"]
    files_to_geocode = [f for f in all_files if f.endswith(file_endings[0]) or f.endswith(file_endings[1]) or f.endswith(file_endings[2])]

    # geocode_back
    geocode_back(files_to_geocode)


#--------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
#--------------------------------------------------------------------------------