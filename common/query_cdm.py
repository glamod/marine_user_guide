#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 16:06:16 2019

We want a set of data descriptors on a monthly lat-lon box grid:
    - counts, max, min, mean
    
We want to have the stats for the qced and not qced thing
    
We want to save that to a nc file to open afterwards in notebooks 
and inspect further or to create static images (maps, plots, etc....) for reports

We are not doing it on the notebooks because we are running these interactively
 and these depend on the changing memo availability of the sci servers.
An alternative will be to run the notebook as a bsub job, but we would need
to know before hand, our memo requirements.

When we have experience with this, we can add the option to (re)compute the nc
 file in the notebook.


We use datashader to create the spatial aggregates because dask does not support
dataframe.cut, which is essential to do a flexible groupby coordinates. We could
groupby(int(coordinates)), but the we would be limited to 1degree boxes, which 
is not bad, but we don't wnat to be limited.  

@author: iregon

DEVS:
    This (functions using dask needs to work with env1 in C3S r092019)
    : because of some issues with pyarrow and
    the following with msgpack that had to be downgraded from 0.6.0 (default)
    to 0.5.6 after:
            
    File "msgpack/_unpacker.pyx", line 187, in msgpack._cmsgpack.unpackb
    ValueError: 1281167 exceeds max_array_len(131072)
    See https://github.com/tensorpack/tensorpack/issues/1003
