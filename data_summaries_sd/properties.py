import datashader as ds
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

# Canvas properties
# ------------------------------------------------------------------------------
REGIONS = dict()
REGIONS['Global'] = ((-180.00, 180.00), (-90.00, 90.00))
DEGREE_FACTOR_RESOLUTION = dict()
DEGREE_FACTOR_RESOLUTION['lo_res'] = 1
DEGREE_FACTOR_RESOLUTION['me_res'] = 2
DEGREE_FACTOR_RESOLUTION['hi_res'] = 5

# Datashader aggregations
# ------------------------------------------------------------------------------
DS_AGGREGATIONS = {'counts':ds.count,'max':ds.max,'min':ds.min, 'mean':ds.mean}

# NC files properties
# ------------------------------------------------------------------------------
NC_ENCODINGS = {'latitude': {'dtype': 'int16', 'scale_factor': 0.01,
            '_FillValue': -99999},
             'longitude': {'dtype': 'int16', 'scale_factor': 0.01,
             '_FillValue': -99999},
             'counts': {'dtype': 'int64','_FillValue': -99999},
             'max': {'dtype': 'int32', 'scale_factor': 0.01,
              '_FillValue': -99999},
             'min': {'dtype': 'int32', 'scale_factor': 0.01,
             '_FillValue': -99999},
             'mean': {'dtype': 'int32', 'scale_factor': 0.01,
             '_FillValue': -99999}}
