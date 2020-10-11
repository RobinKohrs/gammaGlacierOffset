##############################################################
# Script to add pygamma locally to the PYTHONPATH-Systemvariable
##############################################################

# import libraries
import os
import sys
from glob import glob
import re
# no effect of importing pygamma as there is no gamma installed
#import py_gamma
#print(py_gamma.__file__)

# find all files in the current folder
files = os.listdir()

# print the current PYTHONPATH variable
try:
    print(os.environ["PYTHONPATH"])
except KeyError as err:
    print("The PYTHONPATH variable is empty at the moment" \
          "Adding pygamma to it")

# find the pygamma path
r = re.compile("^py_gamma.py$")
m = list(filter(r.match, files))[0]

# if length of the list is 0, there is no py_gamma in the current folder
if len(m) == 0:
    print("the 'py_gamma.py' file has to be in the directory from which you are executing \
          the current scipt")
    exit()
else:
    os.environ["PYTHONPATH"] = m
