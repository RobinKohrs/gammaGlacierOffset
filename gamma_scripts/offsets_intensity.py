
############################################
# Intensity offset tracking of glacier movements in Iceland
############################################

import os

# try importing gamma (only works when working on the server) --> So check if working on server
kernel = str(os.system("uname -r"))
print(kernel)
if kernel == "3.10.0-957.el7.x86_64":
    try:
        import py_gamma as pg
    except ImportError as err:
        print("The module `py_gamma` needs to be installed")
else:
    pass

# Global Variables
path_SLC = "../data/SLC/"
dates = [x for x in os.listdir("../data/SLC/Intensity")]
SLCs = [x for x in os.listdir("../data/SLC") if file.endswith(".slc")]
SLC_pars = [x for x in os.listdir("../data/SLC") if file.endswith(".slc.par")]

def mosaic_tops_bursts():
    create table

def main():
    print(dates)
    print(SLC_pars)
    print(SLCs)