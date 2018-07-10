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

from erddapy import ERDDAP

from io_utils import ConfigParserLocal

import calc.aanderaa_corrO2_sal as optode_O2_corr
from plots.profile_plot import CTDProfilePlot
import io_utils.glider_functions as glider

# Visual Stack
import matplotlib as mpl
import matplotlib.pyplot as plt

"""-------------------------------- Main -----------------------------------------------"""

def castdirection(df):
    """determin index of upcast and downcast - based on reaching max depth"""
    downcast = [0,np.argmax(df['ctd_depth'])+1]
    upcast = [np.argmax(df['ctd_depth']),len(df['ctd_depth'])]

    return (downcast,upcast)

"""-------------------------------- Main -----------------------------------------------"""

parser = argparse.ArgumentParser(description='Plot Oculus Glider Data from ERDDAP')
parser.add_argument('sg_id', metavar='sg_id', 
      type=str,
      help='seaglider id')
parser.add_argument('divenum', metavar='divenum', 
      type=str,
      help='dive number')
parser.add_argument("-s",'--ServerName', type=str,
      default="http://downdraft.pmel.noaa.gov",
      help='server name, eg. http://downdraft.pmel.noaa.gov')
args = parser.parse_args()



#######################
#
# Data Ingest and Processing

server_url = args.ServerName+':8080/erddap'

e = ERDDAP(server=server_url)

df = pd.read_csv(e.get_search_url(response='csv', search_for='sg403'))

sg403 = df['Dataset ID'].values

constraints = {
    'time>=': '2018-01-01T00:00:00Z',
    'time<=': str(datetime.datetime.today()),
}

variables = {'sg403_PS_spring18':['profileid',
             'latitude', 
             'ctd_depth', 
             'longitude', 
             'salinity',
             'density', 
             'time', 
             'temperature'],
             'sg403_PS_spring18_wetlabs':['time',
             'wlbb2fl_sig695nm_adjusted',
             'wlbb2fl_sig470nm_adjusted', 
             'wlbb2fl_sig700nm_adjusted', 
             'wlbb2fl_temp',
             'profileid_wetlabs'],
             'sg403_PS_spring18_aanderaa':['time',
             'aanderaa4330_dissolved_oxygen',
             'aa4330_airsat',
             'aa4330_temp',
             'profileid_aand']}


from requests.exceptions import HTTPError

### add desired profile constraint
# TODO - flag for reprocessing all?
profile_idstr = 'p'+args.sg_id+(args.divenum).zfill(4)


