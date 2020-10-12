# Import SLCs and DEM to GAMMA software within a given directory structure

try:
    import py_gamma as pg
except ImportError as err:
    print("The module `py_gamma` needs to be installed")
    #exit(-1)

import os
import datetime as date
from glob import glob
import zipfile
import shutil
import tqdm
from colors import red, green

# directories
dir_data = "../data"
dir_slc = os.path.join(dir_data, "SLC")
dir_dem = os.path.join(dir_data, "DEM")

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
        zf = zipfile.ZipFile(f)
        uncompressed_size = sum((file.file_size for file in zf.infolist()))
        extraced_size = 0
        print("======")
        print(green("Extracting: {}".format(f)))
        print("======")
        for file in zf.infolist():
            extraced_size += file.file_size
            print("{} %".format(extraced_size * 100/uncompressed_size))
            zf.extract(file, out_dir)
        exit()
        #
        # print(f)
        # shutil.unpack_archive(f, out_dir)
        # exit()

#########################################
# SLC_Import
#########################################


def slc_import():
    pass

#########################################
# DEM_Import
#########################################

def dem_import():
    pass


def main():
    unzip(dir_data, dir_data)
    # slc_import()
    # dem_import()

if __name__ == "__main__":
    main()
