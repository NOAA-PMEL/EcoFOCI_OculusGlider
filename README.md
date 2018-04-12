# EcoFOCI_OculusGlider

This archive hosts utilities and workflows to edit, view, qc, and process Oculus Glider data as it pertains to the EcoFOCI group at PMEL/NOAA.

## Data Flow
- Engineering data is aquired initially by UW data processing team via communications and piloting base software (referred to as **engineering data set**)
- Comprehensive but preliminary processing and qc is performed on the engineering data set to obtain the **initial science data set** (which also has the engineering data in it to allow for comprehensive reprocessing)
- EcoFOCI processing and qc is performed on the **initial science data set** to create the **archival science data set**.  This data set may come in multiple variants.  These are described in a following section of this document.


## Archival Science Data Set - Background, Procedures, and Algorithms
`Seen during the 2017 Northern Bering Sea Deployment of Glider 402 (and not unique to this mission) strong temperature gradients (>10deg over a couple of meters) overwhelm the thermal response of the salinity (and oxygen) optodes.  This leads to unphysical spikes in salinity and oxygen which is either removed or flagged in error.  We have an ability to improve these sharp regions.`

### Jupyter Notebook Examples and Additional Documentation
These can be found in the 'notebooks' subdirectory

################

Legal Disclaimer

This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration (NOAA), or the United States Department of Commerce (DOC). All NOAA GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use. Any claims against the DOC or DOC bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation, or favoring by the DOC. The DOC seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by the DOC or the United States Government.