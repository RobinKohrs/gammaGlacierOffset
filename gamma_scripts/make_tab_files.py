#!/usr/bin/env python

"""
Script for creating the tab-files for each slc
    - <date>.slc <date>.slc.par <date>.slc.par.tops
"""
import os
from functions import get_dates

def make_tab_files(dates_list):
    for date in dates_list:
        slc = date + ".slc"
        slc_par = slc + ".par"
        slc_tops_par = slc + "tops.par"
        tab_name = os.path.join(slc_dir, slc + "_tab")
        tab_content = "{slc} {slc_par} {slc_tops_par}".format(slc=slc, slc_par=slc_par, slc_tops_par=slc_tops_par)
        with open("{}".format(tab_name), "w") as tab_file:
            print("Writing Tabfile for date {}".format(date))
            print(tab_name)
            tab_file.write("{}".format(tab_content))




if __name__ == "__main__":
    slc_dir = "../data/SLC"
    dates = get_dates(slc_dir)
    make_tab_files(dates)