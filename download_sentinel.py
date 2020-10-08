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
from colors import  red
import pandas as pd

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
    group.add_argument("-id", "--uuid", dest='id', nargs='+',
                       help="Downlowad all the available Scenes by their uuid", \
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

# footprint and dates are optional arguments that are only needed when the function is called to print
# an overview with the dates
def download_products(args, api, footprint=None, dates=None):

    # check if output-path specified
    if args.out_path:
        out_path = args.out_path
    else:
        dir = "./data"
        if not os.path.exists(dir):
            os.makedirs(dir)
        out_path = dir


    if args.d:

        # get the year the month and the day as ints with no leading 0
        y,m,d = int(dates[0:4]), int(dates[4:6]), int(dates[6:8])

        products = api.query(footprint,
                         date=(dates, date(y,m,d)),
                         platformname='Sentinel-1',
                         producttype=args.type,
                         path=args.out_path)

    if args.ds:
        # run query for each single date TODO: Option for parallel?!
        for d in dates:
            y, m, d = int(d[0:4]), int(d[4:6]), int(d[6:8])
            products = api.query(footprint,
                                 date=(d, (y,m,d)),
                                 platformname='Sentinel-1',
                                 producttype=args.type,
                                 path=args.out_path)

    # the first two functions (for one date, and the one for multiple dates are acutally just to get an overview)
    if not args.id:
        products_df = api.to_dataframe(products)
        print(products_df.head())


    # if we have the uuid we can download them directly
    if args.id:
        for i,id in enumerate(args.id):

            print(red("=================================="))
            print(red("downloading scene: {}".format(id)))
            print(red("=================================="))

            if i == 0:
                while True:
                    # prompt if he wishes to continues
                    cont = input("Do you want to continue? [y/n]")
                    if cont == "y":
                        api.download(id)
                        break
                    if cont == "n":
                        exit()
                    else:
                        print(red("Didn't get that. Either y or n"))



            # download all the rest
            api.download(id)




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

    # parse the dates (only when not downloading via the uuid)
    if not args.id:
        dates = parse_dates(args)


    # download products (acutally just an overview, when provifing a date or multiple dates)
    if not args.id:
        download_products(args, api=api, footprint=footprint, dates = dates)
    else:
        download_products(args, api=api)



if __name__ == "__main__":
    main()



