#!/bin/bash

# Purpose:

data_dir="/Users/bell/ecoraid/2017/Profilers/OculusGliders/bering_sea_fall17/sg401/*.nc"
prog_dir="/Users/bell/Programs/Python/EcoFOCI_OculusGlider/"
orig_files="/Users/bell/ecoraid/2017/Profilers/OculusGliders/bering_sea_fall17/sg401/"
processed_files="/Users/bell/Programs/Python/EcoFOCI_OculusGlider/data/1p0_dtdz/"

for files in $data_dir
do
    outfile=$(basename "$files" ".nc")
    #echo "processing file: $files as $outfile"

    python ${prog_dir}GliderScienceSet_Analysis.py ${orig_files} ${processed_files} ${outfile}
done

