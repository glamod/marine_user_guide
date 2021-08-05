#!/usr/bin/env python3
#
#  Needs to run with py env2: bwcause of pandas to_parquet (different to dask to parquet!)
# -*- coding: utf-8 -*-
"""CDM tables full record monthly time series of qi value counts

This script creates a time series with the value counts of a CDM header 
table field.

Input arguments to this script are:
    
    * qi: quality indicator (CDM field) to summarize
    * config_file: configuration file

Arguments from the config_file are:
    
    * dir_data: directory where the CDM table files are stored. This directory
    is assumed to be partitioned in source-deck subdirectories with the table
    files within.
    * dir_out: directory to output the gridded summaries to.
    * start: first year
    * stop: last year
"""
import os
import sys
sys.path.append('..')
import glob
import pandas as pd
import logging
import json

import datetime
from dateutil import rrule

from common import query_cdm 

def value_counts(cdm_table_ym,column,loc_ships,loc_buoys):
    vc = cdm_table_ym[column].value_counts()
    vc.index = [ str(x) for x in vc.index ]
    buoys = cdm_table_ym[column].loc[cdm_table_ym['platform_type'] == 5 ]
    vc_buoys = buoys.value_counts() 
    vc_buoys.index = [ str(x) + '.buoys' for x in vc_buoys.index ]
    ships = cdm_table_ym[column].loc[cdm_table_ym['platform_type'] != 5 ]
    vc_ships = ships.value_counts()
    vc_ships.index = [ str(x) + '.ships' for x in vc_ships.index ]
    nreports = pd.Series(index=['nreports'],data=[len(cdm_table_ym)])
    nreports_ships = pd.Series(index=['nreports.ships'],data=[len(ships)])
    nreports_buoys = pd.Series(index=['nreports.buoys'],data=[len(buoys)])
    
    return pd.concat([nreports,nreports_buoys,nreports_ships,vc,vc_buoys,vc_ships])    

def main():       
       
    logging.basicConfig(format='%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s',
                        level=logging.INFO,datefmt='%Y%m%d %H:%M:%S',filename=None)
    
    config_file = sys.argv[1]
    qi = sys.argv[2]
    
    with open(config_file,'r') as fO:
        config = json.load(fO)
    
    
    dir_data = config['dir_data']
    dir_out = config['dir_out']
    start_int = config['start']
    stop_int = config['stop']
    
    # KWARGS FOR CDM FILE QUERY----------------------------------------------------
    kwargs = {}
    kwargs['dir_data'] = dir_data
    kwargs['cdm_id'] = '*'
    kwargs['columns'] = ['report_id','platform_type']
    kwargs['columns'].append(qi)
    table = 'header'
    
    # CREATE THE MONTHLY STATS ON THE DF PARTITIONS -------------------------------
    counts_df = pd.DataFrame()
    
    start = datetime.datetime(start_int,1,1)
    stop = datetime.datetime(stop_int,12,31)
    for i,dt in enumerate(rrule.rrule(rrule.MONTHLY, dtstart=start, until=stop)):
        date_file = dt.strftime('%Y-%m')
        files_list = glob.glob(os.path.join(dir_data,'*','-'.join([table,date_file]) + '*.psv' ))
        if len(files_list) == 0:
            logging.warning('NO DATA FILES FOR TIME PARTITION {}'.format(date_file))
            continue
    
        sid_dck_list = [ os.path.basename(os.path.dirname(x)) for x in files_list ]
        cdm_table_ym = pd.DataFrame()
        logging.info('PROCESSING TIME PARTITION: {0}. Aggregating {1} sources'.format(date_file,str(len(sid_dck_list))))
        for sid_dck in sid_dck_list:
            cdm_table = query_cdm.query_monthly_table(sid_dck, table, dt.year, dt.month, **kwargs)
            cdm_table.dropna(inplace = True)
            cdm_table_ym = pd.concat([cdm_table_ym,cdm_table], sort = False)
        
        logging.info('PT locs')
        loc_buoys = cdm_table_ym.loc[cdm_table_ym['platform_type'] == 5 ].index 
        loc_ships = cdm_table_ym.loc[cdm_table_ym['platform_type'] != 5 ].index
        
        logging.info('qi counts by PT')
        countsi = value_counts(cdm_table_ym,qi,loc_ships,loc_buoys)
        counts_df = pd.concat([counts_df,pd.DataFrame(data=[countsi.values],index=[dt],columns = countsi.index.values)])
        
        if i%120 == 0:
            out_file = os.path.join(dir_out,qi + '-ts_part.psv')
            counts_df.to_csv(out_file,sep='|')
    
    
    out_file = os.path.join(dir_out,qi + '-ts.psv')    
    counts_df.to_csv(out_file,sep='|')

if __name__ == "__main__":
    main()
