#!/usr/bin/env python
# -*- coding: utf-8 -*-


#########################################################################
# Mosaicking and coregistring S-1 scenes
#########################################################################

import os
import re

# parse some arguments
parser = argparse.ArgumentParser(description="Decide whether you are executing this locally (-l) or on the server (-s) and which steps to perform")
# get positional arguments
parser.add_argument("-m", "--machine", dest="m",
                    help="(input) decide if working locally (l) or on the server (s)", default="l", type=str)

parser.add_argument("-s", "--step", dest="steps",
                    help="(input) which step to perform unzip (0), slc-import (1), dem_import (2)", default=0,
                    nargs="+", type=int)

parser.add_argument("-p", "--parallel", dest="parallel",
                    help="parallel(1) or sequential(1)", default=0, type=int)


# get the arguments
global args
args = parser.parse_args()
print(args)
if not args.m == "s":
    print("working locally...")
else:
    try:
        import py_gamma as pg
        print("working on the server...")
    except ImportError as err:
        print("Working on the server...")
        print("However the py_gamma-module can not be loaded...")
        print("Make sure its on $PATH? or PYTHONPATH?")
        exit(-1)