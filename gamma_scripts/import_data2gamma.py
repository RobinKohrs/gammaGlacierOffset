# Import SLCs and DEM to GAMMA software within a given directory structure

try:
    import py_gamma as pg
except ImportError as err:
    print("The module `py_gamma` needs to be installed")
    exit(-1)

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

def dem_import(dir_dem, dem_name):
    """
    Importing national icelandic DEM to GAMMA
    :param dir_dem: Directory containing the unzipped DEM which overlaps with the SLC at least in the areas of interest
    :param dem_name: Full name of the DEM
    :return: None, printing GAMMA output to console
    """

    dem = os.path.join(dir_dem, dem_name)
    out = os.path.join(dir_dem, "DEM")
    out_par = os.path.join(dir_dem, "DEM.par")

    print(out)
    pg.dem_import(dem, out, out_par)

    # TODO: print size of the DEM from par-file
    with open(out_par) as f:
        lines = f.readlines()
        print(lines)
        f.close()

    # dem_width =
    # dem_lines =


def main():
    unzip(dir_data, dir_data)
    # slc_import()
    dem_import(dir_dem, "LMI_Haedarlikan_DEM_16bit_subset.tif")

if __name__ == "__main__":
    main()
