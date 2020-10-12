# Import SLCs and DEM to GAMMA software within a given directory structure


try:
    import py_gamma as pg
except ImportError as err:
    pass
    print("The module `py_gamma` needs to be installed")
    exit(-1)

import os
import datetime as date
import glob
import zipfile as ZipFile

# directories
dir_data = "../data/"
# dir_slc = dir_data + "SLC/"


# arc-parsing arguments
def get_arguments():
    pass


###############
# file finder #

def S1_file_finder(out):
    zip = glob.glob(dir_slc, "*.zip")
    return [zip]


##############
# unzip  #####

def unzip(file, out_dir):
    pass


##############
# unzip  #####

def main():
    zips = glob.glob(dir_slc + "*.zip")
    print(zips)
    ZipFile.extractall(members=zips)

if __name__ == "__main__":
    main()
