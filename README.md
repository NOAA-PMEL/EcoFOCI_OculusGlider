# EcoFOCI_OculusGlider

This archive hosts utilities and workflows to edit, view, qc, and process Oculus Glider data as it pertains to the EcoFOCI group at PMEL/NOAA.

## Data Flow
- Engineering data is aquired initially by UW data processing team via communications and piloting base software (referred to as **engineering data set**)
- Comprehensive but preliminary processing and qc is performed on the engineering data set to obtain the **initial science data set** (which also has the engineering data in it to allow for comprehensive reprocessing)
- EcoFOCI processing and qc is performed on the **initial science data set** to create the **archival science data set**.  This data set may come in multiple variants.  These are described in a following section of this document.


## Archival Science Data Set - Background, Procedures, and Algorithms
`Seen during the 2017 Northern Bering Sea Deployment of Glider 402 (and not unique to this mission) strong temperature gradients (>10deg over a couple of meters) overwhelm the thermal response of the salinity (and oxygen) optodes.  This leads to unphysical spikes in salinity and oxygen which is either removed or flagged in error.  We have an ability to improve these sharp regions.`

Two types of profiles to deal with... sharp interfaces at the thermocline (which causes spiking in salinity and oxygen) and relaxed interfaces.  
- Sharp interfaces will be addressed by merging the upper portion of a downcast with the lower portion of an upcast.  The interface's temperature shape (a fast and more reliable measurement) will be used to interpolate between the two layers.  Data will then be binned in 1m intervals.
- Relaxed interfaces will be binned into 1m intervals on the upcast and downcast seperately to determine which is a more appropriate cast to maintain (perhaps both)

#### Sharp Interface defined and analyzed for 2017
**dt/dz** set at multiple values
- 0.5 -- somewhat weak interface 3445 adjusted profiles, 31 not adjusted
- 1.0 -- initial assumption      2781 adjusted profiles, 596 not adjusted
- 1.5 -- strong interface        1748 adjusted profiles, 1728 not adjusted

#### Data and parameters to keep when making science set
- temperature (has thermal corrections)
- salinity (has minor qc and thermal corrections)
- chlor (no corrections - just converted from digital counts)
- par (no corrections - just converted from digital counts)
- time, lat, lon, depth (see below)
- depth averaged current (scalar for each file)
**TODO** Oxygen?

#### Gaps when bin averaging
- if no data exists in a gap... currently leave as missing (or linearly interpolate?)

#### Location and Time
**For the 2017 Bering Fieldop, the platform surfaced once every three dives**
- It is believed that the UW software geo-routines accounts for this.  Locations (and associated times) can be decimated in the following maner:
- Sharp interfaces will use the location when the platform was at depth
- Relaxed interfaces will use the location at the start of the dive for downcasts and the initial location at the end of the dive for upcasts. (simplify routines by using the location at 1m)
***Should the lat/lons not have an automatic correction, linear interpolation along the path between the initial dive and initial surfacing will be used to estimate location***


#### MetaData
- should include the type of profile
- the dt/dz assumed


### Jupyter Notebook Examples and Additional Documentation
These can be found in the 'notebooks' subdirectory

### TODO:
#### 2018 Data
- A new datalogger (scicon) system has been implemented.
- This data has multiple time words for multiple instruments instead of everything being sampled to the same time.  This will need to be accounted for when creating thinned science data files.  Ultimately, if data is being binned every meter than a uniform window will need to be chosen.  Existing programs may not work or will need to be modified.

################

Legal Disclaimer

This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration (NOAA), or the United States Department of Commerce (DOC). All NOAA GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use. Any claims against the DOC or DOC bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation, or favoring by the DOC. The DOC seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by the DOC or the United States Government.