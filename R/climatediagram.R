#'
#' Make Walter Lieth climate diagram for assignment
#' 

library(raster)
library(ncdf4)

# set wd to far away...
setwd("/home/robin/projects/climate/data_climate_research_unit/")

# load data
nc.pre = nc_open("pre/cru_ts4.04.1901.2019.pre.dat.nc")
nc.temp = nc_open("temp/cru_ts4.04.1901.2019.tmp.dat.nc")
nc.temp
nc.pre

pre = brick("pre/cru_ts4.04.1901.2019.pre.dat.nc", varname="pre")
tmp = brick("temp/cru_ts4.04.1901.2019.tmp.dat.nc", varname="tmp")
tmax = brick("tmax/cru_ts4.04.1901.2019.tmx.dat.nc", varname="tmx")
tmin = brick("tmin/cru_ts4.04.1901.2019.tmn.dat.nc", varname="tmn")

# point of glacier in lat long
glacier.point=data.frame("x" = -20.374, "y" = 63.816)

# extract the values
pre.site = data.frame(extract(pre, glacier.point, ncol=2))
tmp.site = data.frame(extract(tmp, glacier.point, ncol=2))
tmax.site = data.frame(extract(tmax, glacier.point, ncol=2))
tmin.site = data.frame(extract(tmin, glacier.point, ncol=2))

years = 1901:2019
month = c("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

# change col names
names(pre.site) = paste(rep(years, each=12), rep(month, times=116), sep="_")
names(tmp.site) = paste(rep(years, each=12), rep(month, times=116), sep="_")
names(tmax.site) = paste(rep(years, each=12), rep(month, times=116), sep="_")
names(tmin.site) = paste(rep(years, each=12), rep(month, times=116), sep="_")

# write them out
f = "temp/temp19012019.csv"
if (! file.exists(f)) {
  write.csv(tmp.site, f)
  write.csv(pre.site, "temp/temp19012019.csv")
  write.csv(tmax.site, "tmax/tmax19012019.csv")
  write.csv(tmin.site, "tmin/tmin19012019.csv")
}


# Calculate monthly data for the period 1970 - 2000
pre1970 = pre.site[829:1428]
tmin1970 <- tmin.site[829:1428]
tmax1970 <- tmax.site[829:1428]


# Precip - mean monthly total
pre1970.mean = t(as.data.frame(sapply(month, function(x) rowMeans(pre1970[, grep(x, names(pre1970))]))))
rownames(pre1970.mean) = "Precip" # Rename columns in the new data frame object

# tmax
tmax1970.mean = t(as.data.frame(sapply(month, function(x) rowMeans(tmax1970[, grep(x, names(tmax1970))]))))
rownames(tmax1970.mean) = "tmax"

# tmin
tmin1970.mean = t(as.data.frame(sapply(month, function(x) rowMeans(tmin1970[, grep(x, names(tmin1970))]))))
rownames(tmin1970.mean) = "tmin"


# tmin.min
tmin1970.min = t(as.data.frame(sapply(month, function(x) apply(tmin1970[, grep(x, names(tmin1970))], 1, FUN=min))))
rownames(tmin1970.mean) = "tmin.min"


# create matrux
mx = as.matrix(rbind(pre1970.mean[1,], tmin1970.mean[1,], tmax1970.mean[1,], tmin1970.min[1,]))

write.csv(mx, "iceland19702019.csv")

# load it back in
iceland = as.matrix(read.csv("iceland19702019.csv", row.names = 1))

# make plot

plotWalterLieth(iceland, station="Sólheimajökull Glacier [Lat: 63.55 Long: -19.3]", per="1970 to 2019")

