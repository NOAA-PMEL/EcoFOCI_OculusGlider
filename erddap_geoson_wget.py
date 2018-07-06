"""
erddap_geojson_wget.py

Purpose:
	Connect to erddap server and retrieve geojson file for chosen glider 
	The dataset is very high frequency so only get sfc (<1m) points

2018-07-03: Forked from prawler_wget.py

"""
#System Stack
import datetime
import argparse

import wget

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2016, 6, 01)
__modified__ = datetime.datetime(2016, 6, 01)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'CTD', 'SeaWater', 'Cruise', 'derivations','erddap'

"""--------------------------------helper Routines---------------------------------------"""


"""--------------------------------main Routines---------------------------------------"""

parser = argparse.ArgumentParser(description='erddap geojson Data Retrieval')
parser.add_argument("-s",'--ServerName', type=str,
			   default="http://downdraft.pmel.noaa.gov",
               help='server name, eg. http://yawl.pmel.noaa.gov')
parser.add_argument("-e",'--ErddapID', type=str,
			   default="sg403_PS_spring18",
               help='erddap datasetID')
parser.add_argument("-o",'--outfile', type=str,
			   default="out.geojson",
               help='geojson output filename')
parser.add_argument("-i",'--instrument', type=str,
			   default="oculusglider",
               help='datasource')
                    
args = parser.parse_args()

filename = args.outfile
if args.instrument in ['oculusglider']:
	url = args.ServerName + ':8080/erddap/tabledap/'+\
	args.ErddapID + '.geoJson?ctd_depth%2Clatitude%2Clongitude%2Ctime&ctd_depth%3C=1&time%3E=2018-04-05T00%3A00%3A00Z&time%3C=2018-04-12T17%3A11%3A05Z'
elif args.instrument in ['alamo']:
	url = args.ServerName + ':8080/erddap/tabledap/'+\
	args.ErddapID + '.geoJson?PRESS%2Clatitude%2Clongitude%2Ctime&PRESS%3C=1&time%3E=2018-04-05T00%3A00%3A00Z&time%3C=2018-04-12T17%3A11%3A05Z'
else:
	print('Currently only works with gliders and alamos')
print(url)
wget.download(url, filename, bar=wget.bar_thermometer)
