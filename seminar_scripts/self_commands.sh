# GAMMA INTERFEROMETRIE
# init. 01.10.2020, Konstantin Schellenberg


## AUFGABE
# dem_import geoid korrigieren!z
# lt
# inter
# coh
# GRD multilook
# anderes DEM
# welche Aufl�sung, was muss ich im Vergleich zu DInSAR-Beispiel von gestern anders machen?
# Oversampling Optionen: gc_map

###############################################################################
# DOWNLOAD DEM

# mosaic files to vrt
gdalbuildvrt srtm.vrt *tif

# Import DEM (geoid Korrektur, nicht 0 �ber Ozean -> Ellipsoid, 0 �ber Ozean -> Geoid)
# MUSS F�R SRTM GEMACHT WERDEN, TDX Copernicus layer nicht.
dem_import srtm.vrt dem dem.par 0 1 $DIFF_HOME/scripts/egm2008-5.dem $DIFF_HOME/scripts/egm2008-5.dem_par

zip1=S1A_IW_SLC__1SDV_20170731T163002*.zip
zip2=S1A_IW_SLC__1SDV_20170812T163002*.zip

###############################################################################
# Import images

# besser: immer nur mit dem Date als Dateinamen arbeiten, sonst werden die Namen irgend-
# wann sehr lang.

date1=$(echo $zip1 | awk -F '_' '{print $6}' | awk -F 'T' '{print $1}')
date2=$(echo $zip2 | awk -F '_' '{print $6}' | awk -F 'T' '{print $1}')

pol=vv
unzip $zip1
unzip $zip2

dir1=S1A_IW_SLC__1SDV_20170731T163002_20170731T163029_017717_01DAC5_4796.SAFE
dir2=S1A_IW_SLC__1SDV_20170812T163002_20170812T163029_017892_01E015_2E07.SAFE

base1=$(basename ${dir1} .SAFE)
base2=$(basename ${dir2} .SAFE)


# Import SLCs
dirs="$dir1 $dir2"
lst='iw1 iw2 iw3'

# loop over IW bursts to import SLCs
for j in $dirs; do
    for i in $lst; do
        slc=$(find . -iname "*tiff" | grep ${j} | grep $pol | grep $i)
        ann=$(find . -iname "s1a-*xml" | grep ${j} | grep $pol | grep $i)
        cal=$(find . -iname "calibration-s1a-*xml" | grep ${j} | grep $pol | grep $i)
        noi=$(find . -iname "noise-s1a-*xml" | grep ${j} | grep $pol | grep $i)
        
        echo "processing: $j"
        par_S1_SLC $slc $ann $cal $noi $(basename ${j} .SAFE)_${pol}_${i}.slc.par $(basename ${j} .SAFE)_${pol}_${i}.slc $(basename ${j} .SAFE)_${pol}_${i}.slc.tops.par - - -
    done
done

###############################################################################
# create corners file, not needed

#for j in $base1; do
#    for i in $lst; do
#        ScanSAR_burst_corners ${j}_${pol}_${i}.slc.par ${j}_${pol}_${i}.slc.tops.par
#    done
#done
    
    
# create textfile with IW bursts and par-file
# SLC1
echo "${base1}_${pol}_iw1.slc ${base1}_${pol}_iw1.slc.par ${base1}_${pol}_iw1.slc.tops.par" > slc1_tab
echo "${base1}_${pol}_iw2.slc ${base1}_${pol}_iw2.slc.par ${base1}_${pol}_iw2.slc.tops.par" >> slc1_tab
echo "${base1}_${pol}_iw3.slc ${base1}_${pol}_iw3.slc.par ${base1}_${pol}_iw3.slc.tops.par" >> slc1_tab

# SLC2
echo "${base2}_${pol}_iw1.slc ${base2}_${pol}_iw1.slc.par ${base2}_${pol}_iw1.slc.tops.par" > slc2_tab
echo "${base2}_${pol}_iw2.slc ${base2}_${pol}_iw2.slc.par ${base2}_${pol}_iw2.slc.tops.par" >> slc2_tab
echo "${base2}_${pol}_iw3.slc ${base2}_${pol}_iw3.slc.par ${base2}_${pol}_iw3.slc.tops.par" >> slc2_tab

# hier definieren, wie gro� die Zielaufl�sung sein soll -> hier: 90m (f�r Waldanwendungen)

# Sentinel-1 Aufl�sungen:
# range: 4.2m
# azimuth: 14m

ml_rg=22
ml_az=7

# Only reference scene (1)
# mosaic bursts to complex SLC -> needed to transform DEM to RADAR geometry
SLC_mosaic_S1_TOPS slc1_tab ${base1}.slc  ${base1}.slc.par $ml_rg $ml_az

# create multilook to safe CPU power when geocoding the DEM on RADAR
multi_look ${base1}.slc  ${base1}.slc.par ${base1}.mli ${base1}.mli.par $ml_rg $ml_az

# Breite und H�he
mli1_width=$(cat ${base1}.mli.par | grep "range_samples:" | awk -F ':' '{ print $2 }')
mli1_lines=$(cat ${base1}.mli.par | grep "azimuth_lines:" | awk -F ':' '{ print $2 }')

mli2_width=$(cat ${base2}.mli.par | grep "range_samples:" | awk -F ':' '{ print $2 }')
mli2_lines=$(cat ${base2}.mli.par | grep "azimuth_lines:" | awk -F ':' '{ print $2 }')

# display multilook:
dispwr S1A_IW_SLC__1SDV_20170731T163002_20170731T163029_017717_01DAC5_4796.mli $mli1_width

