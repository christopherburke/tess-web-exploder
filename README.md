# tess-web-exploder
TESS Web Exploder (TWEXO) - TESS target information loader

Load a local web page with links customized for the TESS target of interest that point to that target on the major online catalogs.  Optionally '-E' load all of them in web browser tabs. 

### Install
Download twexo.py to a local directory

### Warning
- TWEXO opens tabs on your web browser
- TWEXO saves a local html page to your hard drive 
- Always sanity check that the target resolving is retrieving information for your target
- Information for high proper motion targets may not be retrieved correctly

### Examples
- Display command line arguments and features

`python twexo.py -h`

- Query by name

`python twexo.py -n 'Pi Mensae'`
            
- For the impatient and the EXPLODE experience add -E

`python twexo.py -n 'Pi Mensae' -E`
            
- Query by TOI number

`python twexo.py -toi 144.01`

- Query by TIC number

`python twexo.py -t 261136679`

- Query by Coordinates in decimal degrees

`python twexo.py -c 84.291198 -80.469143`

### AUTHORS
Christopher J. Burke (MIT).  Testing and Advice from Susan Mullally (STScI) and Jennifer Burt (MIT)

### VERSION: 0.3

### WHAT'S NEW:
V0.3
- Extra GAIA information display; TESSCut target pixel file download link; treated some bugs and value checking that cropped due to missing catalog values

V0.2.1
- Added timeout check during the DV report search at MAST to not lead to error

V0.2
- Fixed Finder Chart URL to work.

- Added some proper motion adjustments to position to get better GAIA match for high proper motion objects

- Some basic TIC and GAIA DR2 information about target is not shown on main page

- If you have tess-point installed (pip install tess-point), it will show which TESS sectors the target is observable
   in TESS year 1.  If you don't have tess-point installed that is okay it checks and does not show this information
   
- If NASA Ames SPOC DV reports for this target exist links to them will be given in a list.

### TODOS:
1. Direct link to GAIA results. Currently can be found at bottom of Simbad page
2. Currently this is target based, but want to point to TOI or planet candidate pages
3. Exo.mast.stsci.edu for the TOI based linking
4. Add as page to the TESS-ExoClass candidate reports
5. Someway (lightkurve?) to load a jupyter notebook or other on demand light curve examination product from the web.
6. Capability to set an observatory location and provide links to airmass tables and links to transit event
      observability calculators online.
7. The coding is atrocious.  Need to make many of the procedures into functions to clean things up.

### DEPENDENCIES:
- python 3+
- astropy
- numpy

### SPECIAL THANKS TO:
Includes code from the python MAST query examples 
https://mast.stsci.edu/api/v0/pyex.html
Brett Morris (UW) for name resolving help from the tess-point project

