# Title     : Extracts statistical measurements from displacement maps by pre-defined polygons
# Created by: Konstantin Schellenberg
# Created on: 17.11.2020

# data structure

# storage of gomez' data
# ./ data / disp_gomez / *.tif

# vector geometries
# ./ vector_geometry / glacier.gpkg



# load packages
packages = c("tidyverse", "gridExtra", "grid", "raster", "sf", "exactextractr", "stringr", "data.table", "RColorBrewer", "ggplot2")
lapply(packages, require, character.only = TRUE)

library(ggthemes)

theme_set(theme_minimal())

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

# our displacement data with GAMMA software
dir_disp = "./results/pwr_thresh0.01"
files_disp = list.files(dir_disp, pattern = "\\.mag.geo_32627.tif$", full.names = TRUE)

# Import DEM for slope analyses
dir_dem = "./data/DEM/LMI_Haedarlikan_DEM_16bit_subset_32627.tif"
dem_big = raster(dir_dem)
crs(dem_big)

# Standard Deviation of Cross-Correlation
dir_ccs = "./results/accuracy/20180113_20180125.ccs.geo_32627.tif"
pre_ccs = raster(dir_ccs)

# check for crs
#all
if (!as.character(crs(raster(files_disp[1]))) == as.character(crs(sf))) stop()

# RASTER PREPROCESSING -----------------------------

# creating dummy to refer on:
dummy = raster(crs = "+proj=utm +zone=27 +datum=WGS84 +units=m +no_defs",
               res = c(30, 30), ext = raster::extent(extent_only_glacier))

dem = dem_big %>% resample(dummy)
slope = raster::terrain(dem, opt = "slope", unit = "degrees")

ccs = pre_ccs %>% resample(dummy)


par(mfrow = (c(1, 2)))
plot(slope)
plot(dem)
plot(ccs)
plot(sf, add = TRUE)

# crop all disp to extent
disps = map(files_disp, function(x){
  raster(x) %>%
      resample(dummy)
})
# stacking
disp = stack(disps)
disp_dailyVelocities = disp / 12
#writeRaster(disp, filename = "./results/pwr_thresh0.01/gamma_stack.tif", overwrite = TRUE)
#writeRaster(disp_dailyVelocities, filename = "./results/pwr_thresh0.01/gamma_stack_dailyVelocities.tif", overwrite = TRUE)
#saveRDS(disp, file = "./results/pwr_thresh0.01/gamma_stack.RDS")

disp = readRDS("./results/pwr_thresh0.01/gamma_stack.RDS")
#rasterVis::levelplot(disp)

# gomez displacements
#goms = map(files_gom, function (x){
#    raster(x) %>%
#        resample(dummy)
#})
#
## stacking
#gom = stack(goms)
#saveRDS(gom, file = "./data/disp_gomez/gomez_stack.RDS")

gom = readRDS("./data/disp_gomez/gomez_stack.RDS")
#rasterVis::levelplot(gom)

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
extraction_disp = exact_extract(disp, sf, "mean")
extraction_disp_px = exact_extract(disp, sf, include_xy = TRUE)
extraction_gomez = exact_extract(gom, sf, "mean")
extraction_ccs = exact_extract(ccs, sf, "mean")

# subsetwise
gamma = tidying(extraction_disp) %>% mutate(observation = observation / 12) # per day
gomez = tidying(extraction_gomez)

merged = rbindlist(list(gamma, gomez), use.names = TRUE, idcol = "dataset") %>%
    mutate(name = if_else(dataset == 1, "Gamma workflow", "SNAP workflow Goméz et al. 2020") %>% as.factor()) %>%
    mutate_at(vars(subset), as.factor)

# entire entire glacier
gamma.full = gamma %>% group_by(start) %>% summarise(mean = mean(observation))
gomez.full = gomez %>% group_by(start) %>% summarise(mean = mean(observation))
merged.full = merged %>% group_by(dataset, start) %>% summarise(mean = mean(observation)) %>%
    mutate(dataset, name = if_else(dataset == 1, "GAMMA workflow", "SNAP workflow Goméz et al. 2020") %>% as.factor)

# ---------------------------------------------------------------
# Calculate mean deviation of the techniques at nearest observation

# mean per subset
means = merged %>% group_by(name, subset) %>% summarise(meanSubset = mean(observation))

(a1 = ggplot(means, aes(subset, meanSubset, group = name, fill = name)) +
    geom_bar(stat = "identity", position = "dodge") +
    theme(legend.position = "bottom")+
    labs(fill = "Dataset", x = "Glacier Subset", y = "Mean Velocity [m / day]"))
# SLOPE ANALYSIS -----------------------------

# aggregate slope to segments
df.slope.extract = exact_extract(x = slope, y = sf, include_xy = TRUE)
dt.slope = rbindlist(df.slope.extract, idcol = "Segment")
dt.slope100 = dt.slope[coverage_fraction == 1.0, .(slope = value, x, y)]
dt.slope100$y
# query those only covering 100 with the glacier segments

# mit displacements verschneiden
dt.disp.extracted = rbindlist(extraction_disp_px, idcol = "Segment")
dt.disp.extracted100 = dt.disp.extracted[coverage_fraction == 1.0, ]
dt.disp.extracted100.select = dt.disp.extracted100[, -c("x", "y")]

ggplot(dt.disp.extracted100, aes(X20160827_20160908.disp.mag.geo_32627))+
    geom_histogram()

