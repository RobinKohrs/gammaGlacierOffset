# Import SLCs and DEM to GAMMA software within a given directory structure

try:
    import py_gamma as pg
except ImportError as err:
    print("The module `py_gamma` needs to be installed")
    #exit(-1)

import os
import datetime as date
from glob import glob
import zipfile as ZipFile

# directories
dir_data = "../data"
dir_slc = os.path.join(dir_data + "SLC")
dir_dem = os.path.join(dir_data + "DEM")

# arg-parsing arguments
def get_arguments():
    pass

#########################################
# Unzip
#########################################

def S1_file_finder(dir_data):
    """
    :param : s1dir
    :return:
    """
    safe_zips = glob(os.path.join(dir_data, "*.zip"))
    print(safe_zips)
    return safe_zips

def unzip(dir_data, out_dir):
    safe_zips = S1_file_finder(dir_data)
    for f in safe_zips:
        with ZipFile(f, "r") as zobj:
            print(zobj)
            #zobj.extractall(out_dir)

#########################################
# SLC_Import
#########################################


def slc_import():
    pass

#########################################
# DEM_Import
#########################################

def dem_import():
    print(dir_dem)
    pass


def main():
    unzip(dir_data, "./")
    # slc_import()
    # dem_import()

if __name__ == "__main__":
    main()
