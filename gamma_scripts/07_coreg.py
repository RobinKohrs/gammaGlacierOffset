#!/usr/bin/env python

######################
#
# Module for for coregistering each main with each secondary
#
######################

import argparse

from functions import *

# parse some arguments
parser = argparse.ArgumentParser(description="")
parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)
args = parser.parse_args()


def coreg(slc_dir, dem_dir, tuples_dir):
    # get all the date combos
    date_combinations = [x for x in os.listdir(tuples_dir)]
    
    # for each combination
    for date in date_combinations:
        # Was sind das für dateien SCL1_id SLC2_IF
        main_date = date[0:8]
        second_date = date[9:17]
        main_date_tuples = os.path.join(tuples_dir, date, date[0:8])
        second_date_tuples = os.path.join(tuples_dir, date, date[9:17])
        main_date_slcdir = os.path.join(slc_dir, date[0:8])
        second_date_slcdir = os.path.join(slc_dir, date[9:17])
        
        # Das können wir öfter nutzen um alle datein für den Master aus dem SLC ORdner zurückzubekommen
        main_files_all = file_dict(slc_dir)[date][date[0:8]]
        second_files_all = file_dict(slc_dir)[date][date[9:17]]
        
        # get the necessary information for the main date
        main_tab = [os.path.join(slc_dir, x) for x in main_files_all if x.endswith("slc_tab")][0]
        main_slc = [os.path.join(slc_dir, x) for x in main_files_all if x.endswith(".slc")][0]
        
        # get the necessary information for the secondary date
        second_tab = [os.path.join(slc_dir, x) for x in second_files_all if x.endswith("slc_tab")][0]
        second_slc = [os.path.join(slc_dir, x) for x in second_files_all if x.endswith(".slc")][0]
        
        # reference_tab
        ref_tab = [os.path.join(slc_dir, x) for x in second_files_all if x.endswith(".ref_tab")][0]
        
        # main hgt image
        main_hgt = rec_reg(dem_dir, ".*{}.*\.hgt".format(main_date))[0]
        
        out_dir = os.path.join(tuples_dir, date)
        
        # build cmd
        cmd = f"ScanSAR_coreg.py {main_tab} {main_date} {second_tab} {second_date} {ref_tab} {main_hgt} 30 6 - - 0.8 0.01 0.8 --wdir {out_dir}"
        
        os.system(cmd) if not args.print else print(cmd)


def main():
    slc_dir = "../data/SLC"
    dem_dir = "../data/DEM"
    tuples_dir = "../data/tuples"
    coreg(slc_dir, dem_dir, tuples_dir)


if __name__ == "__main__":
    main()
