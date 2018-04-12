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


def castdirection(depth):
    """determin index of upcast and downcast"""
    downcast = [0,np.argmax(depth)+1]
    upcast = [np.argmax(depth)+1,len(depth)]

    return (downcast,upcast)
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
    data_time = df.epochtime2date()
    df.close()
  except:
    print("Missing file: {file}".format(file=filein))
    continue

  try:
    ncdata['ctd_time'] #passes error if no parameter exists
    pressure = ncdata['ctd_pressure']
    SBE_Temperature = ncdata['temperature']
    SBE_Temperature_raw = ncdata['temperature_raw']
    SBE_Salinity = ncdata['salinity']
    SBE_Salinity_qc = ncdata['salinity_qc']

    SBE_Conductivity_raw = ncdata['conductivity_raw']

    SBE_Salinity_raw = ncdata['salinity_raw']
    SBE_Salinity_raw_qc = ncdata['salinity_raw_qc']

    density_insitu = ncdata['density_insitu']
    sigma_t = ncdata['sigma_t']

    Wetlabs_CDOM = ncdata['wlbb2fl_sig470nm_adjusted']
    if Wetlabs_CDOM is np.ma.masked:
      Wetlabs_CDOM = Wetlabs_CDOM.data
    Wetlabs_CHL  = ncdata['wlbb2fl_sig695nm_adjusted']
    if Wetlabs_CHL is np.ma.masked:
      Wetlabs_CHL = Wetlabs_CHL.data
    Wetlabs_NTU  = ncdata['wlbb2fl_sig700nm_adjusted']
    if Wetlabs_NTU is np.ma.masked:
      Wetlabs_NTU = Wetlabs_NTU.data

    Aand_Temp = ncdata['eng_aa4330_Temp']
    Aand_O2_corr = ncdata['aanderaa4330_dissolved_oxygen'].data
    Aand_DO_Sat  = ncdata['eng_aa4330_AirSat']
    Aand_DO_Sat_calc = optode_O2_corr.O2PercentSat(oxygen_conc=Aand_O2_corr, 
                                         salinity=SBE_Salinity,
                                         temperature=SBE_Temperature,
                                         pressure=pressure)  

    PAR_satu = ncdata['eng_satu_PARuV'] 
    PAR_satd = ncdata['eng_satd_PARuV'] 

    lat = ncdata['latitude']
    lon = ncdata['longitude']
    speed_gsm = ncdata['speed_gsm']
    vert_speed_gsm = ncdata['vert_speed_gsm']
    horz_speed_gsm = ncdata['horz_speed_gsm']
  except KeyError:
    print("Missing Primary Variable:.  Skipping dive")
    continue

  downInd,upInd = castdirection(pressure)
  castdir = np.chararray((np.shape(pressure)[0]+1))
  castdir[downInd[0]:downInd[1]] = 'd'
  castdir[upInd[0]:upInd[1]] = 'u'

  SBE_Salinity = nan2none(SBE_Salinity)
  SBE_Conductivity_raw = nan2none(SBE_Conductivity_raw)
  SBE_Temperature_raw = nan2none(SBE_Temperature_raw)
  PAR_satu = nan2none(PAR_satu)
  PAR_satd = nan2none(PAR_satd)
  Aand_O2_corr = nan2none(Aand_O2_corr)
  Aand_DO_Sat = np.where(Aand_DO_Sat<0, np.nan, Aand_DO_Sat)
  Aand_DO_Sat = np.where(Aand_DO_Sat>200, np.nan, Aand_DO_Sat)
  Aand_DO_Sat = nan2none(Aand_DO_Sat)
  Wetlabs_CDOM = nan2none(Wetlabs_CDOM)
  Wetlabs_CHL = nan2none(Wetlabs_CHL)
  Wetlabs_NTU = nan2none(Wetlabs_NTU)
  density_insitu = nan2none(density_insitu)
  sigma_t = nan2none(sigma_t)
  speed_gsm = nan2none(speed_gsm)
  vert_speed_gsm = nan2none(vert_speed_gsm)
  horz_speed_gsm = nan2none(horz_speed_gsm)

  ###
  #
  # load database
  config_file = 'EcoFOCI_config/db_config/db_config_oculus_root.pyini'
  EcoFOCI_db = EcoFOCI_db_oculus()
  (db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file,ftype='json')

  db_table = state_config['db_table']
  result = EcoFOCI_db.divenum_check(table=db_table,divenum=diveNum)

  if not result:
    print("{divenum} is being added to database".format(divenum=diveNum))
    for i,inst_time in enumerate(data_time):
      if (pressure[i] < 0):
        EcoFOCI_db.add_to_DB(table=db_table,divenum=diveNum,time=data_time[i], salinity_qc=SBE_Salinity_qc[i],
        latitude=lat[i],longitude=lon[i],depth=pressure[i],castdirection='sfc',temperature=SBE_Temperature[i],temperature_raw=SBE_Temperature_raw[i],
        speed_gsm=speed_gsm[i],vert_speed_gsm=vert_speed_gsm[i],horz_speed_gsm=horz_speed_gsm[i])
      else:
        EcoFOCI_db.add_to_DB(table=db_table,divenum=diveNum,time=data_time[i], salinity_qc=SBE_Salinity_qc[i],
        latitude=lat[i],longitude=lon[i],depth=pressure[i],castdirection=castdir[i], conductivity_raw=SBE_Conductivity_raw[i],
        salinity=SBE_Salinity[i],salinity_raw=SBE_Salinity_raw[i],temperature=SBE_Temperature[i],temperature_raw=SBE_Temperature_raw[i],
        sigma_t=sigma_t[i], do_sat=Aand_DO_Sat[i],do_conc=Aand_O2_corr[i],
        sig470nm=Wetlabs_CDOM[i],sig695nm=Wetlabs_CHL[i],sig700nm=Wetlabs_NTU[i],
        up_par=PAR_satu[i],down_par=PAR_satd[i],density_insitu=density_insitu[i],
        speed_gsm=speed_gsm[i],vert_speed_gsm=vert_speed_gsm[i],horz_speed_gsm=horz_speed_gsm[i])

  EcoFOCI_db.close()