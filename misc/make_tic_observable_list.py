#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 09:14:04 2019

@author: cjburke
"""

import numpy as np
from tess_stars2px import tess_stars2px_function_entry

if __name__ == '__main__':
    # This is an example of using tess_stars2px functionality 
    # from a program rather than the typical command line interface
    # read in multiple targets from a prexisting file and output
    #  how many sectors each target is observable
    #  Also filter for the Year 4 sectors
    
    dataBlock = np.genfromtxt('a_list_of_tics_ras_decs.txt', dtype=['i8','f8','f8'])
    ticids = np.array(dataBlock['f0'])
    ras = np.array(dataBlock['f1'])
    decs = np.array(dataBlock['f2'])
    
    outID, outEclipLong, outEclipLat, outSec, outCam, outCcd, \
            outColPix, outRowPix, scinfo = tess_stars2px_function_entry(
                    ticids, ras, decs)
    

    for curtic in ticids:
        idx = np.where((outID == curtic) & (outSec>=40) & (outSec<=55))[0]
        print('{0:d} {1:d}'.format(curtic, len(idx)))
