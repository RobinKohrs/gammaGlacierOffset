# Title     : Extracts statistical measurements from displacement maps by pre-defined polygons
# Created by: Konstantin Schellenberg
# Created on: 17.11.2020

# data structure

# storage of gomez' data
# ./ data / disp_gomez / *.tif

# vector geometries
# ./ vector_geometry / glacier.gpkg





# load packages
packages = c("tidyverse", "raster", "sf", "exactextractr", "stringr", "data.table")
lapply(packages, require, character.only = TRUE)

# CREATE PATHS -----------------------------

plotdir = "./plots/glacier_movement"
if (!dir.exists(plotdir)) dir.create(recursive = TRUE)

# LOAD DATA -----------------------------
# glacier vectors
path_sf = "./vector_geometry/glacier.gpkg"
sf = st_read(path_sf, layer = "parts")

# displacement data gomez et al.
dir_gomez = "./data/disp_gomez"
files = list.files(dir_gomez, pattern = ".tif$", full.names = TRUE)

# stacking
gom = stack(files)

# check for crs
if (!as.character(crs(gom)) == as.character(crs(sf))) stop()

# RASTER PREPROCESSING -----------------------------

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

transformation = function(exact_extract_output){
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
}

extraction_gomez = exact_extract(gom, sf, "mean")
#extraction_disp = exact_extract(, sf, "mean")

gomez = transformation(extraction_gomez)

# VISUALISATION -----------------------------

gg = ggplot(gomez) +
  geom_point(aes(start, observation, group = subset), color = "grey15")+
  facet_wrap(~ subset) +
  geom_smooth(aes(start, observation), method = "lm", color = "darkgreen", fill = "grey60") +
  theme_minimal() +
  labs(title = "Glacier movement by geographical subset",
       subtitle = "Data from Gómez et al. (2020)",
       y = "Velocity [m / year]", x = "Date") +
  theme(strip.text.x = element_text(size = 20),
        axis.text.x = element_text(angle = 65))
print(gg)

ggsave(file.path(plotdir, "Gomez_glacier_movement.png"), device = "png", scale = 0.5, height = 10, width = 15)
