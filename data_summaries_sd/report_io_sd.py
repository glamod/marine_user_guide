#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 10:18:42 2019


@author: iregon
"""

import glob
import datetime
import pandas as pd
import os
import json
import logging
import sys
sys.path.append('..')


from common import query_cdm 

# PARAMS ----------------------------------------------------------------------

COLUMNS = ['ICOADS','PT selection','imma invalid','DT invalid','ID invalid',
           'C3S'] 

kwargs_query = {}
kwargs_query['cdm_id'] = '*'
table_query = 'header'

## END PARAMS ------------------------------------------------------------------

#------------------------------------------------------------------------------

def main():   
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    sid_dck = sys.argv[1]
    config_file = sys.argv[2]

    with open(config_file,'r') as fO:
        config = json.load(fO)  
        
    kwargs_query['dir_data'] = config['dir_data']
    periods_file = config['periods_file']
    
    sd_paths = {}
    sd_paths['dir_data'] = os.path.join(config['dir_data'],sid_dck)
    sd_paths['dir_out'] = os.path.join(config['dir_out'],sid_dck)
    sd_paths['level1a_ql'] = os.path.join(config['dir_level1a_ql'],sid_dck)
    sd_paths['level1c_ql'] = os.path.join(config['dir_level1c_ql'],sid_dck)
    
    with open(periods_file,'r') as fO:
        periods = json.load(fO) 
   
    # Compatibility user manual periods-config file with single release periods file 
    if periods.get('sid_dck'):    
        yr_ini = min(periods['sid_dck'][sid_dck]['year_init'].values())
        yr_end = max(periods['sid_dck'][sid_dck]['year_end'].values())
    else:
        yr_ini = int(periods[sid_dck]['year_init'])
        yr_end = int(periods[sid_dck]['year_end'])
    
    # Initialize the structure where the TSs is stored
    index = pd.date_range(start=datetime.datetime(int(yr_ini),1,1),end=datetime.datetime(int(yr_end),12,1),freq='MS')
    df = pd.DataFrame(index=index,columns = COLUMNS)
         
    # Loop through time range:
    for date in index:
        yr = date.year
        mm = date.month
        yr_mo = date.strftime('%Y-%m')
       

        logging.info('Processing {}'.format(yr_mo)) 
        # C3S data counts
        hdr_path = os.path.join(sd_paths['dir_data'],'-'.join(['header',str(yr),str(mm).zfill(2)]) + '-*.psv')
        hdr_files = glob.glob(hdr_path)
        if len(hdr_files) > 1:
            logging.error('Multiple files found for {0}-{1}'.format(str(yr),str(mm).zfill(2))) 
            logging.error('{}'.format(','.join(hdr_files)))
            sys.exit(1)
        elif len(hdr_files) == 1:
            df.loc[date,'C3S'] = len(query_cdm.query_monthly_table(sid_dck, table_query, yr, mm, **kwargs_query))
        else:
            logging.warning('No level data found for {0}-{1}'.format(str(yr),str(mm).zfill(2)))  
            
            ['ICOADS','PT selection','imma invalid','DT invalid','ID invalid',
           'C3S']
            
        # Source data: initial reports, number of selected, invalid data model reports
        file = glob.glob(os.path.join(sd_paths['level1a_ql'],'-'.join([str(yr),str(mm).zfill(2)]) + '-*.json'))
        if len(file) == 1:
            with open(file[0]) as fileObj:
                level_dict = json.load(fileObj)  
            level_dict = level_dict.get(yr_mo)
            df.loc[date,'ICOADS'] = level_dict.get('read',{}).get('total')
            df.loc[date,'PT selection'] = level_dict.get('pre_selected',{}).get('total')
            df.loc[date,'imma invalid'] = level_dict.get('invalid',{}).get('total')
            
        # 2. Now data that was dropped because it was invalid: level1c
        file = glob.glob(os.path.join(sd_paths.get('level1c_ql'),'-'.join([str(yr),str(mm).zfill(2)]) + '-*.json'))
        if len(file) > 0:
            with open(file[0]) as fileObj:
                level_dict = json.load(fileObj)
            level_dict = level_dict.get(yr_mo)
            df.loc[date,'DT invalid'] = level_dict.get('invalid',{}).get('report_timestamp')
            df.loc[date,'ID invalid'] = level_dict.get('invalid',{}).get('primary_station_id')

    out_file = os.path.join(sd_paths.get('dir_out'), '-'.join(['io_history','ts.psv']))
    df.dropna(how='all',axis=1).to_csv(out_file,sep='|',index_label='yr-mo')    
    
if __name__ == '__main__':
    main()
