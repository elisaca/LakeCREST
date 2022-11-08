# -*- coding: utf-8 -*-

from multiprocessing import Pool
from scripts.functions import data_extraction, find_lakeid

# Define lakes of interest
# Extract specific lakes by lakeids
lakeids = [6, 2, 8, 9, 10, 12]

# Extract all lakes
#lakescci_lut = pd.read_csv('data/auxiliary/lakescci_v2.0.2_data-availability.csv')
#lakeids = list(lakescci_lut.id)

# Extract specific lakes by names
#lakenames = ['Michigan']
#lakeids = [find_lakeid(lakename) for lakename in lakenames]

# Set extraction settings
settings = {'variables': ['lake_surface_water_temperature',
                          'lswt_quality_level',
                          'lake_ice_cover_class'], # (list) Variables to extract
            'use_opendap': False,      # (boolean) Download data using oPeNDAP (slow, up to 2sec per day)
            'startdate': '1992-09-26', # (string) Startdate of the timeseries in the form (YYYY-MM-DD)
            'enddate': '2020-09-01',   # (string) Enddate of the timeseries in the form (YYYY-MM-DD)
            'compress': True,          # (boolean) Apply z-lib compression
            'complevel': 4,            # (int) Compression level to use
            'verbose': False,          # (boolean) Print additional status updates
            }

# Multiprocessing settings
n_processes = 4

# Main
if __name__ == '__main__':
    
    if settings['use_opendap']:
        print(f'Start extracting {len(lakeids)} lakes using oPeNDAP (slow)..')
    else:
        print(f'Start extracting {len(lakeids)} lakes from local dataset..')
    
    # Run extraction in multiprocessing pool
    with Pool(processes=n_processes) as p:
        outputs = p.map(data_extraction, map(lambda id: (id, settings), lakeids))