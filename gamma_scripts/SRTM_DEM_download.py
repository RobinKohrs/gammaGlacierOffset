from pyroSAR.auxdata import dem_autoload
from spatialist import Vector

site = '../vector_geometry/big_glacier.gpkg'
out = '../data/DEM/srtm.vrt'

with Vector(site) as vec:
    vrt = dem_autoload(geometries=[vec],
                       demType='SRTM 1Sec HGT',
                       vrt=out,
                       buffer=0.1)
