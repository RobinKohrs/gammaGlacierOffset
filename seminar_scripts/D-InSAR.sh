# Last update: 24 October 2018 cm
# - ras -> bmp


date1=20160202
date2=20160214

ScanSAR_burst_corners ${date1}_iw1_slc.par ${date1}_iw1_slc.tops_par


echo "${date1}_iw1_slc ${date1}_iw1_slc.par ${date1}_iw1_slc.tops_par" > slc1_tab
echo "${date1}_iw2_slc ${date1}_iw2_slc.par ${date1}_iw2_slc.tops_par" >> slc1_tab

echo "${date2}_iw1_slc ${date2}_iw1_slc.par ${date2}_iw1_slc.tops_par" > slc2_tab
echo "${date2}_iw2_slc ${date2}_iw2_slc.par ${date2}_iw2_slc.tops_par" >> slc2_tab

ml_rg=18
ml_az=4

# mosaic bursts to complex SLC
SLC_mosaic_S1_TOPS slc1_tab ${date1}.slc  ${date1}.slc.par $ml_rg $ml_az

multi_look ${date1}.slc  ${date1}.slc.par ${date1}.mli ${date1}.mli.par $ml_rg $ml_az

# define vars for width and lines for convenience
# awk: zerlegt string in zwei Teile
# | : piping

mli1_width=$(cat ${date1}.mli.par | grep "range_samples:" | awk -F ':' '{ print $2 }')
mli1_lines=$(cat ${date1}.mli.par | grep "azimuth_lines:" | awk -F ':' '{ print $2 }')


dispwr 20160202.mli $mli1_width # to look at multilooked pwr image

gc_map ${date1}.mli.par - srtm.dem_par srtm EQA.dem_par EQA.dem ${date1}.lt 0.5 0.5 - - - ${date1}.inc - - ${date1}.ls_map 8 2

dem_width=$(cat EQA.dem_par | grep "width:" | awk -F ':' '{ print $2 }')
dem_lines=$(cat EQA.dem_par | grep "nlines:" | awk -F ':' '{ print $2 }')

pixel_area ${date1}.mli.par EQA.dem_par EQA.dem ${date1}.lt ${date1}.ls_map ${date1}.inc pix_sigma0 - - - pix

geocode ${date1}.lt EQA.dem ${dem_width} ${date1}.hgt ${mli1_width} ${mli1_lines} 2 0

echo "${date2}_iw1_rslc ${date2}_iw1_rslc.par ${date2}_iw1_rslc.tops_par" > slc3_tab
echo "${date2}_iw2_rslc ${date2}_iw2_rslc.par ${date2}_iw2_rslc.tops_par" >> slc3_tab

S1_coreg_TOPS slc1_tab ${date1} slc2_tab ${date2} slc3_tab ${date1}.hgt ${ml_rg} ${ml_az} - - 0.8 0.01 0.8 1

disras 20160202_20160214.diff.bmp

multi_look ${date2}.rslc  ${date2}.rslc.par ${date2}.rmli ${date2}.rmli.par $ml_rg $ml_az

dis2pwr 20160202.mli 20160214.rmli ${mli1_width} ${mli1_width}

more 20160202_20160214.coreg_quality

base_orbit ${date1}.slc.par ${date2}.rslc.par ${date1}_${date2}.base

product ${date1}.mli pix ${date1}.cmli $mli1_width 1 1 0
product ${date2}.rmli pix ${date2}.crmli $mli1_width 1 1 0

dis2pwr 20160202.mli 20160202.cmli ${mli1_width} ${mli1_width}

cc_ad ${date1}_${date2}.diff ${date1}.cmli - - - ${date1}_${date2}.cc_ad ${mli1_width} 3 7 1

dis_linear ${date1}_${date2}.cc_ad ${mli1_width}

adf ${date1}_${date2}.diff ${date1}_${date2}.diff_sm ${date1}_${date2}.diff_smcc $mli1_width 0.5 64 7 8 0 0 0.25

dis2mph ${date1}_${date2}.diff ${date1}_${date2}.diff_sm $mli1_width $mli1_width
mcf ${date1}_${date2}.diff_sm ${date1}_${date2}.cc_ad - ${date1}_${date2}.diff_sm.unw $mli1_width 0 0 0 - - 1 1 512 180 2046 1

disrmg ${date1}_${date2}.diff_sm.unw ${date1}.mli ${mli1_width} 1 1 0 0.66667

dispmap ${date1}_${date2}.diff_sm.unw ${date1}.hgt ${date1}.slc.par ${date1}_${date2}.off ${date1}_${date2}.disp 0

disdt_pwr24 ${date1}_${date2}.disp ${date1}.mli ${mli1_width} - - - 0.05

geocode_back ${date1}_${date2}.cc_ad ${mli1_width} ${date1}.lt ${date1}_${date2}.geo.cc_ad ${dem_width}

geocode_back ${date1}.cmli ${mli1_width} ${date1}.lt ${date1}.geo.pwr ${dem_width}

geocode_back ${date2}.crmli ${mli1_width} ${date1}.lt ${date2}.geo.pwr ${dem_width}

geocode_back ${date1}_${date2}.disp ${mli1_width} ${date1}.lt ${date1}_${date2}.geo.disp ${dem_width}

data2geotiff EQA.dem_par ${date1}_${date2}.geo.cc_ad 2 ${date1}_${date2}_geo_cc_ad.tif

data2geotiff EQA.dem_par ${date1}.geo.pwr 2 ${date1}_geo_s0.tif 0

data2geotiff EQA.dem_par ${date2}.geo.pwr 2 ${date2}_geo_s0.tif 0

data2geotiff EQA.dem_par ${date1}.inc 2 ${date1}_inc.tif 0

data2geotiff EQA.dem_par ${date1}_${date2}.geo.disp 2 ${date1}_${date2}.geo.disp.tif 0
