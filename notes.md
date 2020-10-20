This repo will contain the code for performing the offset tracking with gamma. Winter Semester 2020/21. Authorship:
Robin Kohrs, Konstantin Schellenberg, University of Jena, M.Sc. Geoinformatics.

# Flowchart

Dieses Flussdiagramm enthält die notwendigen Schritte, um von Level-1 Sentinel-1 SLC Daten Offset-Tracking von
Gletschern durchzuführen. Es ist unterteilt sich in (0) die Erstellung einer kohärenten Ordnerstruktur, (1) den 
Import der SLCs und des isländischen National-DEM in ein GAMMA-kompatibles Format, (2) das debursten des Subswaths
IW2, welcher ausschließlich für unsere Prozessierung notwendig ist und (3) das Offset-Tracking, welches mehrere
Sub-Routinen enthält. Zuletzt bewerten wir den Optimierungsprozess der Tracking-Window-Größe und visualisieren 
unsere Ergebnisse (4, 5).

## Retrieve dates from SLC directory
- Function to get back ALL files for one interfeometric pair splitted up in each date

```python
dates_dict = {"<date1>_<date2>":
                    {"date1":[],
                     "date2":[]},
               "<date3>_<date4>":
                    {"date3":[],
                     "date4":[]},
                    ...}
```

## 0. Create Folder Structure
- Erstellt die Ordnerstruktur

## 1. SLC (R) and DEM Import (K)
- It's really important to name the file: 
    + <date>_<swath>_<pol>.slc
    + <date>_<swath>_<pol>.slc.par
    + <date>_<swath>_<pol>.slc.tops_par

- 

 
## Tab-files für master und slave erstellen

- Tabfiles erstellen für die NICHT-mosaikierten SLCs
- Sowohl für Master als auch für slave, da es später bei der Ko-registrierung gebraucht wird
- 

```python
for each <date>
    for each pol
        <date>_<swath1>_<pol1>.slc <date>_<swath1>_<pol1>.slc.par <date>_<swath1>_<pol1>.slc.tops_par
        <date>_<swath2>_<pol1>.slc <date>_<swath2>_<pol1>.slc.par <date>_<swath2>_<pol1>.slc.tops_par
        <date>_<swath3>_<pol1>.slc <date>_<swath3>_<pol1>.slc.par <date>_<swath3>_<pol1>.slc.tops_par
```


## 2 Mosaiikieren (debursten) of subswath 2
- Brauchen wir für die ERstellung der MLIs!
- Mosaiikiert werden müssen sowhol mast als auch sl!
- (Deramp?, bei offset-fitting auch deramp flag) 


```python
for each <date>.slc:
    SLC_mosaic_S1_tops <date>.slc_tab range_looks (10) azimuth_looks (2) 
# Return <date>.slc (mosaic für den gesamten Subswath)
# Return <date>slc.par (parameterfile des mosaikierten Subswath)
```

# 2.1 Multilooking vom Master
- mutlilooking nur für den Master
- Multilooking vom mosaiikierten SLC!

```commandline
for each date_pair:
    for each master:
        multi_look <date>.slc <date>.slc.par <date>.slc.mli <date>.slc.mli.par ml_range ml_az
# Return: multilook vom master <date>.slc.mli
# Return: multilook parameter file vom master <date>.slc.mli.par
 
```



## 3. Erstellung von Lookuptable

- Wichtig für das Hin und Her konvertieren zwischen Radar und Groundrange geometrien

```python
for each pair
    for each master_date
        gc_map <date>.slc.mli.par - dem.par dem eqa.dem.par eqa.dem <date>.lt 3 1 <master_date>.sim_sar

#Return
```

## 4 Geocode

```python
for each pair
    for each <date>.lt
        geocode <date>.lt eqa.dem <width of dem> <date_master>.hgt <cols of master.mli> <rows of master.mli> 2 0 
```

## 5 Coregistration

- ScanSAR_coreg.py

```python
for each pair
    # create tab-file for each referenced slave
    echo <slave_date*{.rscl, .rslc.par, rslc.TOPS.par}
    ScanSAR_coreg.py <master>.tab master.slc <slave>.tab slave.slc
    
```

```python

```

***

## 4. Offset (power & fringe visibility)
ACHTUNG: Iteration über Szenenpaare


### 3.1 Initialise Offsets (R)
_filename: offsetInitialisation.py_

**Umfasst folgende Funktionen:**
1. create_offsets
2. init_offsets_orbit

Needs to remove .off file in order to rerun process. By default, .off will be used as input and not overwritten

Reference und dependent SLC definition. 
- 1 = Intensity Tracking, 
- 2 = Fringe Visibility Tracking (Phase)

**Notes**

.off file wird geupdated während des gesamten Optimierungsprozesses.

***

### 3.2 offset_pwr / offset_SLC
_filename: offsetRefinement.py_

**Window size optimisation**

input: initiated .offs
output: write out .off, offs, ccp with optimised windows

parameters: window width & height, threshold

repeat offset_pwr & offset_fit -> result of offset_fit assessment of stdev (written to coffsets)

Window size optimisation



**How to call it in Gamma?**

- offset_pwr
- offset_fit

_similar for phase tracking_

**Notes**

- deramp flag?

***

### 3.3 offset_pwr_tracking / offset_SLC_tracking

Log: Azimuth lines werden angezeigt

**What does it?**

**How to call it in Gamma?**

**Notes**

***

### 4. Quality Assessment

1. Optimale Fenstergröße für offset-tracking
2. Jahreszeiten
3. Zeitlicher Verlauf der Gletscherbewegung
4. Vergleiche mit Mishas Paper

***

### 5. Visualisation

1. Displacement map
2. Change of displacement


