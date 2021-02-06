#!/usr/bin/env python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------
import subprocess
import sys
import os
import re
import argparse
#--------------------------------------------------------------------------------

# print the cmds or not
parser = argparse.ArgumentParser(description="")
parser.add_argument("-p", "--print", dest="print", help="only print cmd call", action="store_const", const=True)
args = parser.parse_args()


def get_ordered_files():
    # list all python files
    python_files = [x for x in os.listdir(".") if x.endswith(".py")]
    # sort them
    py_sorted = sorted(python_files, key= lambda x: x[0:2])
    # remove non matching ones
    r = re.compile(r"^\d\d.*")
    new_files = list(filter(r.match, py_sorted))
    new_files = [x for x in new_files if not "slc" in x]
    return new_files

def runem(files_list):

    # for each file
    for i, f in enumerate(files_list):
        if i == 0:
            cmd = f"python {f}"
            print(cmd)

        elif i == 1:
            cmd = f"python {f} -s 0 1 2"
            print(cmd)

        elif i == 2:
            cmd = f"python {f}"
            print(cmd)

        elif i == 3:
            cmd = f"python {f}"
            print(cmd)

        elif i == 4:
            cmd = f"python {f}"
            print(cmd)

        elif i == 5:
            cmd = f"python {f}"
            print(cmd)

        elif i == 6:
            cmd = f"python {f}"
            print(cmd)

        elif i == 7:
            exit()
            cmd = f"python {f}"
            print(cmd)

        elif i == 8:
            cmd = f"python {f} -s 1 2 3 4"
            print(cmd)

        elif i == 9:
            cmd = f"python {f}"
            print(cmd)

        else:
            print("not yet implemented")

        # run command
        if not args.print:
            out = subprocess.run(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)
        else:
            pass

        # in the first iteration make the file
        if i == 0:
            try:
                if out:
                    f_error = "error.txt"
                    f_out = "out.txt"

                    # write stderr to file
                    with open(f_error, "w") as src:
                        src.write(out.stderr.decode("UTF-8"))

                    with open(f_out, "w") as src:
                        src.write(out.stdout.decode("UTF-8"))
            except:
                pass

        # afterwards only append
        else:
            try:
                if out:
                    f_error = "error.txt"
                    f_out = "out.txt"

                    # append
                    with open(f_error, "a") as src:
                        src.write("*"*20 + "\n")
                        src.write(f + "\n")
                        src.write(out.stderr.decode("UTF-8"))

                    with open(f_out, "a") as src:
                        src.write("*"*20)
                        src.write(f)
                        src.write(out.stdout.decode("UTF-8"))
            except:
                pass


#--------------------------------------------------------------------------------
if __name__ == "__main__":
    f = get_ordered_files()
    runem(f)

#--------------------------------------------------------------------------------