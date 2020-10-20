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

def get_dates(slc_dir):

    files_dir = slc_dir
    # find dates based on the slc-files
    files = [f for f in os.listdir(files_dir) if f.endswith(".slc")]

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

def make_keys_from_slcdir(slc_dir):
    """

    :param slc_dir:
    :return: returns a list of strings like [<date1>_<date2>, <date1>_<date2>, ...]
    """
    dates = [x for x in get_dates(slc_dir)]

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


def file_dict(slc_dir):

    # make keys with <date2>_<date2>
    keys = make_keys_from_slcdir(slc_dir)

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

def get_files(slc_dir, image="main", file_type=[".slc"]):
    """
    retrieve a list of files (.slc, .slc.par, .slc_tab, .slc.tops_par) from either the main or the secondary
    :param type:
    :param referece:
    :return:
    """
    files_dict = file_dict(slc_dir)

    for date_pair in files_dict:
        if image == "main" or image == "m":
            date_main = date_pair[0:8]
            key1 = date_pair
            key2 = date_main
            files = [file for file in files_dict[key1][key2] for ty in file_type if file.endswith(ty)]
            if "mosaic" in file_type:
                pass
            else:
                files = [x for x in files if "mosaic" not in x]
        elif image == "secondary" or image == "s":
            date_secondary = date_pair[9:17]
            key1 = date_pair
            key2 = date_secondary
            files = [file for file in files_dict[key1][key2] for ty in file_type if file.endswith(ty)]
            if "mosaic" in file_type:
                pass
            else:
                files = [x for x in files if "mosaic" not in x]

        else:
            print(TRED + "Choose between Main or Secondary images to retrieve files" + ENDC)
            exit()

    return files


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

if __name__ == "__main__":
    slc_dir = "../data/SLC"
    b = get_files(slc_dir, file_type=[".slc", ".par"], image="")
    print(b)
