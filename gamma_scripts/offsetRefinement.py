##########################################################################
# Window Size Refinement loops
##########################################################################

import os
import re
import sys

print()
if sys.platform == "win32":
    pass
else:
    kernel = str(os.system("uname -r"))
    print(kernel)

    if kernel == "3.10.0-957.el7.x86_64":
        try:
            import py_gamma as pg
        except ImportError as err:
            print("The module `py_gamma` needs to be installed")
    else:
        pass

date1 = "20160112"
date2 = "20160124"

slc1 = "../data/test/20160112.db.slc"
slc1_par = "../data/test/20160112.db.slc.par"
slc2 = "../data/test/20160124.db.slc"
slc2_par = "../data/test/20160124.db.slc.par"

off = "../data/test/" + date1 + "_" + date2 + ".off"

tracking_algorithm = 1

def create_offsets(slc1, slc2, off):

    pg.create_offsets(slc1, slc2, off, tracking_algorithm)

def looping():
    pass

def main():
    # create_offsets(slc1_par, slc2_par, off)
    print(off)

if __name__ == '__main__':
    main()
