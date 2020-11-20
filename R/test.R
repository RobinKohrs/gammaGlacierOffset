# Title     : TODO
# Objective : TODO
# Created by: robin
# Created on: 20.11.20

library(ggplot2)

df = data.frame(x=rnorm(100), y=rnorm(100))

ggplot(df) + geom_point(aes(x=x, y=y, size=y, col=y))