dfs = {}
for index,row in df.iterrows():
    if row['Dataset ID'] in sg403:
        print(row['Dataset ID'])
        if row['Dataset ID'] in ['sg403_PS_spring18']:
            constraints_copy = constraints.copy()
            constraints_copy.update({'profileid=':profile_idstr})
        elif row['Dataset ID'] in ['sg403_PS_spring18_wetlabs']:
            constraints_copy = constraints.copy()
            constraints_copy.update({'profileid_wetlabs=':profile_idstr})
        elif row['Dataset ID'] in ['sg403_PS_spring18_aanderaa']:
            constraints_copy = constraints.copy()
            constraints_copy.update({'profileid_aand=':profile_idstr})
        else:
          print('Failed to modify profileid constraint')
          constraints_copy = constraints.copy()
          continue
        try:
            e = ERDDAP(server=server_url,
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
    

############ UPdate ############
rawdata, data_obj = glider.get_inst_data(filein, MooringID='oculus_test')

data_time = dfs['sg403_PS_spring18']['time']

pressure = dfs['sg403_PS_spring18']['ctd_depth']

SBE_Temperature = dfs['sg403_PS_spring18']['temperature']

SBE_Salinity = dfs['sg403_PS_spring18']['salinity']

#map eco to ctd depths
dfwet = dfs['sg403_PS_spring18_wetlabs'].join(dfs['sg403_PS_spring18'])
Wetlabs_CDOM = dfwet['wlbb2fl_sig470nm_adjusted']
Wetlabs_CHL  = dfwet['wlbb2fl_sig695nm_adjusted']
Wetlabs_NTU  = dfwet['wlbb2fl_sig700nm_adjusted']

# map aanderaa to ctd depths
df_aan = dfs['sg403_PS_spring18_aanderaa'].join(dfs['sg403_PS_spring18'])
Aand_O2_corr = df_aan['aanderaa4330_dissolved_oxygen']
          
Aand_DO_Sat = df_aan['aa4330_airsat']
          
############ UPdate ############


#######################
#
# Plots

GliderPlot = CTDProfilePlot()
downInd,upInd = castdirection(dfs['sg403_PS_spring18'])

########## CTD
### temperature
(plt, fig) = GliderPlot.plot1plot(epic_key=['T_28','T_28u','T2_35','T2_35u'],
                 xdata=[SBE_Temperature[downInd[0]:downInd[1]],SBE_Temperature[upInd[0]:upInd[1]],
                        rawdata['aa4330.Temp'][downInd[0]:downInd[1]],rawdata['aa4330.Temp'][upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
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

"""
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
(plt, fig) = GliderPlot.plot1plot(epic_key=['OST_62','OST_62u','CTDOST_4220','CTDOST_4220u'],
                 xdata=[Aand_DO[downInd[0]:downInd[1]],Aand_DO[upInd[0]:upInd[1]],
                        rawdata['aa4330.O2'][downInd[0]:downInd[1]],rawdata['aa4330.O2'][upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                 xlabel='Oxygen Conc (ug/m^3 // ug/l)',
                 updown=['d','u','d','u'])

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
(plt, fig) = GliderPlot.plot1plot(epic_key=['O_65','O_65u','CTDOXY_4221','CTDOXY_4221u'],
                 xdata=[Aand_DO_Sat[downInd[0]:downInd[1]],Aand_DO_Sat[upInd[0]:upInd[1]],
                        rawdata['aa4330.AirSat'][downInd[0]:downInd[1]],rawdata['aa4330.AirSat'][upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                 xlabel='Oxygen PSat (%)',
                 updown=['d','u','d','u'])

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

########## PAR
### Up/Down Welling
(plt, fig) = GliderPlot.plot1plot(epic_key=['PAR_905','PAR_905u','PAR_917','PAR_917u'],
                 xdata=[rawdata['satu.PARuV'][downInd[0]:downInd[1]],rawdata['satu.PARuV'][upInd[0]:upInd[1]],
                        rawdata['satd.PARuV'][downInd[0]:downInd[1]],rawdata['satd.PARuV'][upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                 xlabel='PAR (uE m-2 s) (darker is upward looking, lighter is downard looking) ',
                 updown=['d','u','d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid='erddap-dataset',
                  castid=profile_idstr,
                  castdate=data_time[0])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

plt.savefig('images/dive'+profile_idstr+'_PAR.png', bbox_inches='tight', dpi = (300))
plt.close()

########## WetLabs
###chl
(plt, fig) = GliderPlot.plot1plot(epic_key=['Chl_933','Chl_933u'],
                 xdata=[Wetlabs_CHL[downInd[0]:downInd[1]],Wetlabs_CHL[upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
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
                 xdata=[Wetlabs_CDOM[downInd[0]:downInd[1]],Wetlabs_CDOM[upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
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
                 xdata=[Wetlabs_NTU[downInd[0]:downInd[1]],Wetlabs_NTU[upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
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


## plot postion parameters as function of time
(plt, fig) = GliderPlot.plot1plot(epic_key=['P_1','P_1u'],
                 xdata=[rawdata['elaps_t'][downInd[0]:downInd[1]],rawdata['elaps_t'][upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                 xlabel='Elapsed Time',
                 updown=['d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid='erddap-dataset',
                  castid=profile_idstr,
                  castdate=data_time[0])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )

plt.savefig('images/dive'+profile_idstr+'_depthvtime.png', bbox_inches='tight', dpi = (300))
plt.close()

###
(plt, fig) = GliderPlot.plot1plot(epic_key=['pitch','pitch_u'],
                 xdata=[rawdata['elaps_t'][downInd[0]:downInd[1]],rawdata['elaps_t'][upInd[0]:upInd[1]]],
                 ydata=[rawdata['pitchAng'][downInd[0]:downInd[1]],rawdata['pitchAng'][upInd[0]:upInd[1]]],
                 xlabel='Elapsed Time',
                 ylabel='',
                 updown=['d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid='erddap-dataset',
                  castid=profile_idstr,
                  castdate=data_time[0])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )

plt.savefig('images/dive'+profile_idstr+'_pitchvtime.png', bbox_inches='tight', dpi = (300))
plt.close()

###
(plt, fig) = GliderPlot.plot1plot(epic_key=['roll','roll_u'],
                 xdata=[rawdata['elaps_t'][downInd[0]:downInd[1]],rawdata['elaps_t'][upInd[0]:upInd[1]]],
                 ydata=[rawdata['rollAng'][downInd[0]:downInd[1]],rawdata['rollAng'][upInd[0]:upInd[1]]],
                 xlabel='Elapsed Time',
                 ylabel='',
                 updown=['d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid='erddap-dataset',
                  castid=profile_idstr,
                  castdate=data_time[0])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )

plt.savefig('images/dive'+profile_idstr+'_rollvtime.png', bbox_inches='tight', dpi = (300))
plt.close()
"""