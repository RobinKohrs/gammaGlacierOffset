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

# displacement data gomez et al.
dir_gom = "./data/disp_gomez"
files_gom = list.files(dir_gom, pattern = ".tif$", full.names = TRUE)

# out displacement data with GAMMA software
dir_disp = "./results/pwr_thresh0.01"
files_disp = list.files(dir_disp, pattern = "\\.mag.geo_32627.tif$", full.names = TRUE)

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

par(mfrow = (c(1, 2)))
plot(slope)
plot(dem)
plot(sf, add = TRUE)

# crop all disp to extent
disps = map(files_disp, function(x){
  raster(x) %>%
    resample(dummy)
})

# use the locally converted tiffs for 2020
disps_2020 = map(files_2020, function(x){
  raster(x) %>%
    resample(dummy)
})

#goms = map(files_gom, function (x){
#    raster(x) %>%
#        resample(dummy)
#})
#
## stacking
#gom = stack(goms)

disp = stack(disps)
disps_2020 = stack(disps_2020)


# NAMING -----------------------------
#' test stringr if they match...

# assign dates to raster bands
pairs = names(gom) %>%
  stringr::str_extract(pattern = "\\d+.\\d+") %>%
  str_split(pattern = "\\.") %>%
  map(., ~ as.Date(.x, format = "%Y%m%d"))

names(pairs) = map(pairs, ~ .x[1] %>% as.character())

# calculating date difference
diffs = map_dbl(pairs, ~ diff(as.Date(.x, format = "")))

# some have longer baselines than 12 day, the latter is the usual though
pairs_diff = as.data.frame(pairs) %>%
  t() %>%
  as.data.frame(row.names = FALSE) %>%
  mutate(diffs)
colnames(pairs_diff) = c("start", "end", "diffs")

pairs_df = as.data.frame(pairs) %>%
  t() %>%
  as.data.frame(row.names = FALSE)
colnames(pairs_df) = c("start", "end")

# filter the same dates as the gomez displacements.

#' HERE

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

extraction_gomez = exact_extract(gom, sf, "mean")
extraction_disp = exact_extract(disp, sf, "mean")
extraction_2020 = exact_extract(disps_2020, sf, "mean")

gomez = tidying(extraction_gomez)
gamma = tidying(extraction_disp) %>% mutate(observation = observation / 12) # per day
gamma2020 = tidying(extraction_2020) %>% mutate(observation = observation / 12)

# SLOPE ANALYSIS -----------------------------
#' Baustelle

sp.dt = as.data.table.raster(slope, xy=TRUE)



# VISUALISATION to be outsourced! -----------------------------

ggplot() +
  geom_sf(aes(fill = ID), sf)

colr <- colorRampPalette(brewer.pal(9, 'Blues'))
# quick viz
rasterVis::levelplot(disp,
                     margin=FALSE,
                     colorkey=list(
                       space='bottom',
                       labels=list(at=0:20, font=4),
                       axis.line=list(col='black'),
                       width=0.75
                     ),
                     par.settings=list(
                       strip.border=list(col='transparent'),
                       strip.background=list(col='transparent'),
                       axis.line=list(col='transparent')
                     ),
                     scales=list(draw=FALSE),
                     col.regions=colr,
                     at=seq(0, 20, len=101),
                     names.attr=rep('', nlayers(disp)))


gg1 = ggplot(gomez) +
  geom_point(aes(start, observation, group = subset), color = "grey15")+
  facet_wrap(~ subset) +
  geom_smooth(aes(start, observation), method = "lm", color = "darkgreen", fill = "grey60") +
  theme_minimal() +
  labs(title = "Glacier movement by geographical subset",
       subtitle = "Data from Gómez et al. (2020)",
       y = "Velocity [m / day]", x = "Date") +
  theme(strip.text.x = element_text(size = 20),
        axis.text.x = element_text(angle = 65)) +
  ylim(c(-0.5, 2.5))
print(gg1)

gg2 = ggplot(gamma) +
  geom_point(aes(start, observation, group = subset), color = "grey15")+
  facet_wrap(~ subset) +
  geom_smooth(aes(start, observation), method = "lm", color = "darkgreen", fill = "grey60") +
  theme_minimal() +
  labs(title = "Glacier movement by geographical subset",
       subtitle = "Data processed by GAMMA offset tracking",
       y = "Velocity [m / day]", x = "Date") +
  theme(strip.text.x = element_text(size = 20),
        axis.text.x = element_text(angle = 65)) +
  ylim(c(-0.5, 2.5))
print(gg2)


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


ggsave(file.path(plotdir, "Gomez_glacier_movement.png"), plot = gg1, device = "png", scale = 0.5, height = 10, width = 15)
ggsave(file.path(plotdir, "Gamma_glacier_movement.png"), plot = gg2, device = "png", scale = 0.5, height = 10, width = 15)
