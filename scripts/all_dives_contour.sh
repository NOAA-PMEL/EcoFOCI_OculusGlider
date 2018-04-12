#!/bin/bash

python oer_Glider_contour.py 2017_BeringSea_Occulus --maxdepth=70 --param=temperature --paramspan -2 6 --divenum 1 387 --castdirection=u
python oer_Glider_contour.py 2017_BeringSea_Occulus --maxdepth=70 --param=temperature --paramspan -2 6 --divenum 1 387 --castdirection=d

python oer_Glider_contour.py 2017_BeringSea_Occulus --maxdepth=70 --param=salinity --paramspan 31.3 32.3 --divenum 1 387 --castdirection=u
python oer_Glider_contour.py 2017_BeringSea_Occulus --maxdepth=70 --param=salinity --paramspan 31.3 32.3 --divenum 1 387 --castdirection=d

python oer_Glider_contour.py 2017_BeringSea_Occulus --maxdepth=70 --param=sig695nm --paramspan 0 12 --divenum 1 387 --castdirection=u
python oer_Glider_contour.py 2017_BeringSea_Occulus --maxdepth=70 --param=sig695nm --paramspan 0 12 --divenum 1 387 --castdirection=d

python oer_Glider_contour.py 2017_BeringSea_Occulus --maxdepth=70 --param=do_sat --paramspan 60 130 --divenum 1 387 --castdirection=u
python oer_Glider_contour.py 2017_BeringSea_Occulus --maxdepth=70 --param=do_sat --paramspan 60 130 --divenum 1 387 --castdirection=d