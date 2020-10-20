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
            m = re.search(r'.*1SDV_(\d{8}).*', f).group(1)
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
    print("Searching in the diretory: {}".format(sys.argv[1]))
    print("With regex: {}".format(sys.argv[2]))
    print()
    res = rec_reg(sys.argv[1], sys.argv[2])
    print(res)

if __name__ == "__main__":
    slc_dir = "../data/SLC"
    b = file_dict(slc_dir)
