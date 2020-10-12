# Import SLCs and DEM to GAMMA software within a given directory structure


try:
    import py_gamma as pg
except ImportError as err:
    print("The module `py_gamma` needs to be installed")

import os
import datetime as date
import glob
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

def unzip(file, out_dir):
    pass

#########################################
# SLC_Import
#########################################


def S1_file_finder(out):
    zip = glob.glob(dir_slc, "*.zip")
    return [zip]

def slc_import():
    pass

#########################################
# DEM_Import
#########################################

def dem_import():
    print(dir_dem)
    pass


def main():
    unzip()
    slc_import()
    dem_import()

if __name__ == "__main__":
    main()
