#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################
# Window Size Refinement loops
#########################################

import argparse
import shutil
import subprocess

from functions import *

parser = argparse.ArgumentParser(description="Export Offsets")
# get positional arguments
parser.add_argument("-p", "--print", metavar="", dest="print", help="only print cmd call", action="store_const",
                    const=True)
args = parser.parse_args()


def get_all_files(dir):
    # all top_level_directories
    all_dirs = os.listdir(dir)
    all_files = []
    
    # for all top level directories
    for j in all_dirs:
        
        # build the full path
        full_path = os.path.join(dir, j)
        
        # if its a directory
        if os.path.isdir(full_path):
            all_files = all_files + get_all_files(full_path)
        else:
            all_files.append(full_path)
    
    return all_files


def geocode_back(list_of_files, dem_dir):
    """
    input parameters:
  data_in       (input) data file (format as specified by format_flag parameter)
  width_in      width of input data file
  lookup_table  (input) lookup table containing pairs of real-valued input data coordinates
  data_out      (output) output data file
  width_out     width of gc_map lookup table, output file has the same width
  nlines_out    number of lines of output data file (enter - or 0 for default: number of lines in gc_map)
  interp_mode   interpolation mode (enter - for default)
                  0: nearest-neighbor
                  1: bicubic spline (default)
                  2: bicubic-log spline, interpolates log(data)
                  3: bicubic-sqrt spline, interpolates sqrt(data)
                  4: B-spline interpolation (default B-spline degree: 5)
                  5: B-spline interpolation sqrt(x) (default B-spline degree: 5)
                  6: Lanczos interpolation (default Lanczos function order: 5)
                  7: Lanczos interpolation sqrt(x) (default Lanczos function order: 5)
                NOTE: log and sqrt interpolation modes should only be used with non-negative data!
  dtype         input/output data type (enter - for default)
                  0: FLOAT (default)
                  1: FCOMPLEX
                  2: SUN/BMP/TIFF 8 or 24-bit raster image
                  3: UNSIGNED CHAR
                  4: SHORT
                  5: DOUBLE
  lr_in         input  SUN/BMP/TIFF raster image flipped left/right (enter - for default: 1: not flipped (default), -1: flipped)
  lr_out        output SUN/BMP/TIFF raster image flipped left/right (enter - for default: 1: not flipped (default), -1: flipped)
  order         Lanczos function order or B-spline degree (2->9) (enter - default: 5)
  e_flag        extrapolation flag (enter - for default)
                  0: do not extragpolate (default)
                  1: extrapolate up to 0.5 pixels beyond input edges

    """
    
    for f in list_of_files:
        
        # find mli width
        f_basepath_list = os.path.dirname(f).split("/")[:-1]
        basepath_strings = "/".join(f_basepath_list)
        date = basepath_strings.split("/")[-1]
        date_main = date[0:8]
        mli = [os.path.join(basepath_strings, x) for x in os.listdir(basepath_strings) if
               date_main in x and x.endswith(".rmli.par")][0]
        
        eqa_dem_par = \
        [os.path.join(dem_dir, x) for x in os.listdir(dem_dir) if x.endswith("EQA_dem.par") and date[0:8] in x][0]
        eqa_dem_width = int(awkpy(eqa_dem_par, "width", 2))
        
        # in dem PDF S1_tracking nehmen sie die gleichen width_out width_in, die sie in geocode
        # verwenden um das DEM in die slant-range mli geometrie zu bringen
        # ich glaube, da wir für die Erstellung des MLI, als auch für range-steps u. azimuth-steps die gleiche Auflösung verwenden
        # (30,60) sind die Input-Width (bestimmt durch die range/az steps) und die output-widht (bestimmt durch die MLI-breite und HÖHE)
        # gleich
        
        # die Input-breite denke ich können wir aus dem .off-file nehmen?!
        off_file = \
        [os.path.join(basepath_strings, "intensity", x) for x in os.listdir(os.path.join(basepath_strings, "intensity"))
         if x.endswith(".off")][0]
        with open(off_file, "r") as src:
            lines = [line for line in src.readlines()]
            for l in lines:
                res = re.search(r"^offset_estimation_range_samples:\s*(\d*)", l)
                if res:
                    range_samples = res.group(1)
        
        # die output breite und höhe
        with open(mli, "r") as src:
            lines = [line for line in src.readlines()]
            for i in lines:
                w = re.search("^range_samples:\s*(\d*)", i)
                if w is not None:
                    width_mli = w.group(1)
                
                h = re.search("^azimuth_lines:\s*(\d*)", i)
                if h is not None:
                    height_mli = h.group(1)
        
        # find lookup table
        dem_dir = "../data/DEM/"
        lt = \
        [os.path.join(dem_dir, file) for file in os.listdir(dem_dir) if date_main in file and file.endswith(".lt")][0]
        
        # data out
        data_out = os.path.join(f + ".geo")
        
        # build cmd
        cmd = f"geocode_back {f} {range_samples} {lt} {data_out} {eqa_dem_width} "  # {height_mli}

        if not os.path.isfile(data_out):
            out = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True) if not args.print else print(cmd)
        else:
            print("geocoded file already exists: ", data_out)


