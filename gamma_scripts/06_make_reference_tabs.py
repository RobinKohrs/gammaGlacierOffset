#!/usr/bin/env python

######################
#
# Module for for geocoding the dem to range doppler coordinates
#
######################

import os
from functions import *
import argparse

# parse some arguments
parser = argparse.ArgumentParser(description="")
parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)
args =parser.parse_args()

def geocode():
    """
    will produce the "hgt" files
    :return:
    """

    # get all the lookup-tables for the masters;
    # Returns a list of strings of the absolute paths
    main_lts = rec_reg(dem_dir, ".*\.lt$")

    for lt in main_lts:

        # make identifier for each master date
        identifier = os.path.basename(lt)[0:15]

        # lookup-table path
        lt = lt

        eqa_dem_par = rec_reg(dem_dir, ".*dem.par.*")[0]
        eqa_dem = rec_reg(dem_dir, "EQA.dem$")[0]
        dem_par = rec_reg(dem_dir, "DEM.par$")[0]
        dem_width = int(awkpy(eqa_dem_par, "width", 2))
        hgt_out = os.path.join(dem_dir, identifier + ".hgt")

        # get the width of the mosaiced, munltilook mli
        reg = identifier + ".mosaic.mli.par"

        # returns a list with
        mli_file = rec_reg(slc_dir, reg)[0]
        mli_width = int(awkpy(mli_file, "range_samples", 2))
        mli_height = int(awkpy(mli_file, "azimuth_lines", 2))

        # build the cmd
        cmd = f"geocode {lt} {eqa_dem} {dem_width} {hgt_out} {mli_width} {mli_height} 2 0"
        os.system(cmd) if not args.print else print(cmd)

def reference_tabs():

    # find all the main - secondary pairs
    secondary_dates = [x[0][:15] for x in get_files(slc_dir, image="s")]
    for i in secondary_dates:
        identifier = os.path.join(slc_dir, i) # yyyymmdd_vv_iw2
        rslc = identifier + ".rslc"
        rslc_par = identifier + ".rslc.par"
        rslc_par_tops = identifier + ".rslc_tops.par"
        reference_tab_content = f"{rslc} {rslc_par} {rslc_par_tops}"
        # name of the tab file
        tab_name = os.path.join(slc_dir, os.path.basename(identifier) + ".ref_tab")
        with open(f"{tab_name}", "w") as tab_file:
            if not args.print:
                print(TRED + "Writing tab file: {}\nWith Content: ".format(tab_name) + ENDC)
                print("        " + reference_tab_content)
                tab_file.write(reference_tab_content)
            else:
                print("Writing tab file:\n " + TRED + tab_name+ ENDC)
                print("        " + reference_tab_content)

def main():
    # geocode()
    reference_tabs()


if __name__ == "__main__":
    slc_dir = "../data/SLC"
    dem_dir = "../data/DEM"
    main()