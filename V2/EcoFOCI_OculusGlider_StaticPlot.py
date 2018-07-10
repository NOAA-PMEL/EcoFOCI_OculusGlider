#!/usr/bin/env python

"""
 Background:
 ===========
 EcoFOCI_OculusGlider_StaticPlot.py
 
 Purpose:
 ========
 Plot Data from Glider ERDDAP Server (which is the original netcdf data)

 Assumptions:
 ============
 + Glider and CTD use different (non-standard) variable names (thanks EPIC)

 History:
 ========
 + Forked from V1/oer_glider_plot.py

 Compatibility:
 ==============
 python >=3.6 

"""
import argparse
import datetime

from requests.exceptions import HTTPError
from erddapy import ERDDAP
import pandas as pd
import numpy as np

from io_utils import ConfigParserLocal
from plots.profile_plot import CTDProfilePlot

# Visual Stack
import matplotlib as mpl
import matplotlib.pyplot as plt

"""-------------------------------- Main -----------------------------------------------"""

def castdirection(df):
    """determin index of upcast and downcast - based on reaching max depth"""
    downcast = [0,df['ctd_depth'].values.argmax()+1]
    upcast = [df['ctd_depth'].values.argmax(),len(df['ctd_depth'])]

    return (downcast,upcast)

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


