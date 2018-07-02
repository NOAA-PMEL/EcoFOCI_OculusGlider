#!/bin/bash

#Fall 2017 Deployment
#root_path="/home/pavlof/bell"
root_path="/Volumes/WDC_internal/Users/bell"
prog_dir="${root_path}/Programs/Python/EcoFOCI_ENGR_Testing/oer_glider/"

state_file="EcoFOCI_config/2017_sg401_south.yaml"

python ${prog_dir}oer_glider_ncplot.py -ini ${state_file}
#python ${prog_dir}oer_glider_dbplot.py -ini ${state_file}
