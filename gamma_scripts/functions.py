#!/usr/bin/env python

# Python module with some functions that may be useful for many opperations in this module

import re
import os

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