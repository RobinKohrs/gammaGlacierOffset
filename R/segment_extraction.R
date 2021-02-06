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
dir_ccs = "./results/accuracy"
files_ccs = list.files(dir_ccs, pattern = "*ccs.geo_32627.tif$", full.names = TRUE)

# check for crs
#all
if (!as.character(crs(raster(files_disp[1]))) == as.character(crs(sf))) stop()

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
#disps = map(files_disp, function(x){
#  raster(x) %>%
#      resample(dummy)
#})
## stacking
#disp = stack(disps)
#disp_dailyVelocities = disp / 12

#writeRaster(disp, filename = "./results/pwr_thresh0.01/gamma_stack.tif", overwrite = TRUE)
#writeRaster(disp_dailyVelocities, filename = "./results/pwr_thresh0.01/gamma_stack_dailyVelocities.tif", overwrite = TRUE)
#saveRDS(disp, file = "./results/pwr_thresh0.01/gamma_stack.RDS")

disp = readRDS("./results/pwr_thresh0.01/gamma_stack.RDS")
#disp = readRDS("./results/pwr_thres0.1/gamma_stack.RDS")
#rasterVis::levelplot(disp)

# accuracy
#ccss = map(files_ccs, function(x){
#  raster(x) %>%
#      resample(dummy)
#})
## stacking
#ccs = stack(ccss)
#writeRaster(ccs, filename = "./results/accuracy/ccs_stack.tif", overwrite = TRUE)
#saveRDS(ccs, file = "./results/accuracy/ccs_stack.RDS")
ccs = readRDS(file = "./results/accuracy/ccs_stack.RDS")

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
disp.pairs = names(disp) %>%
  stringr::str_extract(pattern = "\\d+_\\d+") %>%
  str_split(pattern = "\\_") %>%
  map(., ~ as.Date(.x, format = "%Y%m%d"))

names(pairs) = map(pairs, ~ .x[1] %>% as.character())
names(disp.pairs) = map(disp.pairs, ~ .x[1] %>% as.character())

# calculating date difference
diffs = map_dbl(disp.pairs, ~ diff(as.Date(.x, format = "")))

# some have longer baselines than 12 day, the latter is the usual though
pairs_diff = as.data.frame(disp.pairs) %>%
    t() %>%
    as.data.frame(row.names = FALSE) %>%
    dplyr::select(main = V1, secondary = V2) %>%
    mutate(temporal.baseline = diffs, year = year(main),
           month = month(main),
           week = week(main),
           doy = (yday(main) + yday(secondary)) / 2) %>%
    arrange(main)
write_csv(pairs_diff, file = "./results/tables/dates.csv")

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
      mutate_at(vars(subset), as.factor)

  return(tidy)
}
extraction_disp = exact_extract(disp, sf, "mean")
extraction_disp_px = exact_extract(disp, sf, include_xy = TRUE)
extraction_ccs = exact_extract(ccs, sf, "mean")
extraction_gomez = exact_extract(gom, sf, "mean")

# subsetwise
gamma = tidying(extraction_disp)  %>% mutate(observation = observation / 12) # per day
gomez = tidying(extraction_gomez)
df.ccs = tidying(extraction_ccs)

# add ccs to gamma, confbands added
df.uncertainty = left_join(gamma, df.ccs, by = c("start", "subset")) %>%
    dplyr::select(c(start, subset, observation = observation.x, uncertainty = observation.y)) %>%
    mutate(lower.confint = observation - 1.96 * uncertainty,
                            upper.confint = observation + 1.96 * uncertainty)

#' add uncertainty measure here
merged = rbindlist(list(df.uncertainty, gomez), use.names = TRUE, idcol = "dataset", fill = TRUE) %>%
    mutate(name = if_else(dataset == 1, "Gamma workflow", "SNAP workflow Goméz et al. 2020") %>% as.factor()) %>%
    mutate_at(vars(subset), as.factor)

