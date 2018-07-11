#!/usr/bin/env python

"""
 Background:
 ===========
 EcoFOCI_OculusGlider_XSectionPlot.py
 
 Purpose:
 ========
 Plot Data from Glider ERDDAP Server (which is the original netcdf data)

 Assumptions:
 ============
 + Glider and CTD use different (non-standard) variable names (thanks EPIC)

 History:
 ========


 Compatibility:
 ==============
 python >=3.6 

"""
import argparse
import datetime
import os

from requests.exceptions import HTTPError
from erddapy import ERDDAP
import pandas as pd
import numpy as np

from io_utils import ConfigParserLocal

# Visual Stack
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import cmocean

"""-------------------------------- Subroutines-----------------------------------------"""

def plot_params(df, var=None,varstr='',cmap=cmocean.cm.thermal,vmin=None,vmax=None):
    fig, ax = plt.subplots(figsize=(17, 2))
    if vmin:
        cs = ax.scatter(df.index, df['ctd_depth'], s=15, c=df[var], marker='o', 
                        edgecolor='none',cmap=cmap,vmin=vmin,vmax=vmax)
    else:
        cs = ax.scatter(df.index, df['ctd_depth'], s=15, c=df[var], marker='o', 
                        edgecolor='none',cmap=cmap)
        
    ax.invert_yaxis()
    ax.set_xlim(df.index[0], df.index[-1])
    xfmt = mdates.DateFormatter('%d-%b\n%H:%M')
    ax.xaxis.set_major_formatter(xfmt)

    cbar = fig.colorbar(cs, orientation='vertical', extend='both')
    cbar.ax.set_ylabel(varstr)
    ax.set_ylabel('Depth (m)')

    return (fig,ax)

"""-------------------------------- Main -----------------------------------------------"""

parser = argparse.ArgumentParser(description='Plot Oculus Glider Data from ERDDAP')
parser.add_argument('-sg_id','--sg_id', type=str,
      default='403',
      help='seaglider id')
parser.add_argument('-dn','--divenum', type=str,
      default='1',
      help='dive number')
parser.add_argument("-s",'--ServerName', type=str,
      default="http://downdraft.pmel.noaa.gov",
      help='server name, eg. http://downdraft.pmel.noaa.gov')
parser.add_argument("-id",'--DataSetID', type=str,
      default="sg403_PS_spring18",
      help='rootbase of the erddap dataset id')
parser.add_argument("-config",'--config', type=str,
      default="config/config.yaml",
      help='configuration file')
args = parser.parse_args()



#######################
#
# Data Ingest and Processing


if args.config:
  ConfigParams = ConfigParserLocal.get_config(args.config,'yaml')
else:
  ConfigParams = {}
  ConfigParams['sgid_num'] = args.sg_id
  ConfigParams['sgid_string'] = 'sg' + ConfigParams['sgid_num']
  ConfigParams['server_url'] = args.ServerName+':8080/erddap'
  ConfigParams['DataSetID_root'] = args.DataSetID
  ConfigParams['divenum'] = args.divenum

e = ERDDAP(server=ConfigParams['server_url'])
df = pd.read_csv(e.get_search_url(response='csv', search_for=ConfigParams['sgid_string']))
alldata_sets = df['Dataset ID'].values

### ofload constraints to yaml file
constraints = {
    'time>=': '2018-01-01T00:00:00Z',
    'time<=': str(datetime.datetime.today()),
}

variables = {ConfigParams['DataSetID_root']:['profileid',
             'latitude', 
             'ctd_depth', 
             'longitude', 
             'salinity',
             'density', 
             'time', 
             'temperature'],
             ConfigParams['DataSetID_root']+'_wetlabs':['time',
             'wlbb2fl_sig695nm_adjusted',
             'wlbb2fl_sig470nm_adjusted', 
             'wlbb2fl_sig700nm_adjusted', 
             'wlbb2fl_temp',
             'profileid_wetlabs'],
             ConfigParams['DataSetID_root']+'_aanderaa':['time',
             'aanderaa4330_dissolved_oxygen',
             'aa4330_airsat',
             'aa4330_temp',
             'profileid_aand']}


