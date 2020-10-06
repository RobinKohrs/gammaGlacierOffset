# connect to the API
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
import sys

passwd = sys.argv[1]
print(passwd)

api = SentinelAPI('roko93', 'sys.argv[1]', 'https://scihub.copernicus.eu/dhus')
print(api)

# search by polygon, time, and SciHub query keywords
footprint = geojson_to_wkt(read_geojson('./vector_geometry/sample_glacier_wgs84.geojson'))

products = api.query(footprint,
                   date=('20151219', date(2015, 12, 19)),
                   platformname='Sentinel-1',
                   producttype='SLC',
                   path="~/Desktop")
