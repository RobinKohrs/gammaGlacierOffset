# Last update: 25 October 2018 cm
# - offset_pwrm: no oversampling (previously 2 times)
# - wrong width for second image before coregistration => mli_width_i

# download GRDs

ls *mli* srt*
S1A_IW_GRDH_1SDV_20160104T052528_20160104T052553_009340_00D80F_124D_vh_ml.mli      S1A_IW_GRDH_1SDV_20160503T052529_20160503T052554_011090_010B55_C010_vh_ml.mli
S1A_IW_GRDH_1SDV_20160104T052528_20160104T052553_009340_00D80F_124D_vh_ml.mli_par  S1A_IW_GRDH_1SDV_20160503T052529_20160503T052554_011090_010B55_C010_vh_ml.mli_par
S1A_IW_GRDH_1SDV_20160116T052528_20160116T052553_009515_00DD0D_67D8_vh_ml.mli      S1A_IW_GRDH_1SDV_20160714T052524_20160714T052549_012140_012CF8_8F0D_vh_ml.mli
S1A_IW_GRDH_1SDV_20160116T052528_20160116T052553_009515_00DD0D_67D8_vh_ml.mli_par  S1A_IW_GRDH_1SDV_20160714T052524_20160714T052549_012140_012CF8_8F0D_vh_ml.mli_par
S1A_IW_GRDH_1SDV_20160128T052527_20160128T052552_009690_00E237_E032_vh_ml.mli      S1A_IW_GRDH_1SDV_20160726T052525_20160726T052550_012315_0132A1_54F5_vh_ml.mli
S1A_IW_GRDH_1SDV_20160128T052527_20160128T052552_009690_00E237_E032_vh_ml.mli_par  S1A_IW_GRDH_1SDV_20160726T052525_20160726T052550_012315_0132A1_54F5_vh_ml.mli_par
S1A_IW_GRDH_1SDV_20160209T052527_20160209T052552_009865_00E736_BFA2_vh_ml.mli      S1A_IW_GRDH_1SDV_20160807T052526_20160807T052551_012490_013882_969B_vh_ml.mli
S1A_IW_GRDH_1SDV_20160209T052527_20160209T052552_009865_00E736_BFA2_vh_ml.mli_par  S1A_IW_GRDH_1SDV_20160807T052526_20160807T052551_012490_013882_969B_vh_ml.mli_par
S1A_IW_GRDH_1SDV_20160221T052527_20160221T052552_010040_00EC72_C493_vh_ml.mli      S1A_IW_GRDH_1SDV_20160819T052527_20160819T052552_012665_013E40_E96D_vh_ml.mli
S1A_IW_GRDH_1SDV_20160221T052527_20160221T052552_010040_00EC72_C493_vh_ml.mli_par  S1A_IW_GRDH_1SDV_20160819T052527_20160819T052552_012665_013E40_E96D_vh_ml.mli_par
S1A_IW_GRDH_1SDV_20160304T052527_20160304T052552_010215_00F15A_B5A2_vh_ml.mli      S1A_IW_GRDH_1SDV_20160831T052527_20160831T052552_012840_014434_9ADB_vh_ml.mli
S1A_IW_GRDH_1SDV_20160304T052527_20160304T052552_010215_00F15A_B5A2_vh_ml.mli_par  S1A_IW_GRDH_1SDV_20160831T052527_20160831T052552_012840_014434_9ADB_vh_ml.mli_par
S1A_IW_GRDH_1SDV_20160316T052527_20160316T052552_010390_00F654_14C5_vh_ml.mli      S1A_IW_GRDH_1SDV_20160912T052527_20160912T052552_013015_0149CC_F1E5_vh_ml.mli
S1A_IW_GRDH_1SDV_20160316T052527_20160316T052552_010390_00F654_14C5_vh_ml.mli_par  S1A_IW_GRDH_1SDV_20160912T052527_20160912T052552_013015_0149CC_F1E5_vh_ml.mli_par
S1A_IW_GRDH_1SDV_20160409T052528_20160409T052553_010740_01007E_1778_vh_ml.mli      srtm
S1A_IW_GRDH_1SDV_20160409T052528_20160409T052553_010740_01007E_1778_vh_ml.mli_par  srtm.par





