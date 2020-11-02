#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################
# Window Size Refinement loops
#########################################

import os
import re
import argparse
import sys
import numpy as np
import itertools
from functions import *

# parse some arguments
parser = argparse.ArgumentParser(description="Glacier Offset Tracking in 5 steps")
# get positional arguments
parser.add_argument("-s", "--step", metavar="", dest="steps", help="(1)... (2)...", default=1,type=int)
parser.add_argument("-p", "--print", metavar="", dest="print", help="only print cmd call", action="store_const", const=True)

args = parser.parse_args()


def main():


if __name__ == "__main__":
    main()