def make_geotiffs(geofiles, dem_dir):
    """
      DEM_par  (input) DIFF/GEO DEM parameter file
      data     (input) data file
      type     data type:
                 0: RASTER 8 or 24 bit uncompressed raster image, SUN (*.ras), BMP:(*.bmp), or TIFF: (*.tif)
                 1: SHORT integer (2 bytes/value)
                 2: FLOAT (4 bytes/value)
                 3: SCOMPLEX (short complex, 4 bytes/value)
                 4: FCOMPLEX (float complex, 8 bytes/value)
                 5: BYTE
      GeoTIFF  (output) GeoTIFF file (.tif i
    """
    
    for f in geofiles:
        date = os.path.basename(f)[0:8]
        intensity_dir = os.path.dirname(f)
        try:
            dem_par = \
            [os.path.join(dem_dir, x) for x in os.listdir(dem_dir) if x.endswith("EQA_dem.par") and date in x][0]
            output_file = f + ".tif"
            
            cmd = f"data2geotiff {dem_par} {f} 2 {output_file}"

            # check if file already exists
            if not os.path.isfile(output_file):
                out = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True) if not args.print else print(cmd)
                if out:
                    print(out.stdout.decode("UTF-8"))
            else:
                print("geotiff already exists")

        except:
            print("SOME ERROR I DONT KNOW")


def transform(geotiffs, results, tuple_dir):

    
    # handle deleter with care
    deleter = f"find {tuple_dir} -name *32627* | xargs rm"
    subprocess.run(deleter, shell=True) if not args.print else print("no deletion of files.")
    
    for geotiff in geotiffs:
        
        # get only the directory
        base_dir = os.path.dirname(geotiff)
        
        # basenmae is just the name of the file without the directory information
        basename = os.path.basename(geotiff)
        basename_split = basename.split(".")
        sep = "."
        new_name = sep.join(basename_split[0:4]) + "_32627" ".tif"
        
        # assemble the name
        output = os.path.join(base_dir, new_name)
        print(output)
        
        # gdalwarp
        cmd = f"gdalwarp -t_srs EPSG:32627 {geotiff} {output}"
        out = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True) if not args.print else print(cmd)

        # copy data to results folder: easier to copy
        if not args.print:
            print(f"copying {output} to {results}")
            shutil.copy(output, results)
        else:
            print("not copying . . .")
        
        if out:
            print(out.stdout.decode("UTF-8"))


def main():
    # directories for all two data dependent files
    tuple_dir = "../data/tuples/"
    dem_dir = "../data/DEM"
    results = "../results"
    
    if not os.path.exists(results):
        os.mkdir(results)
    
    # make a list of all fildes
    all_files = get_all_files(tuple_dir)
    
    # filter the files you want
    file_endings = [".mag", ".real", ".imag", ".ccs"]
    # files_to_geocode = [f for f in all_files if
    #                     f.endswith(file_endings[0])]
    
    files_to_geocode = [f for f in all_files if
                        f.endswith(file_endings[0]) or f.endswith(file_endings[1]) or f.endswith(file_endings[2]) or
                        f.endswith(file_endings[3])]
    print(files_to_geocode)
    
    # geocode_back
    geocode_back(files_to_geocode, dem_dir=dem_dir)

    # geocode all .geofiles
    # find all geo files
    file_endings = [".geo"]
    geofiles_to_geocode = [f for f in all_files if f.endswith(file_endings[0])]
    
    make_geotiffs(geofiles_to_geocode, dem_dir=dem_dir)
    # find all geotiffs
    geotiffs_to_copy = [f for f in all_files if f.endswith(".tif")]
    [print(i) for i in geotiffs_to_copy]; exit()

    transform(geotiffs_to_copy, results, tuple_dir)
    

# --------------------------------------------------------------------------------
if __name__ == "__main__":

    main()
# --------------------------------------------------------------------------------
