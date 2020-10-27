# Glacier Offset Tracking with the GAMMA software

- This collection of python scripts walks you through the processing of pairwise offsets for Sentinel-1 data.
- Data needs to be downloaded manually (from e.g ASF). Afterwards, however, the processing can be done using our scripts in the
order they are numerated
- Some caution needs to be paid in the setup of the relative paths as most of them are still hardcoded (but all relative to the
main script-directory)

```
.
|–– gammascripts/
|  |–– 00_...
|  |–– 01_...
|–– data/
|  |–– S1A_IW_SLC__1SDV_20160827T185015_20160827T185042_012790_014279_03C2.SAFE
|  |–– S1A_IW_SLC__1SDV_20160908T185016_20160908T185043_012965_01482C_1553.SAFE
|  |–– S1A_IW_SLC__1SDV_20170106T185013_20170106T185040_014715_017F24_1553.SAFE
|  |–– S1A_IW_SLC__1SDV_20170118T185013_20170118T185040_014890_018496_4F8C.SAFE
|  |–– S1A_IW_SLC__1SDV_20170915T185022_20170915T185049_018390_01EF4F_CCEA.SAFE
|  |–– S1A_IW_SLC__1SDV_20170927T185022_20170927T185049_018565_01F4AA_52FB.SAFE
|  |–– S1A_IW_SLC__1SDV_20180113T185020_20180113T185047_020140_022590_1535.SAFE
|  |–– .
|  |–– .
|  |–– .
|  |–– DEM/
|  |–– SLC/
|  |–– tuples/
|  |  |–– 20160112_20160124
|  |  |  |–– intensity
|  |  |  |–– phase

``` 

![interferogram](plots/26102020/Screenshot from 2020-10-26 16-44-41.png)

Authors: Robin Kohrs, Konstantin Schellenberg


