# Common data model table files properties
# ------------------------------------------------------------------------------
CDM_TABLES = ['header','observations-at','observations-sst',
              'observations-dpt','observations-wbt',
              'observations-wd','observations-ws',
              'observations-slp']

CDM_DTYPES = {'latitude':'float32','longitude':'float32',
              'observation_value':'float32','date_time':'object',
              'quality_flag':'int8','crs':'int','report_quality':'int8',
              'report_id':'object'}

CDM_DELIMITER = '|'

CDM_NULL_LABEL = 'null'
