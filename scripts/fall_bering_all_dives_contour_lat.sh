#!/bin/bash

python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=temperature --paramspan -2 15 --divenum 0 1218 --castdirection=u
python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=temperature --paramspan -2 15 --divenum 0 1218 --castdirection=d

python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=salinity_raw --paramspan 31.3 32.3 --divenum 0 1218 --castdirection=u
python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=salinity_raw --paramspan 31.3 32.3 --divenum 0 1218 --castdirection=d

python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=salinity --paramspan 31.3 32.3 --divenum 0 1218 --castdirection=u
python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=salinity --paramspan 31.3 32.3 --divenum 0 1218 --castdirection=d

python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=sig695nm --paramspan 0 12 --divenum 0 1218 --castdirection=u
python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=sig695nm --paramspan 0 12 --divenum 0 1218 --castdirection=d

python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=sig700nm --paramspan 0 0.01 --divenum 0 1218 --castdirection=u 
python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=sig700nm --paramspan 0 0.01 --divenum 0 1218 --castdirection=d 

python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=do_sat --paramspan 60 130 --divenum 0 1218 --castdirection=u
python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=do_sat --paramspan 60 130 --divenum 0 1218 --castdirection=d

python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=density_insitu --paramspan 1024 1028 --divenum 0 1218 --castdirection=u
python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=density_insitu --paramspan 1024 1028 --divenum 0 1218 --castdirection=d

python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=conductivity_raw --paramspan 1.5 4 --divenum 0 1218 --castdirection=u
python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=conductivity_raw --paramspan 1.5 4 --divenum 0 1218 --castdirection=d

python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=up_par --paramspan 0 2000 --divenum 0 1218 --castdirection=u
python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=up_par --paramspan 0 2000 --divenum 0 1218 --castdirection=d

python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=down_par --paramspan 0 200 --divenum 0 1218 --castdirection=u
python oer_Glider_contour.py 2017July_BeringSea_Occulus_n --bylat --maxdepth=70 --param=down_par --paramspan 0 200 --divenum 0 1218 --castdirection=d

