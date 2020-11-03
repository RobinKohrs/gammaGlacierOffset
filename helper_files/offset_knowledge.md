# Most important details from the Gamma Docu

- The quality of the offsets depends on the existence of nearly identical features in both SAR
  images on the scale of the **used patches**
- If there is a lot of coherece, the tracking can be performed with small patch sizes to an
  astonishing performance
- Oversampling raster applied to the image patches increase the offset estimation accuracy


## Three main steps

1. Find bilinear polynomial function
2. Precise estimation of the offsets
3. Computation of the displacement



### Bilinear Function

- Determine orbital offsets between the two slcs either by cross-correlating the real-valued
  intensity or by optimising the fringe visibility
- The polynomial coefficients for the offsets are computed over the whole iamge for range and
  azimuth

### Precisce estimates of the offsets in area of interst

- The bilinear function helps to decide where its possible to estimates local offsets
- Typcal sizes of the patches for offset estimation are 64 x 256 pixels resulting in 1km square
  pixels for old saltellites

### 

- Offsets found in range and azimuth are then transformed to displacements
- The global bilinear function is again used to seperate between the offsets resulting from
  different orbits and thos resulting from displacement
- Displacement can be expressed either in SAR geometry or in Ground Rang

- **you essentially measure the displacements from the offsets**

# <u>Now using GAMMA</u>

## `create_offset`

- Will create the **offset parameter file**
- you already need to decide on the offset method that you will use (either fringe visibility or
  intensity cross correlation)
- Choice of the size of image chips that will be used when estimating the **local offsets** in
  the next step (either `offset_pwr` or `offset_SLC`)

## Initial range and azimuth offsets

### Manually

- disSLC

### Automatically (`init_offset_orbit` and `init_offset`)

- `init_offset_orbit` makes a first guess of the offsets based on the orbital information
- This guess can be improved by `init_offset` which determinies the inital offsets based on the
  image cross-correlation. 
- You can run `init_offset` first with multilooking resolution and afterwards with single look
  resolution
- Each time the offset estimates are written to a file `*.off` and then get updated each time
- User can also define position and size of the area where to calculate cross-correlation
- The default position is in the middle of the image with a size of 1024 x 1024 pixels
- User can also set a threshold for cross-correlation under which the offset estimates get
  rejected


### Even more precise estimates of the offsets `offset_slc`

- The range search window ,rwin, can either be set manually, or it takes the input from the offset
parameter file and the line `offset_estimation_azimuth_samples`
- Can't be bigger than the interferogram patch size `ISZ`, by default 16
- When running the `offset_SLC`, the initial `.off`-file will be updated  
 


