# NOTES

# 22.10.2020
- Die Namensgebung muss so bleiben: 
    ##**`<yyyymmdd>_pol_sw_<file_ending>`**
   
- Irgendwas passte mit dem DEM nicht. Die "Pointer" in dem VRT haben zu TIFFs gezeigt, die es irgendwie nicht gab
- Ich habe erst beide TIFs reprojeziert und dann ein VRT neu erstellt
- **Die Benennung ist das Wichtigste von allem!!**
- Müssen wir dieses EQA.dem und EQA.dem_par in jeder Iteration von `gc_map` für das Masterbild neu berechnen?
- Wir haben gerade zwei Funktionen `rec_reg` und `get_files`, die beide irgendwie eine Liste an Datein basierend auf einem 
Pattern zurückgeben. Da sollten wir uns auf eine einigen
    + Wobei `get_files` insofern nützlich ist, da die Möglichkeit hat, bei unserer Namensgebung **`<yyyymmdd>_pol_sw_<file_ending>`**,
    zwischen den Main-und secondary images zu unterscheiden
    + `rec_reg` gibt einfach, basierend auf einer kleinen regular expression eine liste mit allen matchenden datein zurück
- `awkpy` sollte nützlich sein um die Breiten und Höhen aus einem textfile extrahieren zu können
- Die Ordnerstruktur vielleicht nochmal ändern zu: 

```
data
| DEM
| SLC
| tuples
    | date1_date2
        | intensity
        | phase
    | date1_date2
        | intensity
        | phase
```

Dies ist vielleicht ganz clever, da einige Datein wie die Koregistrierungsqualität für beide Schritte (Pwr und Fringe-Visibility) 
relevant sind und so in den überordner date1_date2 gelegt werden können

- Was sind die SLC1_ID und SLC2_ID Paramterter in `ScanSAR_coreg.py` und auf welche directories sollen die sich beziehen?

        