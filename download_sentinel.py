#!/usr/bin/env python

##################################################
# Module for downloading Seninel 1 Scenes of given date over given region
##################################################

# trying to import sentinelsat
try:
    from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
except ImportError as err:
    print("sentinelsat module not found")
    exit(-1)

from datetime import date
import os
import sys
import argparse

def get_arguments():
    # parse some arguments
    parser = argparse.ArgumentParser(description="Get the necessary information for the \n"
                                                 "Sentinelsat Download")
    # get positional arguments
    parser.add_argument("username", help="(input) Username from the Copernicushub", type=str)
    parser.add_argument("password", help="(input) Username from the Copernicushub", type=str)
    parser.add_argument("roi", help="(input) Path to the geojson region of interest", type=str)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--date", help="Option to check if Download is available for single date", type=str)
    group.add_argument("-ds", "--date_region", help="Downlowad all the available Scenes between the date", \
                        type=str)



    # get the arguments
    args = parser.parse_args()
    return args

def download_scenes(user, passwd, roi, dates):
    pass


def main():
    args = get_arguments()

if __name__ == "__main__":
    main()