"""

import os
import sys
import pandas as pd
import glob
import logging
from . import cdm_properties as properties



# SOME COMMON PARAMS ----------------------------------------------------------
FILTER_PIVOT = 'report_id'


# SOME FUNCTIONS THAT HELP ----------------------------------------------------

def build_pd_query(table,**kwargs):
    logging.basicConfig(format='%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s',
                    level=logging.INFO,datefmt='%Y%m%d %H:%M:%S',filename=None)
    filter_cols = []
    query_list = []
    if kwargs.get('filter_by_values'):
        if table in [ x[0] for x in kwargs['filter_by_values'].keys() ]:
            table_filter = { k:v for k,v in kwargs.get('filter_by_values').items() if table in k[0] }
            filter_cols.extend([ x[1] for x in table_filter.keys() ])
            for k,v in table_filter.items():
                values = [ '"' + x + '"' if type(x) == str else str(x) for x in v ]
                query_list.append(k[1] + ' in [' + ','.join(values) + ']')            
    if kwargs.get('filter_by_range'):        
        if table in [ x[0] for x in kwargs['filter_by_range'].keys() ]:
            table_filter = { k:v for k,v in kwargs.get('filter_by_range').items() if table in k[0] }
            filter_cols.extend([ x[1] for x in table_filter.keys() ])
            for k,v in table_filter.items():
                query_list.append( k[1] + ' >= ' + str(v[0]) + ' & ' + k[1] + ' <= ' + str(v[1]))
      
    return filter_cols,' & '.join(query_list)

def get_data_from_file(sid_dck, table, year, month, dir_data, **kwargs):
    logging.basicConfig(format='%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s',
                    level=logging.INFO,datefmt='%Y%m%d %H:%M:%S',filename=None)
    # See if there is an external table to filter from 
    try:
        tables = []  
        if kwargs.get('filter_by_values'):
            tables.extend(list(set([ x[0] for x in kwargs['filter_by_values'].keys() ])))
        if kwargs.get('filter_by_range'):
            tables.extend(list(set([ x[0] for x in kwargs['filter_by_range'].keys() ])))
        filter_tables = list(set(tables))
        if table in filter_tables:
            tables.remove(table)

        external_filter = False    
        if len(tables) > 0:
            external_filter = True
            for filter_table in tables:
                filter_cols, query = build_pd_query(filter_table,
                                    filter_by_values = kwargs.get('filter_by_values'),
                                    filter_by_range = kwargs.get('filter_by_range'))
                filter_cols.append(FILTER_PIVOT)
                filter_cols = list(set(filter_cols))        
                table_file = '-'.join(filter(None,[filter_table,str(year),str(month).zfill(2),kwargs.get('cdm_id')])) + '.psv'
                table_paths = glob.glob(os.path.join(dir_data,sid_dck,table_file))
                if len(table_paths) > 1:
                    logging.error('Multiple files found for table partition {}'.format(table_file))
                    return 1
                elif len(table_paths) == 0:
                    logging.error('No files found for table partition {}'.format(table_file))
                    return 1
                table_path = table_paths[0]
                iter_csv = pd.read_csv(table_path, usecols=filter_cols,iterator=True, chunksize=300000,delimiter=properties.CDM_DELIMITER)
                df_filter = pd.concat([chunk.query(query)[FILTER_PIVOT] for chunk in iter_csv])
            
        cols, query = build_pd_query(table,
                                    filter_by_values = kwargs.get('filter_by_values'),
                                    filter_by_range = kwargs.get('filter_by_range'))
        cols.extend([FILTER_PIVOT])
        if kwargs.get('columns'):
            cols.extend(kwargs.get('columns'))
            cols = list(set(cols))
        else: # if not specified, read all
            cols = None   
        table_file = '-'.join(filter(None,[table,str(year),str(month).zfill(2),kwargs.get('cdm_id')])) + '.psv'
        table_paths = glob.glob(os.path.join(dir_data,sid_dck,table_file))
        if len(table_paths) > 1:
            logging.error('Multiple files found for table partition {}'.format(table_file))
            return 1
        elif len(table_paths) == 0:
            logging.error('ERROR: No files found for table partition {}'.format(table_file))
            return 1
        table_path = table_paths[0]
        iter_csv = pd.read_csv(table_path, usecols=cols,iterator=True, chunksize=300000,delimiter=properties.CDM_DELIMITER)
        df_list = []
        for chunk in iter_csv:
            if external_filter:
                chunk = chunk.loc[chunk[FILTER_PIVOT].isin(df_filter)]
            if len(query) > 0:
                chunk = chunk.query(query)
            df_list.append(chunk)
        df = pd.concat(df_list)
        # Subset to requested
        if kwargs.get('columns'):
            df = df[kwargs.get('columns')]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        logging.error('Querying data from file', exc_info=True)
        
    return df
    
    
def get_data_from_db():
    return

# FUNCTIONS TO DO WHAT WE WANT ------------------------------------------------
def query_monthly_table(sid_dck, table, year, month, dir_data = None,
                        db_con = None, cdm_id = None, columns = None,
                        filter_by_values = None, 
                        filter_by_range = None):
    """Read monthly table from the marine CDM filesystem or db (not implemented).

    
    Arguments
    ---------
    sid_dck : str
        Source and deck ID (sourceID-deckID)
    table : str
        CDM table to aggregate
    year : int
        Year to aggregate
    month : int
        Month to aggregate
    
    Keyword arguments
    -----------------
    dir_data : str
        The path to the data level in the data release directory (filesystem query)
    db_con : object, optional
        db_con to tables (not avail yet, nor its other filters: source,deck...)
    cdm_id : str, optional
        String with the CDM table partition identifier (if any)
        (<table>-<year>-<month>-<cdm_id>.psv)
    columns : list
        CDM elements to read. Defaults to all.
    filter_by_values : dict, optional
        Dictionary with the {(table,element) :[values]} pairs to filter the data
        with. 
    filter_by_range : dict, optional
        Dictionary with the {(table,element) :[ini, end]} pairs to filter the 
        data with. 
    """
    logging.basicConfig(format='%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s',
                    level=logging.INFO,datefmt='%Y%m%d %H:%M:%S',filename=None) 
    # See this approach to read the data. With this for buoy data large file
    # the normal approach took more or less thes same. But probably
    # we'd benefit here with larger files or column selection...? With all
    # columns did not seem to be much different....
    if dir_data:
        kwargs = {'cdm_id' : cdm_id,'columns' : columns, 
                  'filter_by_values' : filter_by_values, 
                  'filter_by_range' : filter_by_range }
                     
        return get_data_from_file(sid_dck, table, year, month, dir_data, **kwargs)  
    elif db_con:
        return 'Not implemented'
    
    else:
        return 'Must provide a data directory or db connection'
    
    
            
    return