# fuse here
dt.bind.pre = cbind(dt.slope100, dt.disp.extracted100.select)
dt.bind = dt.bind.pre[, -c("coverage_fraction")]

# rename variable names
nm = names(dt.bind)
disps = nm[5:13]
disps.split = str_split_fixed(disps, pattern = "_", 2)[,1]
vec = c("slope", "x", "y", "Segement", disps.split)

names(dt.bind) = vec

# to longer format
dt.longer = dt.bind %>% pivot_longer(cols = -c(slope, x, y, Segement))

# VISUALISATION to be outsourced! -----------------------------

(subsets = ggplot() +
    geom_sf(aes(fill = as.factor(ID)), sf) +
    labs(fill = "Subset area") +
    scale_fill_brewer(type = "seq", palette = 1, direction = -1))


colr <- colorRampPalette(brewer.pal(9, 'Blues'))
# quick viz
#rasterVis::levelplot(disp,
#          margin=FALSE,
#          colorkey=list(
#            space='bottom',
#            labels=list(at=0:20, font=4),
#            axis.line=list(col='black'),
#            width=0.75
#          ),
#          par.settings=list(
#            strip.border=list(col='transparent'),
#            strip.background=list(col='transparent'),
#            axis.line=list(col='transparent')
#          ),
#          scales=list(draw=FALSE),
#          col.regions=colr,
#          at=seq(0, 20, len=101),
#          names.attr=rep('', nlayers(disp)))

# Overall movement
ggplot(gomez.full, aes(start, mean)) +
    geom_point() +
    geom_line()

ggplot(gamma.full, aes(start, mean)) +
    geom_point() +
    geom_line()

(gg0 = ggplot(merged.full, aes(start, mean, group = name, color = name)) +
    geom_point(size = 3) +
    geom_line() +
    labs(color = "Dataset", x = "Year", y = "Velocity [m / day]") +
    theme(legend.position = "bottom"))

# gomez per subset

(gg1 = ggplot(gomez) +
  geom_point(aes(start, observation, group = subset), color = "grey15")+
    geom_line(aes(start, observation, group = subset)) +
  facet_wrap(~ subset) +
  #geom_smooth(aes(start, observation), method = "lm", color = "darkgreen", fill = "grey60") +
  theme_minimal() +
  labs(title = "Glacier movement by geographical subset",
       subtitle = "Data from Gómez et al. (2020)",
       y = "Velocity [m / day]", x = "Date") +
  theme(strip.text.x = element_text(size = 20),
        axis.text.x = element_text(angle = 65)) +
    ylim(c(-0.5, 2.5)))


# gamma per subset

(gg2 = ggplot(gamma) +
  geom_point(aes(start, observation, group = subset), color = "grey15")+
    geom_line(aes(start, observation, group = subset)) +
  facet_wrap(~ subset) +
  #geom_smooth(aes(start, observation), method = "lm", color = "darkgreen", fill = "grey60") +
  theme_minimal() +
  labs(y = "Velocity [m / day]", x = "Date") +
  theme(strip.text.x = element_text(size = 20),
        axis.text.x = element_text(angle = 65)))


# merged per subset
(gg3 = ggplot(merged, aes(start, observation, group = name, color = name)) +
    geom_point() +
    geom_line() +
    facet_grid(cols = vars(subset)) +
    theme(legend.position = "bottom") +
    labs(color = "Dataset", x = "Date", y = "Velocity [m / day]"))

# only 2020
filtered2020 = merged %>% filter(start >= "2020-01-01")
filtered2020 %>% arrange(subset)

(gg4 = ggplot(filtered2020) +
  geom_point(aes(start, observation, group = subset), color = "grey15")+
    geom_line(aes(start, observation, group = subset)) +
  facet_wrap(~ subset) +
  #geom_smooth(aes(start, observation), method = "lm", color = "darkgreen", fill = "grey60") +
  theme_minimal() +
  labs(y = "Velocity [m / day]", x = "Date") +
  theme(strip.text.x = element_text(size = 20),
        axis.text.x = element_text(angle = 65)))




# marrangeGrob(list(subsets, gg3), nrow = 2, ncol = 1, top = "")
ggsave(file.path(plotdir, "Gomez_glacier_movement.png"), plot = gg1, device = "png", scale = 0.5, height = 10, width = 15)
ggsave(file.path(plotdir, "Gamma_glacier_movement_2020.png"), plot = gg2, device = "png", scale = 0.5, height = 10, width = 15)
ggsave(file.path(plotdir, "MergedDS_subsetMeans_lines_2020.png"), plot = gg0, device = "png", height = 5, width = 5)
ggsave(file.path(plotdir, "MergedDS_subsetFacets_2020.png"), plot = gg3, device = "png", height = 5, width = 10)
ggsave(file.path(plotdir, "Subsets.png"), plot = subsets, device = "png", height = 5, width = 5)
ggsave(file.path(plotdir, "Gamma_glacier_movement_only2020.png"), plot = gg4, device = "png", scale = 0.5, height = 10, width = 15)

# Analyses
ggsave(a1, filename = file.path(plotdir, "MergedDS_subsetMeans_bars_2020.png"), device = "png", height = 5, width = 5)

# -------------------------------------------------------
# Visualisation of slope to movement

ggplot(dt.longer, aes(slope, value, color = as.factor(name)))+
    geom_point() +
    xlim(c(0,25)) +
    facet_grid(rows = vars(Segement))

ggplot(dt.longer, aes(slope, value, color = as.factor(name)))+
    geom_point()