# Calculate terrain-geocoding lookup table 
gc_map ${base1}.mli.par - dem.par dem EQA.dem.par EQA.dem ${base1}.lt 1.0 1.0 ${base1}.simsar - - ${base1}.inc - - ${base1}.ls_map 8 2 -

# size of DEM
dem_width=$(cat EQA.dem.par | grep "width:" | awk -F ':' '{ print $2 }')
dem_lines=$(cat EQA.dem.par | grep "nlines:" | awk -F ':' '{ print $2 }')

# Calculate terrain-based sigma0 and gammma0 normalization area in slant-range geometry 
pixel_area ${base1}.mli.par EQA.dem.par EQA.dem ${base1}.lt ${base1}.ls_map ${base1}.inc pix_sigma0 - - - pix


# Forward geocoding transformation using a lookup table -> .hgt file
geocode ${base1}.lt EQA.dem ${dem_width} ${base1}.hgt ${mli1_width} ${mli1_lines} 2 0

# preparation table for coregistration. 
echo "${base2}_iw1_rslc ${base2}_iw1_rslc.par ${base2}_iw1_rslc.tops_par" > slc3_tab
echo "${base2}_iw2_rslc ${base2}_iw2_rslc.par ${base2}_iw2_rslc.tops_par" >> slc3_tab
echo "${base2}_iw3_rslc ${base2}_iw3_rslc.par ${base2}_iw3_rslc.tops_par" >> slc3_tab

# TIME INTENSIVE COREGISTRATION! ~ 1h
S1_coreg_TOPS slc1_tab ${base1} slc2_tab ${base2} slc3_tab ${base1}.hgt ${ml_rg} ${ml_az} - - 0.8 0.01 0.8 1
# display DInSAR
disras ${base1}_${base2}.diff.bmp

# Multilook
multi_look ${base2}.rslc  ${base2}.rslc.par ${base2}.rmli ${base2}.rmli.par $ml_rg $ml_az
dis2pwr ${base1}.mli ${base2}.rmli ${mli1_width} ${mli2_width}

# check quality
more ${base1}_${base2}.coreg_quality

# get the baselin
base_orbit ${base1}.slc.par ${base2}.rslc.par ${base1}_${base2}.base

# Multiplies both mli scenes
product ${base1}.mli pix ${base1}.cmli $mli1_width 1 1 0
product ${base2}.rmli pix ${base2}.crmli $mli1_width 1 1 0

dis2pwr ${base1}.mli ${base1}.cmli ${mli1_width} ${mli1_width}
dis2pwr ${base2}.rmli ${base2}.crmli ${mli2_width} ${mli2_width}

# Coherence
cc_ad ${base1}_${base2}.diff ${base1}.cmli - - - ${base1}_${base2}.cc_ad ${mli1_width} 5 5 1
dis_linear ${base1}_${base2}.cc_ad ${mli1_width}

# Adaptive interferogram filtering
adf ${base1}_${base2}.diff ${base1}_${base2}.diff_sm ${base1}_${base2}.diff_smcc $mli1_width 0.5 64 7 8 0 0 0.25
dis2mph ${base1}_${base2}.diff ${base1}_${base2}.diff_sm $mli1_width $mli1_width

# Phase unwrapping for diff using Minimum Cost Flow (MCF) on a triangular mesh
mcf ${base1}_${base2}.diff_sm ${base1}_${base2}.cc_ad - ${base1}_${base2}.diff_sm.unw $mli1_width 0 0 0 - - 1 1 512 180 100 1

# display tools
# unwrapped phases:
disrmg ${base1}_${base2}.diff_sm.unw ${base1}.mli ${mli1_width} 1 1 0 0.66667

# Conversion of unwrapped differential phase to displacement
dispmap ${base1}_${base2}.diff_sm.unw ${base1}.hgt ${base1}.slc.par ${base1}_${base2}.off ${base1}_${base2}.disp 0
disdt_pwr24 ${base1}_${base2}.disp ${base1}.mli ${mli1_width} - - - 0.05


# geocoding from RADAR to DEM-geometry
geocode_back ${base1}_${base2}.cc_ad ${mli1_width} ${base1}.lt ${base1}_${base2}.geo.cc_ad ${dem_width}
geocode_back ${base1}.cmli ${mli1_width} ${base1}.lt ${base1}.geo.pwr ${dem_width}
geocode_back ${base2}.crmli ${mli1_width} ${base1}.lt ${base2}.geo.pwr ${dem_width}
geocode_back ${base1}_${base2}.disp ${mli1_width} ${base1}.lt ${base1}_${base2}.geo.disp ${dem_width}
# layover/shadow map
geocode_back ${base1}.ls_map ${mli1_width} ${base1}.lt ${base1}.geo.ls_map ${dem_width}
# incidence angle
geocode_back ${base1}.inc ${mli1_width} ${base1}.lt ${base1}.geo.inc ${dem_width}

# EXPORTING as geotiff
data2geotiff EQA.dem.par ${base1}_${base2}.geo.cc_ad 2 ${base1}_${base2}_geo_cc_ad.tif #coherence
data2geotiff EQA.dem.par ${base1}.geo.pwr 2 ${base1}_geo_s0.tif 0 #mli1
data2geotiff EQA.dem.par ${base2}.geo.pwr 2 ${base2}_geo_s0.tif 0 #mli2
data2geotiff EQA.dem.par ${base1}.inc 2 ${base1}_inc.tif 0 #geocoding? pixelsize?
data2geotiff EQA.dem.par ${base1}_${base2}.geo.disp 2 ${base1}_${base2}.geo.disp.tif 0 #displacement
data2geotiff EQA.dem.par ${base1}.geo.inc 2 ${base1}.geo.inc.tif 0

# reproject with gdal_translate

### Was man typischerweise exportiert:
# Backscatter
# displacment
# local incidence 
# shadow
