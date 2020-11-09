# displaying rasters in gamma

import py_gamma as pg

hgt = "../data/DEM/20200911_vv_iw2.hgt.ras"
mli = "../data/tuples/20200911_20200923/20200911_vv_iw2.rmli"

pg.disras(hgt, mli, 2481)
