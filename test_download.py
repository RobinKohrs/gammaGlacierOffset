# connect to the API
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
import sys
import pandas as pd

passwd = sys.argv[1]
print(passwd)

api = SentinelAPI('roko93', sys.argv[1], 'https://scihub.copernicus.eu/dhus')
print(api)

# search by polygon, time, and SciHub query keywords
footprint = geojson_to_wkt(read_geojson('./vector_geometry/big_glacier.geojson'))
print(footprint)

products = api.query(footprint,
                   date=('20200812', date(2020, 9, 12)),
                   platformname='Sentinel-1',
                   producttype='SLC')

df = api.to_dataframe(products)
print(df.head())
