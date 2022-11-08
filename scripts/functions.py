# -*- coding: utf-8 -*-

import os
import sys
from time import time
import pandas as pd
from datetime import datetime
import numpy as np
import netCDF4 as nc4
import json
from scripts import constants as c
from scripts import ROOT
import re

module_path = os.path.abspath(os.path.join('../'))
if module_path not in sys.path:
    sys.path.append(module_path)
    
def valid_variables(variables: list):
    """Check list of variables for validity and return boolean."""
    path_abbreviations = ROOT.joinpath(c.PATH_ABBREV)
    f = open(path_abbreviations)
    abbrev_dict = json.load(f)
    f.close()
    check = all(item in abbrev_dict.keys() for item in variables)
    return check

def get_shortname(variables: list):
    """Get shortnames for variables and return a shortened string for filename."""
    path_abbreviations = ROOT.joinpath(c.PATH_ABBREV)
    f = open(path_abbreviations)
    abbrev_dict = json.load(f)
    f.close()
    shortnames = [abbrev_dict[var] for var in variables]
    shortnames_str = '_'.join(shortnames)
    return shortnames_str

def find_lakeid(lakename: str):
    """Return id corresponding to specified lakename from local-table, revert to web-table or manual input if not available."""
    path_table = ROOT.joinpath(c.PATH_AUXILIARY).joinpath(c.FN_TABLE)
    if path_table.exists():
        df = pd.read_csv(path_table)
    else:
        print('Local lake table not found, trying to use CCI Lakes webtable.')
        try:
            df = pd.read_csv(c.URL_TABLE)
        except:
            lakeid = input('Not able to reach CCI Lakes webtable, '  \
                           f'please enter the lake ID for Lake {lakename} manually: ')
            return lakeid
    ids = df.loc[lambda df: df['name'].str.lower() == lakename.lower()]['id']
    if len(ids) == 0:
        lakeid = int(input(f'No results found for Lake {lakename}, please enter lake ID manually: '))
    elif len(ids) > 1:
        idx = int(input(f'Multiple ID-matches found for Lake {lakename}: {dict(list(zip(range(1, len(ids)+1), ids)))}\n'
              'Please provide the key of the desired lake ID: '))
        while not(idx in range(1, len(ids)+1)):
            idx = int(input(f'Invalid input "{idx}", please give valid key: '))
        lakeid = ids.iloc[idx-1]
    else:
        lakeid = ids.iloc[0]
    return lakeid


def find_lakename(lakeid: int):
    """Return lakename corresponding to specified lakeid from local-table, revert to web-table or manual input if not available."""
    path_table = ROOT.joinpath(c.PATH_AUXILIARY).joinpath(c.FN_TABLE)
    if path_table.is_file():
        df = pd.read_csv(path_table)
    else:
        try:
            df = pd.read_csv(c.URL_TABLE)
        except:
            lakename = input('Not able to reach CCI Lakes webtable, '
                             f'please enter the name for ID{lakeid} manually: ')
            return re.sub(r'[^a-zA-Z\s]', '', lakename)

    names = df.loc[lambda df: df['id'] == lakeid]['name']
    if len(names) == 0:
        lakename = str(input(f'No results found for ID{lakeid}, please enter lakename manually: '))
    elif len(names) > 1:      
        idx = int(input(f'Multiple name-macthes found for Lake ID{lakeid}: {dict(list(zip(range(1, len(names)+1), names)))}\n'
              'Please provide the key of the desired lakename: '))
        while not(idx in range(1, len(names)+1)):
            idx = int(input(f'Invalid input "{idx}", please give valid key: '))
        lakename = names.iloc[idx-1]
    else:
        lakename = names.iloc[0]
    return re.sub(r'[^a-zA-Z\s]', '', lakename)

