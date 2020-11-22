#!/usr/bin/env python

"""
Script for creating mosaics of subswatch 2
    - <date>.slc <date>.slc.par <date>.slc.par.tops
"""
import os
from functions import get_dates
import argparse

# parse some arguments
parser = argparse.ArgumentParser(description="Multilooking parameter")
# get positional arguments
parser.add_argument("-r", "--range", dest="range",
                    help="(input) looks in range (default = 30)", default=30, type=int)

parser.add_argument("-a", "--azimuth", dest="azimuth",
                    help="(input) looks in azimuth (default = 6)", default=6, type=int)

parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)

args =parser.parse_args()

def make_mosaics(dates, range, azimuth):
    """

    :param dates: list of dates
    :return:
    """
    # find corresponding files for the dates
    for date in dates:
        slc = [os.path.join(slc_dir, slc) for slc in os.listdir(slc_dir) if date in slc and slc.endswith((".slc"))][0]
        tab_file = [os.path.join(slc_dir, x) for x in os.listdir(slc_dir) if date in x and x.endswith("slc_tab")][0]
        slc_mosaic = slc[:-4] + ".mosaic_slc"
        slc_mosaic_par = slc_mosaic + ".par"
        cmd = "SLC_mosaic_S1_TOPS {tab_file} {slc_mosaic} {slc_mosaic_par} {rl} {al}".format(tab_file = tab_file,
                                                                                             slc_mosaic = slc_mosaic,
                                                                                             slc_mosaic_par = slc_mosaic_par,
                                                                                             rl=range, al=azimuth)

        # chekc if mosaic not already exists
        if not os.path.isfile(slc_mosaic):
            os.system(cmd) if not args.print else print(cmd)
        else:
            print("The mosaics already exists")

if __name__ == "__main__":
    slc_dir = "../data/SLC"
    dates = get_dates(slc_dir)
    make_mosaics(dates, range=args.range, azimuth=args.azimuth)