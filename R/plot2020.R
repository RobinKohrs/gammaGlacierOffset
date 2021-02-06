# Title     : Extracts statistical measurements from displacement maps by pre-defined polygons
# Created by: Konstantin Schellenberg
# Created on: 17.11.2020

# data structure

# storage of gomez' data
# ./ data / disp_gomez / *.tif

# vector geometries
# ./ vector_geometry / glacier.gpkg

# load packages
packages = c("tidyverse", "raster", "sf", "exactextractr", "stringr", "data.table", "RColorBrewer")
lapply(packages, require, character.only = TRUE)

source("./R/functions.R")

# CREATE PATHS -----------------------------

plotdir = "./plots/glacier_movement"
if (!dir.exists(plotdir)) dir.create(recursive = TRUE)

# LOAD DATA -----------------------------
# glacier vectors
path_sf = "./vector_geometry/glacier.gpkg"
sf = st_read(path_sf, layer = "parts")
extent = st_read(path_sf, layer = "crop_extent")
extent_only_glacier = st_read(path_sf, layer = "crop_onlyglacier")

# dir 2020
dir_2020 = "tiffs_2020"
files_2020 = list.files(dir_2020, pattern = ".*\\.mag.geo_32627.tif$", full.names = TRUE)

# Import DEM for slope analyses
dir_dem = "./data/DEM/LMI_Haedarlikan_DEM_16bit_subset_32627.tif"
dem_big = raster(dir_dem)
crs(dem_big)

# check for crs
#all
#if (!as.character(crs(raster(files_disp[1]))) == as.character(crs(sf))) stop()

# RASTER PREPROCESSING -----------------------------

# creating dummy to refer on:
dummy = raster(crs = "+proj=utm +zone=27 +datum=WGS84 +units=m +no_defs",
               res = c(30, 30), ext = raster::extent(extent_only_glacier))

dem = dem_big %>% resample(dummy)
slope = raster::terrain(dem, opt = "slope", unit = "degrees")

# use the locally converted tiffs for 2020
disps_2020 = map(files_2020, function(x){
  raster(x) %>%
    resample(dummy)
})
disps_2020 = stack(disps_2020)


# EXTRACTION -----------------------------
# for now, exatraction of all gomez displacements, no matter what

tidying = function(exact_extract_output){
  # makes a tidy dataframe from exactextract output
  
  ex = exact_extract_output %>% mutate(subset = row_number()) %>%
    pivot_longer(-subset, names_to = "dates", values_to = "observation")
  
  # grep dates
  col = ex$dates %>% stringr::str_extract(pattern = "\\d+") %>%
    str_split(pattern = "\\.") %>%
    map(., ~ as.Date(.x, format = "%Y%m%d") %>% as.character()) %>%
    flatten_chr() %>%
    as.Date()
  
  tidy = ex %>% mutate(start = col) %>%
    dplyr::select(c(-dates)) %>%
    dplyr::select(c(start, subset, observation)) %>%
    arrange(start)
  
  return(tidy)
}

extraction_2020 = exact_extract(disps_2020, sf, "mean")

gamma2020 = tidying(extraction_2020) %>% mutate(observation = observation / 12)

gg2 = ggplot(gamma2020) +
  geom_point(aes(start, observation, group = subset), color = "grey15")+
  facet_wrap(~ subset) +
  geom_smooth(aes(start, observation), method = "lm", color = "darkgreen", fill = "grey60") +
  theme_minimal() +
  labs(title = "Glacier movement 2020 by geographical subset",
       subtitle = "Data processed by GAMMA offset tracking",
       y = "Velocity [m / day]", x = "Date") +
  theme(strip.text.x = element_text(size = 20),
        axis.text.x = element_text(angle = 65)) +
  ylim(c(-0.5, 2.5))
print(gg2)


ggplot(gamma2020) +
  geom_point(aes(x=start, y=observation, col=subset)) +
  geom_path(aes(x=start, y=observation, col=subset, group=subset)) +
  ylim(c(-0.5,10)) +
  theme_minimal() +
  theme(
    
  )

ggsave(file.path(plotdir, "Gamma_2020_movement.png"), plot = gg2, device = "png", scale = 0.5, height = 10, width = 15)
