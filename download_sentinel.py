#!/usr/bin/env python

##################################################
# Module for downloading Seninel 1 Scenes of given date over given region
##################################################

########
# Imports
#########

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

##################################################
##################################################





def get_arguments():
    # parse some arguments
    parser = argparse.ArgumentParser(description="Get the necessary information for the \n"
                                                 "Sentinelsat Download")
    # get positional arguments
    parser.add_argument("username", help="(input) Username from the Copernicushub", type=str)
    parser.add_argument("password", help="(input) Username from the Copernicushub", type=str)
    parser.add_argument("roi", help="(input) Path to the geojson region of interest", type=str)
    parser.add_argument("-t", "--type", dest="type", default='SLC', help="(input) Decide which type of product to download", type=str)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--date", dest='d', help="Option to check if Download is available for single date" 
                                            "in the format yyyymmdd e.g. 20201231", type=str)
    group.add_argument("-ds", "--date_region",dest='ds', nargs='+', help="Downlowad all the available Scenes between the date", \
                        type=str)

    parser.add_argument("-p", "--path", dest="out_path", help="path where files will be saved", type=str)

    # get the arguments
    args = parser.parse_args()
    return args

def create_api(user, passwd):
    api = SentinelAPI(user, passwd, 'https://scihub.copernicus.eu/dhus')
    return api


def check_dates(date):
    y = date[0:4]
    m = date[4:6]
    d = date[6:8]
    # check for validity of year
    if len(y) != 4:
        print("The year must be a 4-digit number")
        exit()
    if int(y) > 2020 or int(y) < 2014:
        print("Sentinel wasn't up there at that time")

    # check for validity of month
    if len(m) != 2:
        print("The month must be a 2-digit number")
        exit()
    if int(m) > 12 or int(m) < 1:
        print("The year only has 12 months")
        exit()

    # check for validity of day
    if len(d) != 2:
        print("The day must be a 2-digit number")
        exit()
    if int(d) > 31 or int(d) < 1:
        print("This is probably no day in a month")

    return "{0}{1}{2}".format(str(y), str(m), str(d))

def parse_dates(args):
    print(args.d)
    if args.d:
        date = check_dates(args.d)
        return date

    elif args.ds:
        dates = []
        for d in args.ds:
            date = check_dates(d)
            dates.append(date)
        return dates

    else:
        print("Something went terribly wrong")
        exit()

def download_products(args, api, footprint, dates):

    # check if output-path specified
    if args.out_path:
        out_path = args.out_path
    else:
        dir = "./data"
        if not os.path.exists(dir):
            os.makedirs(dir)
        out_path = dir


    if args.d:
        products = api.query(footprint,
                         date=(dates),
                         platformname='Sentinel-1',
                         producttype=args.type,
                         path=args.out_path)

    if args.ds:
        # run query for each single date TODO: Option for parallel?!
        for d in dates:
            products = api.query(footprint,
                                 date=(d),
                                 platformname='Sentinel-1',
                                 producttype=args.type,
                                 path=args.out_path)

def debug_args(args):
    print(args)
    sys.exit(0)

def main():
    # get the arguments
    args = get_arguments()

    #debug_args(args)

    # create the api (whatever this means)
    api = create_api(args.username, args.password)

    # path to the geojson (Straight from the documentary)
    footprint = geojson_to_wkt(read_geojson(args.roi))

    # parse the dates
    dates = parse_dates(args)
    print(dates)

    # download products
    download_products(args, api=api, footprint=footprint, dates = dates)



if __name__ == "__main__":
    main()



