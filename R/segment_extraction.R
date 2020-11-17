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
dir_disp = "./results"
files_disp = list.files(dir_disp, pattern = "\\.mag.geo_32627.tif$", full.names = TRUE)

# check for crs
#if (!as.character(crs(raster(files_disp[1]))) == as.character(crs(sf))) stop()

# RASTER PREPROCESSING -----------------------------

# stacking

#disp = stack(files_disp)

# creating dummy to refer on:
dummy = raster(crs = "+proj=utm +zone=27 +datum=WGS84 +units=m +no_defs",
               res = c(30, 30), ext = raster::extent(extent_only_glacier))

# crop all disp to extent
disps = map(files_disp, function(x){
  raster(x) %>%
      resample(dummy)
})

goms = map(files_gom, function (x){
    raster(x) %>%
        resample(dummy)
})

# stacking
gom = stack(goms)
disp = stack(disps)



# NAMING -----------------------------
# test stringr if they match...

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

# HERE

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

gomez = tidying(extraction_gomez)
gamma = tidying(extraction_disp) %>% mutate(observation = observation / 12) # per day

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
        axis.text.x = element_text(angle = 65))
print(gg1)

gg2 = ggplot(gamma) +
  geom_point(aes(start, observation, group = subset), color = "grey15")+
  facet_wrap(~ subset) +
  geom_smooth(aes(start, observation), method = "lm", color = "darkgreen", fill = "grey60") +
  theme_minimal() +
  labs(title = "Glacier movement by geographical subset",
       subtitle = "Data processed by GAMMA offset tracking",
       y = "Velocity [m / temp.baseline]", x = "Date") +
  theme(strip.text.x = element_text(size = 20),
        axis.text.x = element_text(angle = 65))
print(gg2)

ggsave(file.path(plotdir, "Gamma_glacier_movement.png"), plot = gg2, device = "png", scale = 0.5, height = 10, width = 15)
