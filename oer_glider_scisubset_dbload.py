#!/usr/bin/env python

"""
 Background:
 --------
 oer_glider_dbload.py
 
 
 Purpose:
 --------
 load glider netcdf data into mysql database

 History:
 --------


"""
import argparse, os

from io_utils import ConfigParserLocal
import numpy as np

import calc.aanderaa_corrO2_sal as optode_O2_corr
from plots.profile_plot import CTDProfilePlot
import io_utils.EcoFOCI_netCDF_read as eFOCI_ncread
from io_utils.EcoFOCI_db_io import EcoFOCI_db_oculus

# Visual Stack
import matplotlib as mpl
import matplotlib.pyplot as plt


def nan2none(var):
    return np.where(np.isnan(var), None, var)
"""-------------------------------- Main -----------------------------------------------"""

parser = argparse.ArgumentParser(description='Load Glider NetCDF data into MySQL database')
parser.add_argument('-ini','--ini_file', type=str,
               help='complete path to yaml instrument ini (state) file')
args = parser.parse_args()



#######################
#
# Data Ingest and Processing
state_config = ConfigParserLocal.get_config(args.ini_file,ftype='yaml')
ncfile_list = [state_config['base_id'] + str(item).zfill(4) for item in range(state_config['startnum'],state_config['endnum'],1)]

for fid in ncfile_list:
  diveNum = fid.split(state_config['base_id'])[-1]
  filein = state_config['path'] + fid + '.nc'

  print("Working on file {file}".format(file=filein))

  try:
    df = eFOCI_ncread.EcoFOCI_netCDF(file_name=filein)
    vars_dic = df.get_vars()
    ncdata = df.ncreadfile_dic()
    data_time = df.epochtime2date('time')
    df.close()
  except:
    print("Missing file: {file}".format(file=filein))
    continue

  try:
    pressure = ncdata['Pressure']
    SBE_Temperature = ncdata['Temperature']
    SBE_Salinity = ncdata['Salinity']

    lat = ncdata['latitude']
    lon = ncdata['longitude']
  except KeyError:
    print("Missing Primary Variable:.  Skipping dive")
    continue

  SBE_Salinity = nan2none(SBE_Salinity)
  

  ###
  #
  # load database
  config_file = 'EcoFOCI_config/db_config/db_config_oculus_local.pyini'
  EcoFOCI_db = EcoFOCI_db_oculus()
  (db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file,ftype='json')

  db_table = state_config['db_table']
  result = EcoFOCI_db.divenum_check(table=db_table,divenum=diveNum)

  if not result:
    print("{divenum} is being added to database".format(divenum=diveNum))
    for i,depth in enumerate(pressure):
      EcoFOCI_db.add_to_DB(table=db_table,time=data_time, salinity=SBE_Salinity[i],
      latitude=float(lat),longitude=float(lon),pressure=depth,temperature=SBE_Temperature[i],divenum=diveNum)

  EcoFOCI_db.close()