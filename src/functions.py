#!/usr/bin/env python

# Python module with some functions that may be useful for many opperations in this module

import re
import os
from datetime import date

#############
# some colors
#############
TGREEN = '\033[32m'  # Green Text
ENDC = '\033[m'
TRED = "\u001b[41;1m"
TYEL = "\u001b[33;1m"
start_bold = "\033[1m"
end_bold = "\033[0;0m"
start_underline = "\033[4m"
end_underline = "\033[0m"

def get_dates(slc_dir, ending=".slc"):

    files_dir = slc_dir
    # find dates based on the slc-files
    files = [f for f in os.listdir(files_dir) if f.endswith(ending)]

    # return a list of the dates as strings
    dates = []
    for f in files:
        try:
            m = re.search(r'^(\d{8}).*', f).group(1)
            if not m in dates:
                dates.append(m)
            else:
                pass
        except AttributeError as err:
            print("found some none matching file")

    return dates

def make_keys_from_slcdir(slc_dir, ending=".slc"):
    """

    :param slc_dir:
    :return: returns a list of strings like [<date1>_<date2>, <date1>_<date2>, ...]
    """
    dates = [x for x in get_dates(slc_dir, ending)]

    dates_keys = []
    for d in dates:
        year1 = int(d[0:4])
        month1 = int(d[4:6])
        day1 = int(d[6:8])
        for o in dates:
            year2 = int(o[0:4])
            month2 = int(o[4:6])
            day2= int(o[6:8])
            if d != o:
                d1 = date(year1, month1, day1)
                d2 = date(year2, month2, day2)
                # check if difference between dates is less than 30 days
                if abs(d2-d1).days <= 30:
                    key = min(d,o)+"_"+max(d,o)
                    if not key in dates_keys:
                        dates_keys.append(key)
                    else:
                        pass
    return dates_keys


def file_dict(slc_dir, ending=".slc"):

    # make keys with <date2>_<date2>
    keys = make_keys_from_slcdir(slc_dir, ending)

    # start final dictionary
    d = {k:None for k in keys}

    # for each datepair
    for k in keys:
        # each value of the first key is another dictionary
        d[k] = {}
        # get all the files for the first date
        date1 = k[0:8]
        date2 = k[9:17]
        files_date1 = [x for x in os.listdir(os.path.join(slc_dir)) if date1 in x]
        files_date2 = [x for x in os.listdir(os.path.join(slc_dir)) if date2 in x]
        d[k][date1] = files_date1
        d[k][date2] = files_date2

    return d

def get_files(slc_dir, image="main", file_ending=[".slc"]):
    """
    retrieve a list of files (.slc, .slc.par, .slc_tab, .slc.tops_par) from either the main or the secondary
    :param type:
    :param referece:
    :return:
    """

    files_dict = file_dict(slc_dir)
    files_all = []

    for date_pair in files_dict:
        if image == "main" or image == "m":
            date_main = date_pair[0:8]
            key1 = date_pair
            key2 = date_main
            files = [file for file in files_dict[key1][key2] for ty in file_ending if file.endswith(ty)]
            files_all.append(files)

        elif image == "secondary" or image == "s":
            date_secondary = date_pair[9:17]
            key1 = date_pair
            key2 = date_secondary
            files = [file for file in files_dict[key1][key2] for ty in file_ending if file.endswith(ty)]
            # check if mosaic is a substring of any of the elements of file_ending
            files_all.append(files)

        else:
            print(TRED + "Choose between Main or Secondary images to retrieve files" + ENDC)
            exit()

    # return flattened list with all files
    #return [f for sublist in files_all for f in sublist]
    # return list of lists
    return files_all


def rec_reg(path, regex):
    """
    find files recursively
    """
    regObj = re.compile(regex)
    res = []
    for root, dirs, fnames in os.walk(path):
        for fname in fnames:
            if regObj.match(fname):
                res.append(os.path.join(root, fname))
    return res

########################################################################
# function to exract the value from the nth colum if the column matches something
########################################################################

def awkpy(file, pattern, col_to_extract):

    if not os.path.isfile(file):
        print("FILE YOU TRY TO FILTER DOESN'T EXIST"); exit()

    with open(file, "r") as src:
        for line_list in src:
            # print(line_list)
            fields = line_list.strip().split() # returns each line as a list of string
            if [string for string in fields if pattern in string]:
                return fields[col_to_extract-1]

def offset_fit_output_stddev(file):
    """
    :param a text file that is the stddout from the function òffset_fit:
    :return: a tuple with (<stddev_range>, <stddev_azimuth>)
    """
    with open(file, "r") as src:
        lines = [line for line in src.readlines()]
        for i in lines:
            m = re.search("^final model.*range:\s*(\d\.\d+).*azimuth:\s*(\d\.\d+)", i)
            if m is not None:
                std_range= float(m.group(1))
                std_azimuth = float(m.group(2))
                return std_range, std_azimuth

if __name__ == "__main__":
    #######################
    # Only for testing on the command line
    # This module is intended to be imported
    #######################
    slc_dir = "../data/SLC"
    b = get_files(slc_dir, file_ending=["mosaic_slc"], image="m")