def extract_lake_subset(lakeid: int = None, lakename: str = None, use_opendap: bool = False,
                        variables: list = c.DEFAULT_VARS,
                        startdate: str = c.DEFAULT_START, enddate: str = c.DEFAULT_END,
                        compress: bool = True, complevel: int = 4, verbose: bool = False, 
                        temp: bool = False, merge_with_lakes: list = []):
    """Take lakeid or lakename and extract corresponding lake and specified variables from local dataset.
    
    Parameters
    ----------
    lakeid : int
        CCI lake id of lake to extract
    lakename : str
        CCI lake name of lake to extract
    use_opendap : bool
        Download the CCI Lakes data using oPeNDAP
    variables : list
        Variables to extract
    startdate : str
        Startdate of the timeseries to extract in the form (YYYY-MM-DD)
    enddate : str
        Enddate of the timeseries to extract in the form (YYYY-MM-DD)
    compress : bool
        Apply z-lib compression
    complevel : int
        Compression level to use
    verbose : bool
        Print status updates to console
    temp : bool
        Put inside temporary folder
    merge_with_lakes : list
        List with additional lakeids to merge with the provided lakeid
    Returns
    -------
    str
        Filename of the extracted subset
    """
    if not (bool(lakeid) or bool(lakename)):
        raise ValueError('At least one of the params lakeid and lakename '
                         'should be passed!')
    elif not lakename:
        lakename = find_lakename(lakeid)
    else:
        lakeid = find_lakeid(lakename)

    if not valid_variables(variables):
        raise ValueError('The passed variable-list is invalid!')

    if verbose:
        print(f'Extracting {variables} for Lake {lakename} (ID{lakeid}) from '
              f'{startdate} to {enddate} from local dataset..')
        
    time_start = time()

    # Define paths
    path_dataset = ROOT.joinpath(c.PATH_RAW).joinpath(f'v{c.VERSION}')
    path_maskfile = ROOT.joinpath(c.PATH_AUXILIARY).joinpath(c.FN_MASK)

    if not (path_maskfile.exists()):
        raise ValueError('The maskfile does not exist!')

    # Get filepaths and filter daterange
    paths_ncfiles = list(path_dataset.rglob(f'*-fv{c.VERSION}.nc'))
    
    allowed_daterange = pd.date_range(startdate, enddate)
    paths_ncfiles_filter = [str(paths_ncfiles[i]).split('-')[-2] for i in range(len(paths_ncfiles))]
    paths_ncfiles_filter = [pd.to_datetime(day_str, yearfirst=True) in allowed_daterange for day_str in
                            paths_ncfiles_filter]
    paths_ncfiles = np.array(paths_ncfiles)[paths_ncfiles_filter]

    # Get mask and distance to shoreline from maskfile and compute bounding box
    nc_mask = nc4.Dataset(path_maskfile, 'r')
    var_lakeid = nc_mask['CCI_lakeid']
    var_dist = nc_mask['distance_to_land']
    
    bool_mask_full = var_lakeid[:] == lakeid
    
    if len(merge_with_lakes) > 0:
        for lakeid_additional in merge_with_lakes:
            bool_mask_full = bool_mask_full | (var_lakeid[:] == lakeid_additional)

    i0 = np.min(np.nonzero(bool_mask_full)[0])
    i1 = np.max(np.nonzero(bool_mask_full)[0])
    j0 = np.min(np.nonzero(bool_mask_full)[1])
    j1 = np.max(np.nonzero(bool_mask_full)[1])

    lat_min, lat_max = nc_mask['lat'][i0], nc_mask['lat'][i1]
    lon_min, lon_max = nc_mask['lon'][j0], nc_mask['lon'][j1]
    
    if verbose:
        print(f'Computed bbox: {lon_min:0.2f}, {lat_min:0.2f} | '
              f'{lon_max:0.2f}, {lat_max:0.2f}')
    
    # Crop mask and distance to shoreline
    bool_mask_crop = bool_mask_full[i0:i1, j0:j1]
    float_dist_crop = np.where(~bool_mask_crop, nc4.default_fillvals['f4'], var_dist[i0:i1, j0:j1])
    lakecells = np.count_nonzero(bool_mask_crop)
    
    # Close maskfile
    nc_mask.close()

    # Define output path
    fn_varnames = get_shortname(variables)
    fn_output = f'ID{lakeid}-{lakename.lower()}-{fn_varnames}-{startdate.replace("-", "")}' \
        f'_{enddate.replace("-", "")}-v{c.VERSION}.extracted.nc'

    if temp:
        path_output = ROOT.joinpath(c.PATH_EXTRACTED).joinpath('temp').joinpath(fn_output)
    else:
        path_output = ROOT.joinpath(c.PATH_EXTRACTED).joinpath(fn_output)

    path_output.parent.mkdir(parents=True, exist_ok=True)

    # Run extraction from web-files using OpENDaP protocol
    if use_opendap:
        # Generate OPeNDAP urls for dataset
        urls = []
        date_range = pd.date_range(start=startdate, end=enddate, freq="D")

        if len(date_range) == 0:
            raise ValueError('Empty timerange provided!')

        lat_range_str = f'[{i0}:1:{i1 - 1}]'
        lon_range_str = f'[{j0}:1:{j1 - 1}]'
        year = list(map(str, date_range.year))
        months = ['{:02d}'.format(month) for month in date_range.month]
        days = ['{:02d}'.format(day) for day in date_range.day]
        var_str = ''

        for var in variables:
            newVar = ',' + var + '[0:1:0]' + lat_range_str + lon_range_str
            var_str += newVar

        for date in range(0, len(date_range)):
            path = ('https://data.cci.ceda.ac.uk/thredds/dodsC/esacci/lakes/data/lake_products/L3S/v'
                    + c.VERSION + '/' + year[date] + '/' + months[date]
                    + '/ESACCI-LAKES-L3S-LK_PRODUCTS-MERGED-'
                    + year[date] + months[date] + days[date] + '-fv' + c.VERSION + '.nc?'
                    + 'lat' + lat_range_str + ',lon' + lon_range_str
                    + ',time[0:1:0]' + var_str)
            urls.append(path)


        # Use first day to recreate necessary dims and vars in output
        with nc4.Dataset(urls[0], 'r') as nc_in, \
             nc4.Dataset(path_output, 'w', format='NETCDF4') as nc_out:

                nc_out.setncatts({k: nc_in.getncattr(k) for k in nc_in.ncattrs()})
                nc_out.setncatts({'lakename': lakename,
                                  'lakeid': lakeid,
                                  'lakecells': lakecells})

                # Create dimensions
                for dname, the_dim in iter(nc_in.dimensions.items()):
                    dim_size = len(the_dim)
                    if dname == 'lat':
                        dim_size = i1 - i0
                    if dname == 'lon':
                        dim_size = j1 - j0
                    nc_out.createDimension(dname, dim_size if not the_dim.isunlimited() else None)

                # Create variables and fill (including dims)
                dims = nc_in.dimensions.keys()
                for v_name, varin in iter(nc_in.variables.items()):
                    if v_name in [*variables, *dims]:
                        outVar = nc_out.createVariable(v_name, varin.datatype, varin.dimensions,
                                                       zlib=compress, complevel=complevel)
                        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
                        if v_name in dims:
                            outVar[:] = varin[:]
                        else:
                            varin_masked = np.ma.masked_array(varin[0, :, :], mask=~bool_mask_crop)
                            outVar[0, :, :] = varin_masked

                # Add lakemask and distance to shoreline as variables
                outVar_mask = nc_out.createVariable('lakemask', 'u1', ('lat', 'lon'),
                                                    zlib=compress, complevel=complevel,
                                                    fill_value=nc4.default_fillvals['u1'])
                outVar_dist = nc_out.createVariable('distance_to_land', 'f4', ('lat', 'lon'),
                                                    zlib=compress, complevel=complevel,
                                                    fill_value=nc4.default_fillvals['f4'])
                outVar_mask.setncatts({
                    '_FillValue': np.array(nc4.default_fillvals['u1'], dtype=np.uint8),
                    'long_name': 'lakemask',
                    'description': 'Lakemask extracted from the CCI Lakes maskfile.'})
                outVar_dist.setncatts({
                    '_FillValue': np.array(nc4.default_fillvals['f4'], dtype=np.float32),
                    'long_name': 'distance to land',
                    'units': 'km',
                    'description': 'Distance to shoreline extracted from the CCI Lakes maskfile.',
                })
                outVar_mask[:, :] = np.where(~bool_mask_crop, 255, 1)
                outVar_dist[:, :] = float_dist_crop

        # Append the rest of the days to output .nc file
        with nc4.Dataset(path_output, 'r+', format='NETCDF4') as nc_out:
            for idx, url in enumerate(urls):
                if idx == 0:
                    # Skip first url
                    continue
                with nc4.Dataset(url, 'r') as nc_in:
                    # Copy variables
                    for v_name, varin in iter(nc_in.variables.items()):
                        if v_name in variables:
                            outVar = nc_out[v_name]
                            varin_masked = np.ma.masked_array(varin[0, :, :], mask=~bool_mask_crop)
                            outVar[idx, :, :] = varin_masked
                    nc_out['time'][idx] = nc_in['time'][0]
                    nc_out.time_coverage_end = nc_in.time_coverage_end

    # Run extraction from local files
    else:
        if len(paths_ncfiles) == 0:
            raise ValueError('No .nc files found for specified timerange!')

        # Use first day to recreate necessary dims and vars in output
        with nc4.Dataset(paths_ncfiles[0], 'r') as nc_in, \
             nc4.Dataset(path_output, 'w', format='NETCDF4') as nc_out:

            # Copy main attributes and add additional ones
            nc_out.setncatts({k: nc_in.getncattr(k) for k in nc_in.ncattrs()})
            nc_out.setncatts({'lakename': lakename,
                              'lakeid': lakeid,
                              'lakecells': lakecells})
            # copy dimensions
            for dname, the_dim in iter(nc_in.dimensions.items()):
                dim_size = len(the_dim)
                if dname == 'lat':
                    dim_size = i1 - i0
                if dname == 'lon':
                    dim_size = j1 - j0
                nc_out.createDimension(dname, dim_size if not the_dim.isunlimited() else None)

            # Copy variables
            dims = nc_in.dimensions.keys()
            for v_name, varin in iter(nc_in.variables.items()):
                if v_name in [*variables, *dims]:
                    outVar = nc_out.createVariable(v_name, varin.datatype, varin.dimensions,
                                                   zlib=compress, complevel=complevel)
                    outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
                    if v_name == 'lat':
                        outVar[:] = varin[i0:i1]
                    elif v_name == 'lon':
                        outVar[:] = varin[j0:j1]
                    elif v_name == 'time':
                        outVar[0] = varin[0]
                    else:
                        varin_clipped = varin[0, i0:i1, j0:j1]
                        varin_masked = np.ma.masked_array(varin_clipped, mask=~bool_mask_crop)
                        outVar[0, :, :] = varin_masked

            # Add lakemask and distance to shoreline as variables
            outVar_mask = nc_out.createVariable('lakemask', 'u1', ('lat', 'lon'),
                                                zlib=compress, complevel=complevel,
                                                fill_value=nc4.default_fillvals['u1'])
            outVar_dist = nc_out.createVariable('distance_to_land', 'f4', ('lat', 'lon'),
                                                zlib=compress, complevel=complevel,
                                                fill_value=nc4.default_fillvals['f4'])
            outVar_mask.setncatts({
                '_FillValue': np.array(nc4.default_fillvals['u1'], dtype=np.uint8),
                'long_name': 'lakemask',
                'description': 'Lakemask extracted from the CCI Lakes maskfile.'})
            outVar_dist.setncatts({
                '_FillValue': np.array(nc4.default_fillvals['f4'], dtype=np.float32),
                'long_name': 'distance to land',
                'units': 'km',
                'description': 'Distance to shoreline extracted from the CCI Lakes maskfile.',
            })
            outVar_mask[:, :] = np.where(~bool_mask_crop, 255, 1)
            outVar_dist[:, :] = float_dist_crop

        # Append the rest of the days to output .nc file
        with nc4.Dataset(path_output, 'r+', format='NETCDF4') as nc_out:
            for idx, filepath in enumerate(paths_ncfiles):
                if idx == 0:
                    continue # Skip first url
                with nc4.Dataset(filepath, 'r') as nc_in:
                    # Copy variables
                    for v_name, varin in iter(nc_in.variables.items()):
                        if v_name in variables:
                            outVar = nc_out[v_name]
                            varin_clipped = varin[0, i0:i1, j0:j1]
                            varin_masked = np.ma.masked_array(varin_clipped, mask=~bool_mask_crop)
                            outVar[idx, :, :] = varin_masked
                    nc_out['time'][idx] = nc_in['time'][0]
                    nc_out.time_coverage_end = nc_in.time_coverage_end

    time_elapsed = time() - time_start
    
    if verbose:
        print(f'Finished extraction and masking after {time_elapsed:0.2f} seconds.')

    return fn_output

def log(str, indent=0):
    out = datetime.now().strftime("%H:%M:%S.%f") + (" " * 3 * (indent + 1)) + str
    with open("log.txt", "a") as file:
        file.write(out + "\n")
    print(out)

def data_extraction(id_and_settings):
    """Take tuple in the form (id, settings) and call extraction function."""
    id = id_and_settings[0]
    settings = id_and_settings[1]

    log("Processing id: {}".format(id))
    
    try:
        fns_ext = extract_lake_subset(lakeid=int(id),
                                      use_opendap=settings['use_opendap'], 
                                      variables=settings['variables'],
                                      startdate=settings['startdate'], 
                                      enddate=settings['enddate'],
                                      compress=settings['compress'], 
                                      complevel=settings['complevel'], 
                                      verbose=settings['verbose'])
    
    except:
        log("Failed to process id: {}".format(id), indent=1)
        
    return