> This will hopefully help to decide which height and width must be used in order 
> to plot the specific file and where to find the width and height


# Plot the SLC

# Plot the MLI

# Plot the Lookuptable

- The lookuptable is responsible for transferring back and forth between the Radar-Geometry
and the ground range geometry
- It is geocoded and can be plotted with the width that is found in the cropped dem, produced by gc_map (e.g eqa.dem.par)

# PLot the geocoded file (.geo)

- The geocoded file will probably have as many colums (width) as the cropped DEM (e.g eqa.dem.par)


```commandline
dismph ...lt
```