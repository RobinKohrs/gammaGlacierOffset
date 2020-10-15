#!/usr/bin/env python

import os
import re
import sys

def rec_reg(path, regex):
    """
    find files recursively
    """
    regObj = re.compile(regex)
    res = []
    for root, dirs, fnames in os.walk(path):
        for fname in fnames:
            if regObj.match(fname):
                res.append(os.path.join(root, fname))
    return res


if __name__ == "__main__":
    print("Searching in the diretory: {}".format(sys.argv[1]))
    print("With regex: {}".format(sys.argv[2]))
    print()
    res = rec_reg(sys.argv[1], sys.argv[2])
    print(res)