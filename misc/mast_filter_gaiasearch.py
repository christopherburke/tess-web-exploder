
import numpy as np
import sys
import json
import time
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

def mast_filter_gaiasearch(starGaia):
    # Do a MAST  TIC search given a GAIA ID
    # Need to make a string of Gaia ID
    str_Gaia = "{0:d}".format(starGaia)
    startTime = time.time()
    request = {'service':'Mast.Catalogs.Filtered.Tic.Rows', \
                   'params':{'columns':'ID,ra,dec,Tmag,GAIA', \
                             'filters':[ \
                                        {'paramName':'GAIA',\
                                         'values':[str_Gaia]}]},\
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
    
    try:
        x = outObject['data']
        ticId = x[0]['ID']
        ticRa = x[0]['ra']
        ticDec = x[0]['dec']
        ticTmag = x[0]['Tmag']
        ticGaia = x[0]['GAIA']
    except:
        # Try rerunning search
        while True:    
            headers, outString = mastQuery(request)
            outObject = json.loads(outString)
            if outObject['status'] != 'EXECUTING':
                    break
            if time.time() - startTime > 30:
                    print('Working...')
                    startTime = time.time()
            time.sleep(5)
            
        try:
            ticId = x[0]['ID']
            ticRa = x[0]['ra']
            ticDec = x[0]['dec']
            ticTmag = x[0]['Tmag']
            ticGaia = x[0]['GAIA']
        except:
            print('Tried MAST GAIA search twice and failed. Exiting')
            exit()
        

    return ticId, ticRa, ticDec, ticTmag, ticGaia

if __name__ == '__main__':
    # Test Pi Mensae 
    tic, ra, dec, tmag, gaia = mast_filter_gaiasearch(4623036865373793408)
    print('TIC: ',tic)
    print('RA: ',ra)
    print('Dec: ',dec)
    print('Tmag: ',tmag)
    print('GAIA ID: ',gaia)
    
