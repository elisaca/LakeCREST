# -*- coding: utf-8 -*-

"""This module defines constants which are valid package-wide."""

DEFAULT_VARS = ['lake_surface_water_temperature', 
                'lswt_quality_level', 
                'lake_ice_cover_class']

LSWT_FLAGS = {0: 'unprocessed', 1: 'bad', 2: 'suspect/marginal',
              3: 'intermediate', 4: 'good', 5: 'best'}

DEFAULT_START = '1992-09-26'
DEFAULT_END = '2020-12-31'

VERSION = '2.0.2'

PATH_RAW = 'data/raw'
PATH_EXTRACTED = 'data/extracted'
PATH_INTERP = 'data/interpolated'
PATH_AUXILIARY = 'data/auxiliary'
PATH_OUTPUT = 'data/output'
PATH_DINEOF = 'data/output/DINEOF'
PATH_ABBREV = PATH_AUXILIARY+'/abbreviations.json'

FN_MASK = f'ESA_CCI_static_lake_mask_{VERSION}.nc'
FN_TABLE = 'lakescci_v{VERSION}_data-availability.csv'
URL_TABLE = f'https://climate.esa.int/documents/1637/lakescci_v{VERSION}_data-availability.csv'