ls -d S1*SAFE/ > dirlist

#########################################################################################
# Import images
pol=vv
for i in $(cat dirlist); do
    pwr=$(find . -iname "*tiff" | grep ${i} | grep $pol)
    ann=$(find . -iname "s1a-*xml" | grep ${i} | grep $pol)
    cal=$(find . -iname "calibration-s1a-*xml" | grep ${i} | grep $pol)
    noi=$(find . -iname "noise-s1a-*xml" | grep ${i} | grep $pol)
    par_S1_GRD $pwr $ann $cal $noi $(basename $i .SAFE)_${pol}.mli_par $(basename $i .SAFE)_${pol}.mli - - - -
done
pol=vh
for i in $(cat dirlist); do
    pwr=$(find . -iname "*tiff" | grep ${i} | grep $pol)
    ann=$(find . -iname "s1a-*xml" | grep ${i} | grep $pol)
    cal=$(find . -iname "calibration-s1a-*xml" | grep ${i} | grep $pol)
    noi=$(find . -iname "noise-s1a-*xml" | grep ${i} | grep $pol)
    par_S1_GRD $pwr $ann $cal $noi $(basename $i .SAFE)_${pol}.mli_par $(basename $i .SAFE)_${pol}.mli - - - -
done

#########################################################################################
# Multilook to reduce file size
#########################################################################################
for i in $(ls *mli); do
    multi_look_MLI $i ${i}_par $(basename $i .mli)_ml.mli $(basename $i .mli)_ml.mli_par 5 5
done

#########################################################################################
# Define reference image for co-registration
#########################################################################################
ref=S1A_IW_GRDH_1SDV_20160104T052528_20160104T052553_009340_00D80F_124D_vh_ml.mli

#########################################################################################
# Prepare DEM
#########################################################################################
dem=/home/oliver/g22_data/dem_1arcsec/global_1arcsec_dem.vrt
vrt2dem $dem ${ref}_par srtm srtm.par 2 -

#########################################################################################
# Create geocoding lookup table for reference image
#########################################################################################
gc_map ${ref}_par - srtm.par srtm gcdem.par gcdem geo2rdc 0.5 0.5 - - - inc - - ls_map - 2

#########################################################################################
# map dimensions
#########################################################################################
mli_width=`awk '$1 == "range_samples:" {print $2}' ${ref}_par`
mli_lines=`awk '$1 == "azimuth_lines:" {print $2}' ${ref}_par`
dem_width=`awk '$1 == "width:" {print $2}' gcdem.par`

#########################################################################################
# Estimate pixel scattering area based on DEM and ellipsoid
#########################################################################################
# pixel area normalisation
pixel_area ${ref}_par gcdem.par gcdem geo2rdc  ls_map inc pix_dem - - - pix

#########################################################################################
# Refinement of geocoding lookup table
#########################################################################################
create_diff_par ${ref}_par - diff_par 1 0
offset_pwrm pix_dem ${ref} diff_par offs snr 128 64 offsets 1 64 24 0.2
offset_fitm offs snr diff_par coffs coffsets 0.2 4

# Updating of the look-up table (rdc -> range doppler coordinate)
gc_map_fine geo2rdc $dem_width diff_par geo2rdc.fine 1
/bin/mv geo2rdc.fine geo2rdc

# Reproduce pixel area estimate
pixel_area ${ref}_par gcdem.par gcdem geo2rdc ls_map inc pix_dem - - - pix

#########################################################################################
# Co-registration of all MLIs to selected refernce image
#########################################################################################

# Resample dem to rdc geometry
geocode geo2rdc gcdem $dem_width gcdem.rdc $mli_width $mli_lines 0 0