summary_subset = merged %>% group_by(name, subset) %>% summarise_all(function(x) mean(x, na.rm = TRUE))
summary_observation = df.uncertainty %>% group_by(start) %>% summarise_all(~mean(.x, na.rm = TRUE))

# entire entire glacier
gamma.full = gamma %>% group_by(start) %>% summarise(mean = mean(observation))
gomez.full = gomez %>% group_by(start) %>% summarise(mean = mean(observation))

merged.full = merged %>% group_by(dataset, start) %>% summarise(mean = mean(observation), mean_lower = mean(lower.confint, na.rm = TRUE),
                                                                mean_upper = mean(upper.confint, na.rm = TRUE)) %>%
    mutate(dataset, name = if_else(dataset == 1,"GAMMA workflow", "SNAP workflow Goméz et al. 2020") %>% as.factor)

# ---------------------------------------------------
# deviation analysis

# average standard deviation of the results
mean(df.ccs$observation)

# bias between gomez and gamma mean glacier velocity
mean(gamma$observation) - mean(gomez$observation)


# Plotting ------------------------------------------

#colr <- colorRampPalette(brewer.pal(9, 'Blues'))
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

(subsets = ggplot() +
    geom_sf(aes(fill = as.factor(ID)), sf) +
    labs(fill = "Subset area") +
    scale_fill_brewer(type = "seq", palette = 1, direction = -1))

ggplot(df.uncertainty, aes(subset, observation)) +
    geom_point()

(a1 = ggplot(summary_subset, aes(subset, observation, group = name, fill = name)) +
    geom_bar(stat = "identity", position = "dodge") +
    theme(legend.position = "bottom")+
    labs(fill = "Dataset", x = "Glacier Subset", y = "Mean Velocity [m / day]"))

# Overall movement
ggplot(gomez.full, aes(start, mean)) +
    geom_point() +
    geom_line()

# ---------------------------
# Uncertainty
# gamma with uncertainty

ggplot(summary_observation, aes(start, observation)) +
    geom_point() +
    geom_line() +
    geom_errorbar(aes(ymin = lower.confint, ymax = upper.confint))

(gg0a = ggplot(df.uncertainty, aes(start, observation, group = subset, color = subset)) +
    geom_point(size = 2) +
    geom_line() +
    #geom_smooth(method = "lm", se = F) +
    geom_errorbar(aes(ymin = lower.confint, ymax = upper.confint)) +
    labs(x = "Date", y = "Velocity [m / day]", color = "Glacier Subset") +
    theme(legend.position = "bottom"))

# only uncertainty
ggplot(df.ccs, aes(start, observation, group = subset, color = subset)) +
    geom_point() +
    geom_line()

