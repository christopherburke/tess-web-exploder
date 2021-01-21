#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 10:53:25 2017

@author: cjburke
"""

# Here are some things for MAST queries of TIC
import sys
import time
import json
try: # Python 3.x
    from urllib.parse import quote as urlencode
    from urllib.request import urlretrieve
except ImportError:  # Python 2.x
    from urllib import pathname2url as urlencode
    from urllib import urlretrieve
try: # Python 3.x
    import http.client as httplib 
except ImportError:  # Python 2.x
    import httplib  

import numpy as np

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


if __name__ == '__main__':
    # Load a list of TICs
    dataBlock = np.genfromtxt('a_list_of_tics.txt', dtype=['i8'])
    getTics = dataBlock['f0']

    # Make a list of TICs using strings
    # This is the key step the list HAS to strings NOT integers
    ticStringList = ['{0:d}'.format(x) for x in getTics]
    
    # Setup mast query
    request = {'service':'Mast.Catalogs.Filtered.Tic', \
               'params':{'columns':'*', 'filters':[{ \
                        'paramName':'ID', 'values':ticStringList}]}, \
                'format':'json', 'removenullcolumns':True}
    
    startTime = time.time()
    while True:
        headers, outString = mastQuery(request)
        outObject = json.loads(outString)
        if outObject['status'] != 'EXECUTING':
            break
        if time.time() - startTime > 30:
            print('Working...')
            startTime = time.time()
        time.sleep(5)
    print('#Returned {0:d} Entries'.format(len(outObject['data'])))
    ticList = [x['ID'] for x in outObject['data']]
    tMags = [x['Tmag'] for x in outObject['data']]
    ras = [x['ra'] for x in outObject['data']]
    decs = [x['dec'] for x in outObject['data']]
    ecliplat = [x['eclat'] for x in outObject['data']]
    ecliplong = [x['eclong'] for x in outObject['data']]
    twomass = [x['TWOMASS'] for x in outObject['data']]
    
    for i in range(len(ticList)):
        str='{0:d} {1:f} {2:f}'.format(ticList[i], ras[i], decs[i])
        print(str)
    

