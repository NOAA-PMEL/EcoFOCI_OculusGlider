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

parser = argparse.ArgumentParser(description='yawl Data Retrieval')
parser.add_argument('Project', metavar='Project', type=str,
               help='project name e.g. 2016_ITAE')
parser.add_argument("-s",'--ServerName', type=str,
			   default="http://downdraft.pmel.noaa.gov",
               help='server name, eg. http://yawl.pmel.noaa.gov')
parser.add_argument("-e",'--ErddapID', type=str,
			   default="sg403_PS_spring18",
               help='erddap datasetID')

          
args = parser.parse_args()

filename = '18PS_erddap_cron.geojson'
url = args.ServerName + ':8080/erddap/tabledap/'+\
args.ErddapID + '.geoJson?ctd_depth%2Clatitude%2Clongitude%2Ctime&ctd_depth%3C=1&time%3E=2018-04-05T00%3A00%3A00Z&time%3C=2018-04-12T17%3A11%3A05Z'
print(url)
wget.download(url, filename, bar=wget.bar_thermometer)