for i in $(ls *ml.mli); do
    if [ ${i} !=  ${ref} ]; then
        # Pixel dimensions of image to be coregistered
        mli_width_t=`awk '$1 == "range_samples:" {print $2}' ${i}_par`
	      mli_lines_t=`awk '$1 == "azimuth_lines:" {print $2}' ${i}_par`

        rdc_trans ${ref}_par gcdem.rdc ${i}_par ${i}.lt
        geocode ${i}.lt ${ref} $mli_width ${i}.sim $mli_width_t $mli_lines_t 0 0

        create_diff_par ${i}_par - ${i}.diff_par 1 0
        offset_pwrm ${i}.sim ${i} ${i}.diff_par ${i}.offs ${i}.snr 128 128 ${i}.offsets 1 12 12 0.2
        offset_fitm ${i}.offs ${i}.snr ${i}.diff_par ${i}.coffs ${i}.coffsets 0.2 1
        gc_map_fine ${i}.lt $mli_width ${i}.diff_par ${i}.lt_fine 1

	MLI_interp_lt ${i} ${ref}_par ${i}_par ${i}.lt_fine ${ref}_par ${i}_par ${i}.diff_par $(basename ${i} mli)rmli $(basename ${i} mli)rmli_par
    fi
done

mli_width_i=`awk '$1 == "range_samples:" {print $2}' ${i}_par`

dis2pwr $ref $i $mli_width $mli_width_i				# Before coregistration
dis2pwr $ref $(basename ${i} mli)rmli $mli_width $mli_width     # After coregistration

#########################################################################################
# Compensate pwr images for pixel area variations
#########################################################################################
product ${ref} pix $(basename ${ref} mli)s0 $mli_width 1 1 0
for i in $(ls *rmli); do
    product ${i} pix $(basename ${i} rmli)s0 $mli_width 1 1 0
done

#########################################################################################
# Apply multi-temporal filter
#########################################################################################
for i in $(ls *s0); do
    echo "$i $(basename $i .s0)_mtfil.s0" >> optfile
done
temp_filt optfile $mli_width 5 5

dis2pwr 
S1A_IW_GRDH_1SDV_20160316T052527_20160316T052552_010390_00F654_14C5_vh_ml_mtfil.s0 S1A_IW_GRDH_1SDV_20160316T052527_20160316T052552_010390_00F654_14C5_vh_ml.s0 $mli_width $mli_width

#########################################################################################
# Calculate multitemporal metrics
#########################################################################################
ls *_mtfil.s0 > optfile_mt
temp_lin_var optfile_mt mtmean mtstdev $mli_width


#########################################################################################
# Geocode intensity images
#########################################################################################
for i in $(ls *mtfil.s0); do
    geocode_back ${i} $mli_width geo2rdc $(basename ${i} .s0)_geo.s0 $dem_width
done
geocode_back mtmean $mli_width geo2rdc mtmean_geo.s0 $dem_width
geocode_back mtstdev $mli_width geo2rdc mtstdev_geo.s0 $dem_width

#########################################################################################
#  Sigma to gamma conversion --> reduces incidence angle dependence of backscatter
#########################################################################################
# gamma0 = sigma0/cos(theta)
# sigma0: Starke Beeinflussung der Rückstreuung von Gelände
# funktioniert gut über Wälder

for i in $(ls S*geo.s0); do
    sigma2gamma ${i} inc $(basename ${i} s0)g0 $dem_width
done

#########################################################################################
# Convert images to GeoTiff
#########################################################################################
data2geotiff gcdem.par inc 2 inc.tif
data2geotiff gcdem.par ls_map 5 ls_map.tif
data2geotiff gcdem.par mtmean_geo.s0 2 mtmean_geo_s0.tif 0
data2geotiff gcdem.par mtstdev_geo.s0 2 mtstdev_geo_s0.tif 0
for i in $(ls S*g0); do
    data2geotiff gcdem.par $i 2 ${i}.tif 0
done
