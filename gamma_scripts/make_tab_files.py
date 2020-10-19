#!/usr/bin/env python

"""
Script for creating the tab-files for each slc
    - <date>.slc <date>.slc.par <date>.slc.par.tops
"""
import argparse
import os
from functions import get_dates

# colors
ENDC = '\033[m'
TRED = "\u001b[41;1m"

# parse some arguments
parser = argparse.ArgumentParser(description="Only printing the tab files or creating them")
parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)
args =parser.parse_args()


def make_tab_files(dates_list):
    for date in dates_list:
        slc = os.path.join(slc_dir, date + ".slc")
        slc_par = slc + ".par"
        slc_tops_par = slc + "tops.par"
        tab_name = slc + "_tab"
        tab_content = "{slc} {slc_par} {slc_tops_par}".format(slc=slc, slc_par=slc_par, slc_tops_par=slc_tops_par)
        if not args.print:
            with open("{}".format(tab_name), "w") as tab_file:
                print("Writing Tabfile for date {}".format(date))
                print(tab_name)
                tab_file.write("{}".format(tab_content))
        else:
            print()
            print(TRED + "Creting Tabfile: ", tab_name, ENDC)
            print("         ", tab_content)
            print()

if __name__ == "__main__":
    slc_dir = "../data/SLC"
    dates = get_dates(slc_dir)
    make_tab_files(dates)