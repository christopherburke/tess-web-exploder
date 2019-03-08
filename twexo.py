"""
twexo.py - TESS Web Explode
  TESS Input Catalog web browser data exploder.
  WARNING: This routines opens tabs on your browser!
     This routine saves a local file for the html page!
     Always sanity check the target is correctly resolved!
     High proper motion targets may not be resolved correctly.
     
  Creates a local html page tailored for the target of interest
    and loads the page in your web browser with the links to the major
    catalogs to get information about the target.  Targets can be specified
    by TIC id, TOI number, common name, and ra/dec coordinates.
    
    
USAGE: 
        -to display command line arguments:
            python twexo.py -h
            
        -query by Name
            python twexo.py -n 'Pi Mensae'
            
        -For the impatient and the EXPLODE experience add -E
            python twexo.py -n 'Pi Mensae' -E
            
        -query by TOI number
            python twexo.py -toi 144.01
        -query by TIC number
            python twexo.py -t 261136679
        -query by Coordinates in decimal degrees
            python twexo.py -c 84.291198 -80.469143
       
      
AUTHORS: Christopher J. Burke (MIT)
 Testing and Advice from Susan Mullally (STScI) and Jennifer Burt (MIT)

VERSION: 0.1

NOTES: This routine opens tabs on your browser!
    This routine saves a local file for the html!
    
DEPENDENCIES:
    python 3+
    astropy
    numpy
    
SPECIAL THANKS TO:
    Includes code from the python MAST query examples 
    https://mast.stsci.edu/api/v0/pyex.html
    Brett Morris (UW) for help with the name resolving from another the tess-point project

"""

import webbrowser
import numpy as np
import os
import argparse
from astropy.coordinates import SkyCoord
import sys
import datetime
import json
try: # Python 3.x
    from urllib.parse import quote as urlencode
    from urllib.request import urlretrieve
    from urllib.parse import urlencode as dict_urlencode
    from urllib.request import urlopen
except ImportError:  # Python 2.x
    from urllib import pathname2url as urlencode
    from urllib import urlretrieve
    from urllib import urlendcode as dict_urlencode
    from urllib import urlopen
try: # Python 3.x
    import http.client as httplib 
except ImportError:  # Python 2.x
    import httplib
    
import csv
import time



## [Mast Query]
def mastQuery(request):

    server='mast.stsci.edu'

    # Grab Python Version 
    version = ".".join(map(str, sys.version_info[:3]))

    # Create Http Header Variables
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain",
               "User-agent":"python-requests/"+version}

    # Encoding the request as a json string
    requestString = json.dumps(request)
    requestString = urlencode(requestString)
    
    # opening the https connection
    conn = httplib.HTTPSConnection(server)

    # Making the query
    conn.request("POST", "/api/v0/invoke", "request="+requestString, headers)

    # Getting the response
    resp = conn.getresponse()
    head = resp.getheaders()
    content = resp.read().decode('utf-8')

    # Close the https connection
    conn.close()

    return head,content
## [Mast Query]

def safe_char(input):
    """ https://stackoverflow.com/questions/5843518/remove-all-special-characters-punctuation-and-spaces-from-string
    """
    if input:

        import re
        input = re.sub('\W+', '', input)

    return input



    
if __name__ == '__main__':
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--ticId", type=int, \
                        help="TIC Id [int] ")
    parser.add_argument("-c", "--coord", type=float, nargs=2, \
                        help="RA and Dec of target [deg]")
    parser.add_argument("-n", "--name", nargs=1, type=str, \
                        help="Search for a target by resolving its name with SESAME")
    parser.add_argument("-toi", "--toi", type=float, \
                        help="TOI number of target")
    parser.add_argument("-E", "--explode", action='store_true', \
                        help="Pre-load all URLs into tabs of browser rather than just the link page")
                        
    args = parser.parse_args()

# DEBUG BLOCK for hard coding input parameters and testing
 #   class test_arg:
 #       def __init__(self):
