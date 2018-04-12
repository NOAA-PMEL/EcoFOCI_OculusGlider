#!/bin/bash

python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=temperature --paramspan -2 15 --divenum 1218 3500 --castdirection=u --reverse_x --extend_plot 23 --scatter
python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=temperature --paramspan -2 15 --divenum 1218 3500 --castdirection=d --reverse_x --extend_plot 23 --scatter

python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=salinity_raw --paramspan 31.3 32.3 --divenum 1218 3500 --castdirection=u --reverse_x --extend_plot 23 --scatter
python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=salinity_raw --paramspan 31.3 32.3 --divenum 1218 3500 --castdirection=d --reverse_x --extend_plot 23 --scatter

python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=salinity --paramspan 31.3 32.3 --divenum 1218 3500 --castdirection=u --reverse_x --extend_plot 23 --scatter
python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=salinity --paramspan 31.3 32.3 --divenum 1218 3500 --castdirection=d --reverse_x --extend_plot 23 --scatter

python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=sig695nm --paramspan 0 12 --divenum 1218 3500 --castdirection=u --reverse_x --extend_plot 23 --scatter
python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=sig695nm --paramspan 0 12 --divenum 1218 3500 --castdirection=d --reverse_x --extend_plot 23 --scatter

python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=sig700nm --paramspan 0 0.01 --divenum 1218 3500 --castdirection=u --reverse_x --extend_plot 23 --scatter
python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=sig700nm --paramspan 0 0.01 --divenum 1218 3500 --castdirection=d --reverse_x --extend_plot 23 --scatter

python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=do_sat --paramspan 60 130 --divenum 1218 3500 --castdirection=u --reverse_x --extend_plot 23 --scatter
python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=do_sat --paramspan 60 130 --divenum 1218 3500 --castdirection=d --reverse_x --extend_plot 23 --scatter

python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=density_insitu --paramspan 1024 1028 --divenum 1218 3500 --castdirection=u --reverse_x --extend_plot 23 --scatter
python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=density_insitu --paramspan 1024 1028 --divenum 1218 3500 --castdirection=d --reverse_x --extend_plot 23 --scatter

python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=conductivity_raw --paramspan 1.5 4 --divenum 1218 3500 --castdirection=u --reverse_x --extend_plot 23 --scatter
python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=conductivity_raw --paramspan 1.5 4 --divenum 1218 3500 --castdirection=d --reverse_x --extend_plot 23 --scatter

python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=up_par --paramspan 0 2000 --divenum 1218 3500 --castdirection=u --reverse_x --extend_plot 23 --scatter
python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=up_par --paramspan 0 2000 --divenum 1218 3500 --castdirection=d --reverse_x --extend_plot 23 --scatter

python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=down_par --paramspan 0 200 --divenum 1218 3500 --castdirection=u --reverse_x --extend_plot 23 --scatter
python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --bydivenum --maxdepth=70 --param=down_par --paramspan 0 200 --divenum 1218 3500 --castdirection=d --reverse_x --extend_plot 23 --scatter

python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --latlon_vs_time --maxdepth=70 --param=latlon --paramspan 0 200 --divenum 0 3500 --reverse_x --extend_plot 23


## User built parameters
python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --maxdepth=70 --param=dtemp_dpress --paramspan -12 12 --divenum 1218 3500 --castdirection=u --reverse_x --bydivenum
python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --maxdepth=70 --param=dtemp_dpress --paramspan -12 12 --divenum 1218 3500 --castdirection=d --reverse_x --bydivenum

python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --maxdepth=70 --param=ddens_dpress --paramspan -2 2 --divenum 1218 3500 --castdirection=u --reverse_x --bydivenum
python oer_Glider_contour.py 2017July_BeringSea_Occulus_s --maxdepth=70 --param=ddens_dpress --paramspan -2 2 --divenum 1218 3500 --castdirection=d --reverse_x --bydivenum
