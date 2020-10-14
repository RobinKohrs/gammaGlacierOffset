
This repo will contain the code for performing the offset tracking with gamma


# Flowchart

Dieses Flussdiagramm enthält die notwendigen Schritte, um von Level-1 Sentinel-1 SLC Daten Offset-Tracking von
Gletschern durchzuführen. Es ist unterteilt sich in (0) die Erstellung einer kohärenten Ordnerstruktur, (1) den 
Import der SLCs und des isländischen National-DEM in ein GAMMA-kompatibles Format, (2) das debursten des Subswaths
IW2, welcher ausschließlich für unsere Prozessierung notwendig ist und (3) das Offset-Tracking, welches mehrere
Sub-Routinen enthält. Zuletzt bewerten wir den Optimierungsprozess der Tracking-Window-Größe und visualisieren 
unsere Ergebnisse (4, 5).

## 0. Create Folder Structure
_filename: makeFolderStructure.py_

## 1. SLC and DEM Import
_filename: import_data2gamma.py_


**What does it?**

Iteration über jede Szene. Main() enthält eine Loop, um über alle Szene zu iterieren.
- Nur IW2 (dort liegt der Gletscher)

**How to call it in Gamma?**

**Notes**
 

## 2. Mosaic
_filename: mosaicTOPS.py_

**What does it?**

Iteration über jede Szene.

SLC_mosaic_S1_TOPS nur IW2
input: Table with slc - slc.par - slc.tops.par parameters
output: debursted & mosaicked

multi_look
input:
output:

**How to call it in Gamma?**

**Notes**


## 3. Offset (power & fringe visibility)
_filename: .py_

Iteration nur Szenenpaare

### 3.1 create_offsets

Remove .off file

Reference und dependent SLC definition. 1 = Intensity Tracking, 2 = Fringe Visibility Tracking (Phase)

.off file wird geupdated während des gesamten Optimierungsprozesses

**What does it?**

**How to call it in Gamma?**

**Notes**

### 3.2 init_offsets_orbit (and init_offsets)
_filename: offsetInitialisation.py_

**What does it?**

**How to call it in Gamma?**

**Notes**

### 3.3 offset_pwr / offset_SLC
_filename: offsetRefinement.py_

**Window size optimisation**

input: initiated .offs
output: write out .off, offs, ccp with optimised windows

parameters: window width & height, threshold

repeat offset_pwr & offset_fit -> result of offset_fit assessment of stdev (written to coffsets)

Window size optimisation



**What does it?**

**How to call it in Gamma?**

- offset_pwr
- offset_fit

_similar for phase tracking_

**Notes**

- deramp flag?


### 3.3 offset_pwr_tracking / offset_SLC_tracking

Log: Azimuth lines werden angezeigt

**What does it?**

**How to call it in Gamma?**

**Notes**

### 4. Quality Assessment

1. Optimale Fenstergröße für offset-tracking
2. Jahreszeiten
3. Zeitlicher Verlauf der Gletscherbewegung
4. Vergleiche mit Mishas Paper

### 5. Visualisation

1. Displacement map
2. Change of displacement