#            self.ticId = 366443426
#           self.ticId = None
#            self.coord = None
#            self.name = None
#            self.name = 'Pi Mensae'
#            self.toi = None
#            self.explode = False
#            self.toi = 383.01
#    args = test_arg()

    #Search radius for reporting nearby TIC targets
    SEARCH_RAD = 60.0 # arcsec
    # At least one Mode -t -c -n -toi must have been specified
    if (args.ticId is None) and (args.coord is None) and (args.name is None) and (args.toi is None):
        print('You must specify one and only one mode -t, -c, -n, -toi')
        print('`python twex.py -h\' for help')
        sys.exit(1)

    useTIC = 0
    # If TIC specified assign it to useTIC
    # and query MAST for RA and Dec and other catalog identifiers
    if args.ticId is not None:
        useTIC = int(args.ticId)
        starTics = np.array([useTIC], dtype=np.int32)
        ticStringList = ['{0:d}'.format(x) for x in starTics]    
        # Setup mast query
        request = {'service':'Mast.Catalogs.Filtered.Tic', \
           'params':{'columns':'*', 'filters':[{ \
                    'paramName':'ID', 'values':ticStringList}]}, \
            'format':'json', 'removenullcolumns':True}
        headers, outString = mastQuery(request)
        outObject = json.loads(outString)
        starRa = outObject['data'][0]['ra']
        starDec = outObject['data'][0]['dec']
        star2mass = outObject['data'][0]['TWOMASS']
        stargaia = outObject['data'][0]['GAIA']
        
    # TOI specified get toi -> tic mapping from table at exofop
    if args.toi is not None:
        toiURL = 'https://exofop.ipac.caltech.edu/tess/download_toi.php?sort=toi&output=csv'
        tmp = []
        with urlopen(toiURL) as response:
            for line in response:
                line = line.decode('utf-8')
                for x in csv.reader([line]):
                    tmp.append("|".join(x))

        dtypeseq = ['i4','f8']
        dtypeseq.extend(['i4']*7)
        dtypeseq.extend(['U3','U3'])
        dtypeseq.extend(['f8','f8'])
        dtypeseq.extend(['U40','i4','U40','U40','U40'])
        dtypeseq.extend(['f8']*27)
        dtypeseq.extend(['U80']*4)
        dataBlock = np.genfromtxt(tmp, \
                                  dtype=dtypeseq, delimiter='|',skip_header=1)
        exoTic = dataBlock['f0']
        exoToi = dataBlock['f1']
        idx = np.where(exoToi == args.toi)[0]
        if len(idx) == 0:
            print('Could not find TOI {0} at ExoFop'.format(args.toi))
            sys.exit(1)
        useTIC = int(exoTic[idx])
        # Now that we have the TIC do a MAST query to get TIC values
        starTics = np.array([useTIC], dtype=np.int32)
        ticStringList = ['{0:d}'.format(x) for x in starTics]    
        # Setup mast query
        request = {'service':'Mast.Catalogs.Filtered.Tic', \
           'params':{'columns':'*', 'filters':[{ \
                    'paramName':'ID', 'values':ticStringList}]}, \
            'format':'json', 'removenullcolumns':True}
        headers, outString = mastQuery(request)
        outObject = json.loads(outString)
        starRa = outObject['data'][0]['ra']
        starDec = outObject['data'][0]['dec']
        star2mass = outObject['data'][0]['TWOMASS']
        stargaia = outObject['data'][0]['GAIA']
        
        #print('TOI: {0} is associated with TIC: {1} at ExoFop'.format(args.toi, useTIC))

    # Do name resolving to get ra and dec
    if args.name is not None:
        # Name resolve  in try except  for detecting problem
        try:
            coordinate = SkyCoord.from_name(args.name[0])
            print("Coordinates for {0}: ({1}, {2})"
              .format(args.name[0], coordinate.ra.degree,
                      coordinate.dec.degree))
            starRa = coordinate.ra.degree
            starDec = coordinate.dec.degree
        except:
            print("Could not resolve: {0}".format(args.name[0]))
            sys.exit(1)


    if args.coord is not None:
        starRa = args.coord[0]
        starDec = args.coord[1]
    # Do a MAST cone search around the ra and dec to get the nearby stars
    #  for all runs and to find the closest  TIC for the coordinate input 
    #   and name query
    # Protect against missing TICs
    try:
        # Do cone search around this position
        startTime = time.time()
        request = {'service':'Mast.Catalogs.Filtered.Tic.Position', \
                   'params':{'columns':'c.*', \
                             'filters':[ \
                                        {'paramName':'Tmag',\
                                         'values':[{'min':0, 'max':20.0}]}], \
                             'ra':'{:10.5f}'.format(starRa),\
                             'dec':'{:10.5f}'.format(starDec),\
                             'radius':'{:10.7f}'.format(SEARCH_RAD/3600.0) \
                             }, \
                    'format':'json', 'removenullcolumns':False}
        while True:    
            headers, outString = mastQuery(request)
            outObject = json.loads(outString)
            if outObject['status'] != 'EXECUTING':
                    break
            if time.time() - startTime > 30:
                    print('Working...')
                    startTime = time.time()
            time.sleep(5)
         
        ticList = np.array([x['ID'] for x in outObject['data']], dtype=np.int32)
        ticRas = np.array([x['ra'] for x in outObject['data']], dtype=np.float)
        ticDecs = np.array([x['dec'] for x in outObject['data']], dtype=np.float)

    except:
        # Cone search failed
        print('TIC Search Fail at position {0} {1}'.format(starRa, starDec))
        sys.exit(1)

    # Check if no targets were returned in cone search
    if len(ticList) == 0:
        print('MAST cone search around TIC returned no objects')
        sys.exit(1)
    
    targCoord = SkyCoord(starRa, starDec, unit='deg')
    ticCoords = SkyCoord(ticRas, ticDecs, unit='deg')
    seps = targCoord.separation(ticCoords)
    ia = np.argsort(seps)
    ticList = ticList[ia]
    ticRas = ticRas[ia]
    ticDecs = ticDecs[ia]
    seps = seps[ia]

    # If we hadn't defined which target is useTIC yet do it now
    if useTIC == 0:
        useTIC = ticList[0]
        starTics = np.array([useTIC], dtype=np.int32)
        ticStringList = ['{0:d}'.format(x) for x in starTics]    
        # Setup mast query
        request = {'service':'Mast.Catalogs.Filtered.Tic', \
           'params':{'columns':'*', 'filters':[{ \
                    'paramName':'ID', 'values':ticStringList}]}, \
            'format':'json', 'removenullcolumns':True}
        headers, outString = mastQuery(request)
        outObject = json.loads(outString)
        starRa = outObject['data'][0]['ra']
        starDec = outObject['data'][0]['dec']
        star2mass = outObject['data'][0]['TWOMASS']
        stargaia = outObject['data'][0]['GAIA']

    # If we weren't given TOI number check exofop to see if it has TOIs
    if args.toi is None:
        toiURL = 'https://exofop.ipac.caltech.edu/tess/download_toi.php?sort=toi&output=csv'
        tmp = []
        with urlopen(toiURL) as response:
            for line in response:
                line = line.decode('utf-8')
                for x in csv.reader([line]):
                    tmp.append("|".join(x))

        dtypeseq = ['i4','f8']
        dtypeseq.extend(['i4']*7)
        dtypeseq.extend(['U3','U3'])
        dtypeseq.extend(['f8','f8'])
        dtypeseq.extend(['U40','i4','U40','U40','U40'])
        dtypeseq.extend(['f8']*27)
        dtypeseq.extend(['U80']*4)
        dataBlock = np.genfromtxt(tmp, \
                                  dtype=dtypeseq, delimiter='|',skip_header=1)
        exoTic = dataBlock['f0']
        exoToi = dataBlock['f1']
        idx = np.where(exoTic == useTIC)[0]
        if len(idx) == 0:
            toihdr = 'No TOIs associated with TIC at ExoFop'
            toicheckstr = '<br>'
        else:
            toihdr = 'TIC Hosts TOIs'
            toilist = []
            for j in idx:
                toilist.append('{0:.2f}<br>'.format(exoToi[j]))     
            toicheckstr = ' '.join(toilist)
    else:
        toihdr = 'Using TOI {:.2f}'.format(args.toi)
        toicheckstr = ''
        
    # FORM THE URLS
        
    # ESO archive
    esoURLPart1 = 'https://archive.eso.org/scienceportal/home?data_release_date=*:2019-03-06&'
    esoURLPart2 = 'pos={0},{1}'.format(starRa,starDec)
    esoURLPart3 = '&r=0.008333&sort=dist,-fov,-obs_date&s=P%2fDSS2%2fcolor&f=0.064387&fc=84.485552,-80.451816&cs=J2000&av=true&ac=false&c=8,9,10,11,12,13,14,15,16,17,18&mt=true&dts=true'
    esoURL = esoURLPart1 + esoURLPart2 + esoURLPart3

        
    # IRSA finderchart
    irsaURLPart1 = 'https://irsa.ipac.caltech.edu/applications/finderchart/?__action=table.search&request=%7B%22startIdx%22%3A0%2C%22pageSize%22%3A100%2C%22id%22%3A%22QueryFinderChartWeb%22%2C%22tbl_id%22%3A%22results%22%2C%22UserTargetWorldPt%22%3A%22126.61572%3B10.08046%3BEQ_J2000%3B'
    irsaURLPart2 = urlencode('2MASS J{0}'.format(star2mass))
    irsaURLPart3 = '%3Bned%22%2C%22imageSizeAndUnit%22%3A%220.042777777777777776%22%2C%22thumbnail_size%22%3A%22256%22%2C%22selectImage%22%3A%22dss%2Csdss%2C2mass%22%2C%22searchCatalog%22%3A%22no%22%2C%22ckgDSS%22%3A%22dss1Blue%2Cdss1Red%2Cdss2Blue%2Cdss2Red%2Cdss2IR%22%2C%22ckgSDSS%22%3A%22u%2Cg%2Cr%2Cz%22%2C%22ckg2MASS%22%3A%22j%2Ch%2Ck%22%2C%22imageSearchOptions%22%3A%22closed%22%2C%22META_INFO%22%3A%7B%22title%22%3A%22QueryFinderChartWeb%22%2C%22tbl_id%22%3A%22results%22%7D%7D&options=%7B%22tbl_group%22%3A%22results%22%2C%22removable%22%3Afalse%2C%22showTitle%22%3Afalse%2C%22pageSize%22%3A100%7D'
    irsaURL = irsaURLPart1 + irsaURLPart2 + irsaURLPart3
    
    # MAST Data portal
    mstURLPart1 = 'https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html?searchQuery=%7B%22service%22%3A%22CAOMDB%22%2C%22inputText%22%3A%22'
    mstURLPart2 = 'TIC%20{0:d}'.format(useTIC)
    mstURLPart3 = '%22%2C%22paramsService%22%3A%22Mast.Caom.Cone%22%2C%22title%22%3A%22MAST%3A%20TIC%20261136679%22%2C%22columns%22%3A%22*%22%2C%22caomVersion%22%3Anull%7D'
    mstURL = mstURLPart1 + mstURLPart2 + mstURLPart3

    #Vizier search
    vizPOSTDict = {'-c': '2MASS J{0}'.format(star2mass)}
    vizURLPart1 = 'http://vizier.u-strasbg.fr/viz-bin/VizieR-4?-out.max=50&-out.form=HTML+Table&-out.add=_r&-out.add=_RAJ%2C_DEJ&%2F%2Foutaddvalue=default&-sort=_r&-order=I&-oc.form=sexa&'
    vizURLPart2 = dict_urlencode(vizPOSTDict)
    vizURLPart3 = '&-c.eq=J2000&-c.r=+30&-c.u=arcsec&-c.geom=r'
    vizURL = vizURLPart1 + vizURLPart2 + vizURLPart3

    # exofop 
    exofopURL = 'https://exofop.ipac.caltech.edu/tess/target.php?id={0}'.format(useTIC)
    
    # Simbad page
    simbadPOSTDict = {'Ident': '2MASS J{0}'.format(star2mass)}
    simbadURL = 'http://simbad.u-strasbg.fr/simbad/sim-basic?{0}'.format(dict_urlencode(simbadPOSTDict))
    #print(simbadURL)

    # Prepare strings for the HTML page
    DATE_STR = datetime.date.today().strftime('%Y%m%d')

    if args.toi is not None:
        path = os.path.abspath('twexo_temp_{0}_{1:.2f}.html'.format(DATE_STR,args.toi))
        ModeHeader = 'TOI: {0} is associated with TIC: {1} at ExoFop'.format(args.toi, useTIC)
    if args.ticId is not None:
        path = os.path.abspath('twexo_temp_{0}_{1:016d}.html'.format(DATE_STR,args.ticId))
        ModeHeader = 'Using TIC: {0}'.format(useTIC)
    if args.name is not None:
        # strip white space and only keep regular characters to protect against
        #  special characters that would be bad to put into filenames also clip lenght

        useName = safe_char(args.name[0])
        if (len(useName)>30):
            useName = useName[0:11]
        path = os.path.abspath('twexo_temp_{0}_{1}.html'.format(DATE_STR,useName))
        ModeHeader = 'From {0} Using TIC: {1}'.format(args.name[0], useTIC)
    if args.coord is not None:
        path = os.path.abspath('twexo_temp_{0}_{1:016d}.html'.format(DATE_STR,useTIC))
        ModeHeader = 'From input coordinates Using TIC: {0}'.format(useTIC)

    ticPos = 'Using TIC catalog position {0} {1} [J2000.0; epoch 2000.0]'.format(starRa, starDec)
    twoMassId = '2MASS J{0} From TIC'.format(star2mass)
    closeTICN = '{0} TIC entries within {1} arcsec of target {2}'.format(len(ticList)-1, SEARCH_RAD, useTIC)
    neighTIC = []
    for i, curTIC in enumerate(ticList[1:]):
        neighTIC.append('{0:d} Sep [arcsec]: {1:8.3f}<br>'.format(curTIC, seps[i+1].arcsecond))     
    neighTICStr = ' '.join(neighTIC)

    # We had all the HTML strings, put them in a dictionary that will
    #  will be used for replacement in HTML template below        
    htmlDict = {'neighTIC':neighTICStr, 'closeTICN':closeTICN, \
                'twoMassId':twoMassId, 'ticPos':ticPos, \
                'ModeHeader':ModeHeader, 'useTIC':useTIC, \
                'exofopURL':exofopURL, 'simbadURL':simbadURL, 'vizURL':vizURL, \
                'mstURL':mstURL, 'irsaURL':irsaURL, 'esoURL':esoURL, \
                'toicheckstr':toicheckstr, 'toihdr':toihdr}
    #HTML TEMPLATE
    template = """
<html>
<head>
<title>TESS Web Exploder {useTIC}</title>
</head>
<body>
<h1>{ModeHeader}</h1>
<h3>{ticPos}</h3>
<h3>{twoMassId}</h3>
<h3>{closeTICN}</h3>
{neighTIC}
<h3>{toihdr}</h3>
{toicheckstr}
<h2>Target Links</h2>
<a href="{exofopURL}" target="_blank">ExoFOP</a> |
<a href="{simbadURL}" target="_blank">Simbad</a> |
<a href="{vizURL}" target="_blank">Vizier</a> |
<a href="{mstURL}" target="_blank">MAST TESS Data Holdings</a> |
#<a href="{irsaURL}" target="_blank">IRSA Finderchart</a>
IRSA Finderchart Link Currently Broken |
<a href="{esoURL}" target="_blank">ESO Data Archive Holdings</a> 
</body>
</html>
"""
    # Replace tags in HTML template with the strings in the htmlDict
    page_string = template.format(**htmlDict)
    url = 'file://' + path
    # Write the html to a local file
    with open(path, 'w') as f:
        f.write(page_string)

    # If the user requested a web explode load em all!
    if args.explode:
        webbrowser.open(esoURL, new=2)
        #webbrowser.open(irsaURL, new=2)
        webbrowser.open(mstURL, new=2)
        webbrowser.open(vizURL, new=2)
        webbrowser.open(simbadURL, new=2)
        webbrowser.open(exofopURL, new=2)  


    # Load the webpage
    webbrowser.open(url)
    
        
    
