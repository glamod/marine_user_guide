#!/usr/bin/env python3
#
#  Needs to run with py env2: bwcause of pandas to_parquet (different to dask to parquet!)
# -*- coding: utf-8 -*-
"""CDM tables full record monthly time series of qi value counts

This script creates a time series with the value counts of a CDM header 
table field.

Input arguments to this script are:
    
    * sid-dck: source deck to process
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
    
    
    sid_dck = sys.argv[1]
    qi = sys.argv[2]
    config_file = sys.argv[3]
    
    with open(config_file,'r') as fO:
        config = json.load(fO)
        
    dir_out = os.path.join(config['dir_out'],sid_dck)
    
    
#    dir_data = config['dir_data']
#    dir_out = config['dir_out']
#    start_int = config['start']
#    stop_int = config['stop']
    
    start = datetime.datetime(config.get('start',1600),1,1)
    stop = datetime.datetime(config.get('stop',2100),12,1)
    
    # KWARGS FOR CDM FILE QUERY------------------------------------------------
    kwargs = {}
    kwargs['dir_data'] = config['dir_data']
    kwargs['cdm_id'] = '*'
    kwargs['columns'] = ['report_id','platform_type']
    kwargs['columns'].append(qi)
    table = 'header'
    
    # CREATE THE MONTHLY STATS ON THE DF PARTITIONS ---------------------------
    counts_df = pd.DataFrame()
    files_list = sorted(glob.glob(os.path.join(config['dir_data'],sid_dck,'-'.join([table,'????','??',kwargs['cdm_id']])) + '.psv' ))
    no_files = len(files_list)
    if no_files == 0:
        logging.error('NO DATA FILES FOR HEADER TABLE IN DIR {}'.format(os.path.join(config['dir_data'],sid_dck)))
        sys.exit(1)

    for i,file in enumerate(files_list):
        yyyy,mm = os.path.basename(file).split(table)[1].split('-')[1:3]
        logging.info('Processing file {0} of {1}: {2}-{3}'.format(str(i+1),str(no_files),yyyy,mm))
        dt = datetime.datetime(int(yyyy),int(mm),1)
        if dt < start or dt > stop:
            logging.info('File {} out of requested period'.format(file))
            continue

        cdm_table = query_cdm.query_monthly_table(sid_dck, table, dt.year, dt.month, **kwargs)
        cdm_table.dropna(inplace = True)
        
        logging.info('PT locs')
        loc_buoys = cdm_table.loc[cdm_table['platform_type'] == 5 ].index 
        loc_ships = cdm_table.loc[cdm_table['platform_type'] != 5 ].index
        
        logging.info('qi counts by PT')
        countsi = value_counts(cdm_table,qi,loc_ships,loc_buoys)
        counts_df = pd.concat([counts_df,pd.DataFrame(data=[countsi.values],index=[dt],columns = countsi.index.values)])    
    
    out_file = os.path.join(dir_out,qi + '-ts.psv')    
    counts_df.to_csv(out_file,sep='|')

if __name__ == "__main__":
    main()