for inc_idnum in range(ConfigParams['divenum'],max_divenum,1):
  ### add desired profile constraint
  profile_idstr = 'p'+ConfigParams['sgid_num']+str(inc_idnum).zfill(4)

  print("Plotting: {profile}".format(profile=profile_idstr))

  dfs = {}
  for index,row in df.iterrows():
      if row['Dataset ID'] in alldata_sets:
          print(row['Dataset ID'])
          if row['Dataset ID'] in [ConfigParams['DataSetID_root']]:
              constraints_copy = constraints.copy()
              constraints_copy.update({'profileid=':profile_idstr})
          elif row['Dataset ID'] in [ConfigParams['DataSetID_root']+'_wetlabs']:
              constraints_copy = constraints.copy()
              constraints_copy.update({'profileid_wetlabs=':profile_idstr})
          elif row['Dataset ID'] in [ConfigParams['DataSetID_root']+'_aanderaa']:
              constraints_copy = constraints.copy()
              constraints_copy.update({'profileid_aand=':profile_idstr})
          else:
            print('Failed to modify profileid constraint')
            constraints_copy = constraints.copy()
            continue
          try:
              e = ERDDAP(server=ConfigParams['server_url'],
                  protocol='tabledap',
                  response='csv',
              )
              e.dataset_id=row['Dataset ID']
              e.constraints=constraints_copy
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

  GliderPlot = CTDProfilePlot()
  downInd,upInd = castdirection(dfs[ConfigParams['DataSetID_root']])
  Aand_downInd,Aand_upInd = castdirection(df_aan)
  WetLabs_downInd,WetLabs_upInd = castdirection(dfwet)

  ########## CTD
  ### temperature
  (plt, fig) = GliderPlot.plot1plot(epic_key=['T_28','T_28u','T2_35','T2_35u'],
                   xdata=[SBE_Temperature[downInd[0]:downInd[1]],SBE_Temperature[upInd[0]:upInd[1]],
                          Aand_Temp[Aand_downInd[0]:Aand_downInd[1]],Aand_Temp[Aand_upInd[0]:Aand_upInd[1]]],
                   ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]],
                          Aand_pressure[Aand_downInd[0]:Aand_downInd[1]],Aand_pressure[Aand_upInd[0]:Aand_upInd[1]]],
                   xlabel='Temperature (C)',
                   updown=['d','u','d','u'])

  ptitle = GliderPlot.add_title(cruiseid='',
                    fileid='erddap-dataset',
                    castid=profile_idstr,
                    castdate=data_time[0])

  t = fig.suptitle(ptitle)
  t.set_y(1.06)
  DefaultSize = fig.get_size_inches()
  fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

  plt.savefig('images/dive'+profile_idstr+'_temperature.png', bbox_inches='tight', dpi = (300))
  plt.close()

  ###salinity
  (plt, fig) = GliderPlot.plot1plot(epic_key=['S_41','S_41u'],
                   xdata=[SBE_Salinity[downInd[0]:downInd[1]],SBE_Salinity[upInd[0]:upInd[1]]],
                   ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                   xlabel='Salinity (PSU)',
                   updown=['d','u'])

  ptitle = GliderPlot.add_title(cruiseid='',
                    fileid='erddap-dataset',
                    castid=profile_idstr,
                    castdate=data_time[0])

  t = fig.suptitle(ptitle)
  t.set_y(1.06)
  DefaultSize = fig.get_size_inches()
  fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

  plt.savefig('images/dive'+profile_idstr+'_salinity.png', bbox_inches='tight', dpi = (300))
  plt.close()

  ##### optode
  ### conc
  (plt, fig) = GliderPlot.plot1plot(epic_key=['O_65','O_65u'],
                   xdata=[Aand_O2_corr[Aand_downInd[0]:Aand_downInd[1]],Aand_O2_corr[Aand_upInd[0]:Aand_upInd[1]]],
                   ydata=[Aand_pressure[Aand_downInd[0]:Aand_downInd[1]],Aand_pressure[Aand_upInd[0]:Aand_upInd[1]]],
                   xlabel='Oxygen Conc (ug/m^3 // ug/l)',
                   updown=['d','u'])

  ptitle = GliderPlot.add_title(cruiseid='',
                    fileid='erddap-dataset',
                    castid=profile_idstr,
                    castdate=data_time[0])

  t = fig.suptitle(ptitle)
  t.set_y(1.06)
  DefaultSize = fig.get_size_inches()
  fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

  plt.savefig('images/dive'+profile_idstr+'_O2Conc.png', bbox_inches='tight', dpi = (300))
  plt.close()

  ### PSat
  (plt, fig) = GliderPlot.plot1plot(epic_key=['OST_62','OST_62u'],
                   xdata=[Aand_DO_Sat[Aand_downInd[0]:Aand_downInd[1]],Aand_DO_Sat[Aand_upInd[0]:Aand_upInd[1]]],
                   ydata=[Aand_pressure[Aand_downInd[0]:Aand_downInd[1]],Aand_pressure[Aand_upInd[0]:Aand_upInd[1]]],
                   xlabel='Oxygen PSat (%)',
                   updown=['d','u'])

  ptitle = GliderPlot.add_title(cruiseid='',
                    fileid='erddap-dataset',
                    castid=profile_idstr,
                    castdate=data_time[0])

  t = fig.suptitle(ptitle)
  t.set_y(1.06)
  DefaultSize = fig.get_size_inches()
  fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

  plt.savefig('images/dive'+profile_idstr+'_O2Psat.png', bbox_inches='tight', dpi = (300))
  plt.close()


  ########## WetLabs
  ###chl
  (plt, fig) = GliderPlot.plot1plot(epic_key=['Chl_933','Chl_933u'],
                   xdata=[Wetlabs_CHL[WetLabs_downInd[0]:WetLabs_downInd[1]],Wetlabs_CHL[WetLabs_upInd[0]:WetLabs_upInd[1]]],
                   ydata=[Wetlabs_pressure[WetLabs_downInd[0]:WetLabs_downInd[1]],Wetlabs_pressure[WetLabs_upInd[0]:WetLabs_upInd[1]]],
                   xlabel='Chl (ug/l)',
                   updown=['d','u'])

  ptitle = GliderPlot.add_title(cruiseid='',
                    fileid='erddap-dataset',
                    castid=profile_idstr,
                    castdate=data_time[0])

  t = fig.suptitle(ptitle)
  t.set_y(1.06)
  DefaultSize = fig.get_size_inches()
  fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

  plt.savefig('images/dive'+profile_idstr+'_chl.png', bbox_inches='tight', dpi = (300))
  plt.close()

  ###cdom
  (plt, fig) = GliderPlot.plot1plot(epic_key=['CDOM_2980','CDOM_2980u'],
                   xdata=[Wetlabs_CDOM[WetLabs_downInd[0]:WetLabs_downInd[1]],Wetlabs_CDOM[WetLabs_upInd[0]:WetLabs_upInd[1]]],
                   ydata=[Wetlabs_pressure[WetLabs_downInd[0]:WetLabs_downInd[1]],Wetlabs_pressure[WetLabs_upInd[0]:WetLabs_upInd[1]]],
                   xlabel='CDOM (ppb)',
                   updown=['d','u'])

  ptitle = GliderPlot.add_title(cruiseid='',
                    fileid='erddap-dataset',
                    castid=profile_idstr,
                    castdate=data_time[0])

  t = fig.suptitle(ptitle)
  t.set_y(1.06)
  DefaultSize = fig.get_size_inches()
  fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

  plt.savefig('images/dive'+profile_idstr+'_cdom.png', bbox_inches='tight', dpi = (300))
  plt.close()

  ###turb
  (plt, fig) = GliderPlot.plot1plot(epic_key=['Trb_980','Trb_980u'],
                   xdata=[Wetlabs_NTU[WetLabs_downInd[0]:WetLabs_downInd[1]],Wetlabs_NTU[WetLabs_upInd[0]:WetLabs_upInd[1]]],
                   ydata=[Wetlabs_pressure[WetLabs_downInd[0]:WetLabs_downInd[1]],Wetlabs_pressure[WetLabs_upInd[0]:WetLabs_upInd[1]]],
                   xlabel='Turbidity (NTU)',
                   updown=['d','u'])

  ptitle = GliderPlot.add_title(cruiseid='',
                    fileid='erddap-dataset',
                    castid=profile_idstr,
                    castdate=data_time[0])

  t = fig.suptitle(ptitle)
  t.set_y(1.06)
  DefaultSize = fig.get_size_inches()
  fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

  plt.savefig('images/dive'+profile_idstr+'_turbidity.png', bbox_inches='tight', dpi = (300))
  plt.close()


  

### update config file
ConfigParams['divenum'] = inc_idnum 
ConfigParserLocal.write_config(args.config,ConfigParams,'yaml')

