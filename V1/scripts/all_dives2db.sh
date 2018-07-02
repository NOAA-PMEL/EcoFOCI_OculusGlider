#!/bin/bash

#Fall 2017 Deployment
root_path="/home/pavlof/bell"
prog_dir="${root_path}/Programs/Python/EcoFOCI_ENGR_Testing/oer_glider/"

state_file="EcoFOCI_config/2017_sg401_south.yaml"

python ${prog_dir}oer_glider_dbload.py -ini ${state_file}


state_file="EcoFOCI_config/2017_sg401_north.yaml"

python ${prog_dir}oer_glider_dbload.py -ini ${state_file}


