# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 11:05:07 2022

@author: Elisa Calamita, elisa.calamita@eawag.ch

- extract all lake LSWT data from LakeCCI v2.0.1

"""
import multiprocessing
import pandas as pd
from scripts.functions import data_extraction, find_lakeid

# Define lakes of interest
# Extract specific lakes by lakeids
lakeids = [6, 2]

# Extract specific lakes by names
# Note: If lakeids is non-empty this argument will be ignored!
lakenames = []

# Extract all lakes
#lakescci_lut = pd.read_csv('data/lakescci_v201.csv')
#lakeids = list(lakescci_lut.id)

# Set extraction settings
settings = {'variables': ['lake_surface_water_temperature',
                          'lswt_quality_level',
                          'lake_ice_cover_class'],
            'use_opendap': False,      # (boolean) Download the CCI Lakes data using directly oPeNDAP (slow, up to 2sec per day)
            'startdate': '1999-09-01', # (string) Startdate of the timeseries in the form (YYYY-MM-DD)
            'enddate': '2020-09-01',   # (string) Enddate of the timeseries in the form (YYYY-MM-DD)
            'compress': True,          # (boolean) Apply z-lib compression
            'complevel': 4,            # (int) Compression level to use
            'verbose': False,          # (boolean) Print additional status updates
            }

# Multiprocessing settings
n_processes = 4

# Main
if __name__ == '__main__':
  
    # create multiprocessing pool object and set no. of processes
    pool = multiprocessing.Pool()
    pool = multiprocessing.Pool(processes=n_processes)
    
    # Get lakeids from given lakenames
    if not(lakeids):
        lakeids = [find_lakeid(lakename) for lakename in lakenames]
        
    # map the function to the list and pass
    # function and input list as arguments
    outputs = pool.map(data_extraction, map(lambda id: (id, settings), lakeids))