(gg0b = ggplot(merged.full, aes(start, mean, group = name, color = name)) +
    geom_point(size = 3) +
    geom_line() +
    geom_errorbar(aes(ymin = mean_lower, ymax = mean_upper)) +
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
#
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

# monthly aggregation
months = merged.full %>% mutate(year = year(start), month = month(start))
summary_months = months %>% group_by(month, name) %>% summarise(observation = mean(mean)) %>%
    mutate_at(vars(month), as.factor)

(gg4 = ggplot(filtered2020, aes(start, observation, group = subset, color = subset)) +
    geom_point() +
    geom_line() +
    labs(x = "Date", y = "Velocity [m / day]", color = "Glacier Subset") +
    theme(legend.position = "bottom"))

# include gomez' dataset
(gg5 = ggplot(summary_months, aes(month, observation, group = name, color = name)) +
    geom_point() +
    geom_line() +
    labs(x = "Date", y = "Velocity [m / day]", color = "Glacier Subset") +
    theme(legend.position = "bottom"))




# marrangeGrob(list(subsets, gg3), nrow = 2, ncol = 1, top = "")
ggsave(file.path(plotdir, "Gomez_glacier_movement.png"), plot = gg1, device = "png", scale = 0.5, height = 10, width = 15)
ggsave(file.path(plotdir, "Gamma_glacier_movement.png"), plot = gg2, device = "png", scale = 0.5, height = 10, width = 15)
ggsave(file.path(plotdir, "Gamma_subsetMeans_lines.png"), plot = gg0a, device = "png", height = 5, width = 5)
ggsave(file.path(plotdir, "MergedDS_subsetMeans_lines.png"), plot = gg0b, device = "png", height = 5, width = 5)
ggsave(file.path(plotdir, "MergedDS_subsetFacets.png"), plot = gg3, device = "png", height = 5, width = 10)
ggsave(file.path(plotdir, "Subsets.png"), plot = subsets, device = "png", height = 5, width = 5)
ggsave(file.path(plotdir, "Gamma_glacier_movement_only2020.png"), plot = gg4, device = "png", height = 5, width = 5)
ggsave(file.path(plotdir, "MergedDS_monthly.png"), plot = gg5, device = "png", height = 5, width = 5)

# Analyses
ggsave(a1, filename = file.path(plotdir, "MergedDS_subsetMeans_bars_2020.png"), device = "png", height = 4, width = 10)

# -------------------------------------------------------
# SLOPE ANALYSIS -----------------------------

# aggregate slope to segments
df.slope.extract = exact_extract(x = slope, y = sf, include_xy = TRUE)
dt.slope = rbindlist(df.slope.extract, idcol = "Segment")
dt.slope100 = dt.slope[coverage_fraction == 1.0, .(slope = value, x, y)]

# aggregate DEM to segments
df.dem.extract = exact_extract(x = dem, y = sf, include_xy = TRUE)
dt.dem = rbindlist(df.dem.extract, idcol = "Segment")
dt.dem100 = dt.dem[coverage_fraction == 1.0, .(dem = value, x, y)]
# query those only covering 100 with the glacier segments

# mit displacements verschneiden
dt.disp.extracted = rbindlist(extraction_disp_px, idcol = "Segment")
dt.disp.extracted100 = dt.disp.extracted[coverage_fraction == 1.0, ]
dt.disp.extracted100.select = dt.disp.extracted100[, -c("x", "y")]

ggplot(dt.disp.extracted100, aes(X20160827_20160908.disp.mag.geo_32627))+
    geom_histogram()

# fuse here
dt.bind.pre = cbind(dt.slope100, dt.dem100[, .(dem)], dt.disp.extracted100.select)
dt.bind = dt.bind.pre[, -"coverage_fraction"]

# rename variable names
nm = names(dt.bind)
disps = nm[str_detect(nm, pattern = "^X")]
rest = nm[!str_detect(nm, pattern = "^X")]
disps.split = str_split_fixed(disps, pattern = "_", 2)[,1]
vec = c(rest, disps.split)

names(dt.bind) = vec
names(dt.bind)

# to longer format
dt.longer = dt.bind %>% pivot_longer(cols = -c(slope, dem, x, y, Segment))

# -----------------------------------------------------------
# Visualisation of slope to movement

# average slope of the segments
(slope.segment = dt.bind %>% group_by(Segment) %>% summarise(mean.slope = mean(slope), mean.height = mean(dem)))
write_csv(slope.segment, file = "./results/tables/slope_at_segments.csv")

# dem
ggplot(dt.dem100, aes(y, dem)) + geom_point(size = .5)
ggplot(dt.dem100, aes(x, dem)) + geom_point(size = .5)

# slope
ggplot(dt.slope100, aes(y, slope)) + geom_point(size = .5)
ggplot(dt.slope100, aes(x, slope)) + geom_point(size = .5)

# dem x slope
ggplot(dt.bind, aes(dem, slope)) + geom_point() + geom_smooth(method = "gam")

ggplot(dt.longer, aes(slope, value, color = as.factor(name)))+
    geom_point() +
    xlim(c(0,25)) +
    facet_grid(rows = vars(Segment))

ggplot(dt.longer, aes(slope, value, color = as.factor(name)))+
    geom_point()