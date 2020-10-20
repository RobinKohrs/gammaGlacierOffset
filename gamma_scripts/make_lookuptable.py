#!/usr/bin/env python

######################
#
# Module for creating a lookuptable for each interferometric pair
#
######################
#

import os
from functions import *
import argparse

# parse some arguments
parser = argparse.ArgumentParser(description="")
parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)
args =parser.parse_args()





def create_lookup(slc_dir, image="main"):
    # get the necessary files
    master_slcs_pars = get_files(slc_dir, image=image, file_type=[".mli.par", ".mli.par"])
    print(master_slcs_pars)



def main():
    create_lookup(slc_dir, image="main")


if __name__ == "__main__":
    slc_dir = "../data/SLC"
    main()