### Get total number of profiles
try:
    e = ERDDAP(server=ConfigParams['server_url'],
        protocol='tabledap',
        response='csv',
    )
    e.dataset_id=ConfigParams['DataSetID_root']
    e.variables=['profileid']
except HTTPError:
    print('Failed to generate url {}'.format(row['Dataset ID']))
dfp = e.to_pandas(
            skiprows=(1,)  # units information can be dropped.
            )

max_divenum = int(dfp.tail(1)['profileid'].values[0].split('p'+ConfigParams['sgid_num'])[-1])



dfs = {}
for index,row in df.iterrows():
    if row['Dataset ID'] in alldata_sets:
        print(row['Dataset ID'])
        try:
            e = ERDDAP(server=ConfigParams['server_url'],
                protocol='tabledap',
                response='csv',
            )
            e.dataset_id=row['Dataset ID']
            e.constraints=constraints
            e.variables=variables[row['Dataset ID']]
        except HTTPError:
            print('Failed to generate url {}'.format(row['Dataset ID']))
            continue
        dfs.update({row['Dataset ID']: e.to_pandas(
                                index_col='time',
                                parse_dates=True,
                                skiprows=(1,)  # units information can be dropped.
                                )})
    

#rename data variables for consistency
data_time = dfs[ConfigParams['DataSetID_root']].index
pressure = dfs[ConfigParams['DataSetID_root']]['ctd_depth']
SBE_Temperature = dfs[ConfigParams['DataSetID_root']]['temperature']
SBE_Salinity = dfs[ConfigParams['DataSetID_root']]['salinity']

#map eco to ctd depths
dfwet = dfs[ConfigParams['DataSetID_root']+'_wetlabs'].join(dfs[ConfigParams['DataSetID_root']])
Wetlabs_CDOM = dfwet['wlbb2fl_sig470nm_adjusted']
Wetlabs_CHL  = dfwet['wlbb2fl_sig695nm_adjusted']
Wetlabs_NTU  = dfwet['wlbb2fl_sig700nm_adjusted']
Wetlabs_pressure = dfwet['ctd_depth']

# map aanderaa to ctd depths
df_aan = dfs[ConfigParams['DataSetID_root']+'_aanderaa'].join(dfs[ConfigParams['DataSetID_root']])
Aand_O2_corr = df_aan['aanderaa4330_dissolved_oxygen']
Aand_DO_Sat = df_aan['aa4330_airsat']
Aand_Temp = df_aan['aa4330_temp']
Aand_pressure = df_aan['ctd_depth']

#######################
#
# Plots


image_directory = 'images/xsections/'
if not os.path.exists(image_directory):
    os.makedirs(image_directory)

########## CTD
### temperature
(fig,ax) = plot_params(dfs['sg403_PS_spring18'], 'temperature','Temperature (DegC)')
plt.savefig(image_directory + ConfigParams['sgid_string'] +'_temperature.png', bbox_inches='tight', dpi = (300))
plt.close()

### salinity
(fig,ax) = plot_params(dfs['sg403_PS_spring18'], 'salinity','Salinity (PSU)',cmocean.cm.haline)
plt.savefig(image_directory + ConfigParams['sgid_string'] +'_salinity.png', bbox_inches='tight', dpi = (300))
plt.close()  

### density
plot_params(dfs['sg403_PS_spring18'], 'density','Density',cmocean.cm.dense)
plt.savefig(image_directory + ConfigParams['sgid_string'] +'_density.png', bbox_inches='tight', dpi = (300))
plt.close()  

### chlor-a
plot_params(dfwet, 'wlbb2fl_sig695nm_adjusted','Chlor mg/m3',cmocean.cm.algae)
plt.savefig(image_directory + ConfigParams['sgid_string'] +'_chlora.png', bbox_inches='tight', dpi = (300))
plt.close()  

### Oxy Sat
plot_params(df_aan, 'aa4330_airsat','Oxy Sat (%)',cmocean.cm.oxy,vmin=80,vmax=100)
plt.savefig(image_directory + ConfigParams['sgid_string'] +'_do_sat.png', bbox_inches='tight', dpi = (300))
plt.close()  




