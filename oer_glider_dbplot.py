#!/usr/bin/env python

"""
 Background:
 --------
 oer_glider_dbplot.py
 
 
 Purpose:
 --------
 
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
    downcast = [0,np.argmax(np.diff(depth)<0)+1]
    upcast = [np.argmax(np.diff(depth)<0),len(depth)]

    return (downcast,upcast)

"""-------------------------------- Main -----------------------------------------------"""

parser = argparse.ArgumentParser(description='Plot archived db glider data')
parser.add_argument('-ini','--ini_file', type=str,
               help='complete path to yaml instrument ini (state) file')
args = parser.parse_args()



#######################
#
# Data Ingest and Processing
state_config = ConfigParserLocal.get_config(args.ini_file,ftype='yaml')
#get information from local config file - a json formatted file
config_file = 'EcoFOCI_config/db_config/db_config_oculus.pyini'
db_table = '2017_fall_sg401_southward'
db_table2 = '2017_fall_sg401_northward'

EcoFOCI_db = EcoFOCI_db_oculus()
(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)

ncfile_list = [state_config['base_id'] + str(item).zfill(4) for item in range(state_config['startnum'],state_config['endnum'],1)]

for fid in ncfile_list:
  diveNum = fid
  filein = state_config['path'] + fid + '.nc'

  print("Working on diveNum {file}".format(file=diveNum))

  try:
    df = eFOCI_ncread.EcoFOCI_netCDF(file_name=filein)
    vars_dic = df.get_vars()
    ncdata = df.ncreadfile_dic()
    data_time = df.epochtime2date()
    df.close()
  except IOError:
    continue

  try:
    pressure = ncdata['ctd_pressure']
    SBE_Temperature = ncdata['temperature']
    SBE_Temperature[SBE_Temperature > 20] = np.nan
    SBE_Salinity = ncdata['salinity']
    SBE_Salinity[SBE_Salinity < 28] = np.nan
    SBE_Salinity_raw = ncdata['salinity_raw']
    SBE_Salinity_raw[SBE_Salinity_raw < 28] = np.nan

    lat = ncdata['log_gps_lat'][0]
    lon = ncdata['log_gps_lon'][0]
  except KeyError:
    continue

  dbData = EcoFOCI_db.read_profile(table=db_table2, 
                    divenum=int(diveNum.split('p401')[-1]), 
                    castdirection='', 
                    param='TwoLayer_merged_temp,TwoLayer_merged_sal',
                    verbose=True,
                    result_index='id')

  GliderPlot = CTDProfilePlot()
  downInd,upInd = castdirection(pressure)

  if not os.path.exists('images/dive' + diveNum ):
      os.makedirs('images/dive' + diveNum)

  ########## CTD
  ### temperature
  (plt, fig) = GliderPlot.plot1plot_CTD(epic_key=['T_28','T_28u','T2_35'],
                   xdata=[SBE_Temperature[downInd[0]:downInd[1]],SBE_Temperature[upInd[0]:upInd[1]],
                          np.array([dbData[x]['TwoLayer_merged_temp'] for x in dbData.keys()])],
                   ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]],np.array([dbData[x]['depth'] for x in dbData.keys()])],
                   xlabel='Temperature (C)',
                   updown=['d','u',''],
                   maxdepth=np.max(pressure))

  ptitle = GliderPlot.add_title(cruiseid='',
                    fileid=filein.split('/')[-1],
                    castid=diveNum,
                    castdate=data_time[0],
                    lat=lat,
                    lon=lon)

  t = fig.suptitle(ptitle)
  t.set_y(1.06)
  DefaultSize = fig.get_size_inches()
  fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

  plt.savefig('images/dive'+diveNum+'/dive'+diveNum+'_temperature.png', bbox_inches='tight', dpi = (300))
  plt.close()

  ###salinity
  (plt, fig) = GliderPlot.plot1plot_CTD(epic_key=['S_41','S_41u','S_42'],
                   xdata=[SBE_Salinity_raw[downInd[0]:downInd[1]],SBE_Salinity_raw[upInd[0]:upInd[1]],
                          np.array([dbData[x]['TwoLayer_merged_sal'] for x in dbData.keys()])],
                   ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]],np.array([dbData[x]['depth'] for x in dbData.keys()])],
                   xlabel='Salinity (PSU)',
                   updown=['d','u',''],
                   maxdepth=np.max(pressure))

  ptitle = GliderPlot.add_title(cruiseid='',
                    fileid=filein.split('/')[-1],
                    castid=diveNum,
                    castdate=data_time[0],
                    lat=lat,
                    lon=lon)

  t = fig.suptitle(ptitle)
  t.set_y(1.06)
  DefaultSize = fig.get_size_inches()
  fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

  plt.savefig('images/dive'+diveNum+'/dive'+diveNum+'_salinity.png', bbox_inches='tight', dpi = (300))
  plt.close()