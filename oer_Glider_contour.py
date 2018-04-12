#!/usr/bin/env python

"""

 Background:
 --------
 oer_Glider_contour.py
 
 Purpose:
 --------
 Contour glider profile data as a function of dive/date

 History:
 --------

"""

#System Stack
import datetime
import argparse

import numpy as np
import pandas as pd

# Visual Stack
import matplotlib as mpl
mpl.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.dates import YearLocator, WeekdayLocator, MonthLocator, DayLocator, HourLocator, DateFormatter
import matplotlib.ticker as ticker
import cmocean

from io_utils.EcoFOCI_db_io import EcoFOCI_db_oculus

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2016, 9, 22)
__modified__ = datetime.datetime(2016, 9, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'arctic heat','ctd','FOCI', 'wood', 'kevin', 'alamo'

mpl.rcParams['axes.grid'] = False
mpl.rcParams['axes.edgecolor'] = 'white'
mpl.rcParams['axes.linewidth'] = 0.25
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['xtick.major.size'] = 2
mpl.rcParams['xtick.minor.size'] = 1
mpl.rcParams['xtick.major.width'] = 0.25
mpl.rcParams['xtick.minor.width'] = 0.25
mpl.rcParams['ytick.major.size'] = 2
mpl.rcParams['ytick.minor.size'] = 1
mpl.rcParams['xtick.major.width'] = 0.25
mpl.rcParams['xtick.minor.width'] = 0.25
mpl.rcParams['ytick.direction'] = 'out'
mpl.rcParams['xtick.direction'] = 'out'
mpl.rcParams['ytick.color'] = 'grey'
mpl.rcParams['xtick.color'] = 'grey'
mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['svg.fonttype'] = 'none'

# Example of making your own norm.  Also see matplotlib.colors.
# From Joe Kington: This one gives two different linear ramps:

class MidpointNormalize(colors.Normalize):
	def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
		self.midpoint = midpoint
		colors.Normalize.__init__(self, vmin, vmax, clip)

	def __call__(self, value, clip=None):
		# I'm ignoring masked values and all kinds of edge cases to make a
		# simple example...
		x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
		return np.ma.masked_array(np.interp(value, x, y))

"""----------------------------- Main -------------------------------------"""

parser = argparse.ArgumentParser(description='Oculus Glider datafile parser ')
parser.add_argument('filepath', metavar='filepath', type=str,
			   help='full path to file')
parser.add_argument('--maxdepth', type=float, 
	help="known bathymetric depth at location")
parser.add_argument('--paramspan', nargs='+', type=float, 
	help="max,min of parameter")
parser.add_argument('--divenum','--divenum', type=int, nargs=2,
	help='start and stop range for dive number')
parser.add_argument('--param', type=str,
	help='plot parameter (temperature, salinity, do_sat, sig695nm')
parser.add_argument('--castdirection', type=str,
	help='cast direction (u or d or all)')
parser.add_argument('--reverse_x', action="store_true",
	help='plot axis in reverse')
parser.add_argument('--extend_plot', type=int,
	help='days to prefil plot with blanks')
parser.add_argument('--bydivenum', action="store_true",
	help='plot x as a function of divenum and time')
parser.add_argument('--bylat', action="store_true",
	help='plot x as a function of lat')
parser.add_argument('--scatter', action="store_true",
	help='plot sample scatter points')
parser.add_argument('--boundary', action="store_true",
	help='plot boundary depth')
parser.add_argument('--latlon_vs_time', action="store_true",
	help='plot lat/lon as a function of time')

args = parser.parse_args()


startcycle=args.divenum[0]
endcycle=args.divenum[1]

#get information from local config file - a json formatted file
config_file = 'EcoFOCI_config/db_config/db_config_oculus_local.pyini'
db_table = '2017_fall_sg401_sciencesubset'
db_table2 = '2017_fall_sg401_sciencesubset'

EcoFOCI_db = EcoFOCI_db_oculus()
(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)

depth_array = np.arange(0,args.maxdepth+1,0.5) 
num_cycles = EcoFOCI_db.count(table=db_table2, start=startcycle, end=endcycle)
temparray = np.ones((num_cycles,len(depth_array)))*np.nan
ProfileTime, ProfileLat = [],[]
cycle_col=0

if args.param in ['temperature']:
	cmap = cmocean.cm.thermal
elif args.param in ['salinity','salinity_raw','conductivity_raw']:
	cmap = cmocean.cm.haline
elif args.param in ['do_sat']:
	cmap = cmocean.cm.delta_r
elif args.param in ['sig695nm','chl','chla','chlorophyl']:
	cmap = cmocean.cm.algae
elif args.param in ['sig700nm','turb','turbidity']:
	cmap = cmocean.cm.turbid
elif args.param in ['density_insitu','sigma_t','sigma_theta']:
	cmap = cmocean.cm.dense
elif args.param in ['up_par','down_par']:
	cmap = cmocean.cm.solar
elif args.param in ['dtemp_dpress','ddens_dpress']:
	if args.boundary:
		cmap = cmocean.cm.gray_r
	else:
		cmap = cmocean.cm.delta

else:
	cmap = cmocean.cm.gray

### plot a single parameter as a function of time gouping by divenum (good for lat/lon)
if args.latlon_vs_time:
	Profile_sb = EcoFOCI_db.read_location(table=db_table, 
									  param=['latitude,longitude'],
									  dive_range=[startcycle,endcycle],
									  verbose=True)	
	
	Profile_nb = EcoFOCI_db.read_location(table=db_table2, 
									  param=['latitude,longitude'],
									  dive_range=[startcycle,endcycle],
									  verbose=True)

	fig = plt.figure(1, figsize=(12, 3), facecolor='w', edgecolor='w')
	ax1 = fig.add_subplot(111)

	xtime = np.array([Profile_sb[v]['time'] for k,v in enumerate(Profile_sb.keys())])
	ydata = np.array([Profile_sb[v]['latitude'] for k,v in enumerate(Profile_sb.keys())])
	plt.scatter(x=xtime, y=ydata,s=1,marker='.',color='#849B00') 
	xtime_nb = np.array([Profile_nb[v]['time'] for k,v in enumerate(Profile_nb.keys())])
	ydata_nb = np.array([Profile_nb[v]['latitude'] for k,v in enumerate(Profile_nb.keys())])
	plt.scatter(x=xtime_nb, y=ydata_nb,s=1,marker='.',color='#B6D800') 


	ax1.set_ylim([59,63])
	"""	if args.extend_plot:
		ax1.set_xlim([xtime[0],xtime[0]+datetime.timedelta(days=args.extend_plot)])
	if args.reverse_x:
		ax1.invert_xaxis()"""

	ax1.xaxis.set_major_locator(DayLocator(bymonthday=15))
	ax1.xaxis.set_minor_locator(DayLocator(bymonthday=range(1,32,1)))
	ax1.xaxis.set_major_formatter(ticker.NullFormatter())
	ax1.xaxis.set_minor_formatter(DateFormatter('%d'))
	ax1.xaxis.set_major_formatter(DateFormatter('%b %y'))
	ax1.xaxis.set_tick_params(which='major', pad=25)

	plt.tight_layout()
	#plt.savefig(args.filepath + '_' + args.param + args.castdirection + '.svg', transparent=False, dpi = (300))
	plt.savefig(args.filepath + '_' + args.param + '.png', transparent=False, dpi = (300))
	plt.close()

if args.bydivenum:
	fig = plt.figure(1, figsize=(12, 3), facecolor='w', edgecolor='w')
	ax1 = fig.add_subplot(111)		
	for cycle in range(startcycle,endcycle+1,1):
		#get db meta information for mooring
		Profile = EcoFOCI_db.read_profile(table=db_table, 
										  divenum=cycle, 
										  castdirection=args.castdirection, 
										  param=args.param,
										  verbose=True)

		try:
			temp_time =  Profile[sorted(Profile.keys())[0]]['time']
			ProfileTime = ProfileTime + [temp_time]
			Pressure = np.array(sorted(Profile.keys()))
			if args.boundary:
				Temperature = np.array([Profile[x][args.param] for x in sorted(Profile.keys()) ], dtype=np.float)
				dtdz_max = np.where(Temperature == np.min(Temperature))
				Temperature = np.zeros_like(Temperature)
				Temperature[dtdz_max] = 1
			else:
				Temperature = np.array([Profile[x][args.param] for x in sorted(Profile.keys()) ], dtype=np.float)

			temparray[cycle_col,:] = np.interp(depth_array,Pressure,Temperature,left=np.nan,right=np.nan)
			cycle_col +=1

			xtime = np.ones_like(np.array(sorted(Profile.keys()))) * mpl.dates.date2num(temp_time)
			#turn off below and set zorder to 1 for no scatter plot colored by points
			if args.scatter:
				plt.scatter(x=xtime, y=np.array(sorted(Profile.keys())),s=1,marker='.', edgecolors='none', c='k', zorder=3, alpha=1) 
			
			plt.scatter(x=xtime, y=np.array(sorted(Profile.keys())),s=15,marker='.', edgecolors='none', c=Temperature, 
			vmin=args.paramspan[0], vmax=args.paramspan[1], 
			cmap=cmap, zorder=1)
		except:
			pass


	cbar = plt.colorbar()
	#cbar.set_label('Temperature (C)',rotation=0, labelpad=90)
	if args.param in ['sig700nm','turb','turbidity','dtemp_dpress','ddens_dpress']:
		interval=0.005
	else:
		interval=0.05
	plt.contourf(ProfileTime,depth_array,temparray.T, 
		extend='both', cmap=cmap, levels=np.arange(args.paramspan[0],args.paramspan[1],interval), alpha=1.0)

	ax1.invert_yaxis()
	if args.extend_plot:
		ax1.set_xlim([ProfileTime[0],ProfileTime[0]+datetime.timedelta(days=args.extend_plot)])
	if args.reverse_x:
		ax1.invert_xaxis()

	ax1.xaxis.set_major_locator(DayLocator(bymonthday=15))
	ax1.xaxis.set_minor_locator(DayLocator(bymonthday=range(1,32,1)))
	ax1.xaxis.set_major_formatter(ticker.NullFormatter())
	ax1.xaxis.set_minor_formatter(DateFormatter('%d'))
	ax1.xaxis.set_major_formatter(DateFormatter('%b %y'))
	ax1.xaxis.set_tick_params(which='major', pad=25)

	plt.tight_layout()
	#plt.savefig(args.filepath + '_' + args.param + args.castdirection + '.svg', transparent=False, dpi = (300))
	plt.savefig(args.filepath + '_' + args.param + args.castdirection + '.png', transparent=False, dpi = (300))
	plt.close()

if args.bylat:
	fig = plt.figure(1, figsize=(12, 3), facecolor='w', edgecolor='w')
	ax1 = fig.add_subplot(111)		
	for cycle in range(startcycle,endcycle+1,1):
		#get db meta information for mooring
		Profile = EcoFOCI_db.read_ave_lat(table=db_table2, 
										  divenum=cycle, 
										  castdirection=args.castdirection, 
										  param=args.param,
										  verbose=True)

		try:
			temp_lat =  Profile[sorted(Profile.keys())[0]]['latitude']
			ProfileLat = ProfileLat + [temp_lat]
			Pressure = np.array(sorted(Profile.keys()))
			Temperature = np.array([Profile[x][args.param] for x in sorted(Profile.keys()) ], dtype=np.float)

			temparray[cycle_col,:] = np.interp(depth_array,Pressure,Temperature,left=np.nan,right=np.nan)
			cycle_col +=1

			xtime = np.ones_like(np.array(sorted(Profile.keys()))) * temp_lat
			#turn off below and set zorder to 1 for no scatter plot colored by points
			plt.scatter(x=xtime, y=np.array(sorted(Profile.keys())),s=1,marker='.', edgecolors='none', c='k', zorder=3, alpha=1) 
			
			plt.scatter(x=xtime, y=np.array(sorted(Profile.keys())),s=15,marker='.', edgecolors='none', c=Temperature, 
			vmin=args.paramspan[0], vmax=args.paramspan[1], 
			cmap=cmap, zorder=1)
		except IndexError:
			pass


	cbar = plt.colorbar()
	#cbar.set_label('Temperature (C)',rotation=0, labelpad=90)
	if args.param in ['sig700nm','turb','turbidity']:
		interval=0.005
	else:
		interval=0.05
	plt.contourf(ProfileLat,depth_array,temparray.T, 
		extend='both', cmap=cmap, levels=np.arange(args.paramspan[0],args.paramspan[1],interval), alpha=1.0)

	ax1.invert_yaxis()
	if args.extend_plot:
		pass
	if args.reverse_x:
		ax1.invert_xaxis()

	#ax1.xaxis.set_major_locator(DayLocator(bymonthday=15))
	#ax1.xaxis.set_minor_locator(DayLocator(bymonthday=range(1,32,1)))
	#ax1.xaxis.set_major_formatter(ticker.NullFormatter())
	#ax1.xaxis.set_minor_formatter(DateFormatter('%d'))
	#ax1.xaxis.set_major_formatter(DateFormatter('%b %y'))
	#ax1.xaxis.set_tick_params(which='major', pad=25)

	plt.tight_layout()
	#plt.savefig(args.filepath + '_' + args.param + args.castdirection + '.svg', transparent=False, dpi = (300))
	plt.savefig(args.filepath + '_' + args.param + args.castdirection + '_lat.png', transparent=False, dpi = (300))
	plt.close()

EcoFOCI_db.close()
