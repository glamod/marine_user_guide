import datashader as ds
import cartopy.crs as ccrs

# Some plotting options
font_size_legend = 11
axis_label_size = 11
tick_label_size = 9
title_label_size = 14
figsize=(9, 14)

# Map properties
mosaic_map = {}
mosaic_map['coastline_width'] = 0.3
mosaic_map['grid_width'] = 0.7
mosaic_map['grid_label_size'] = 6
mosaic_map['colorbar_title_size'] = 9
mosaic_map['colorbar_label_size'] = 7
mosaic_map['colorbar_width'] = 6

single_map = {}
single_map['coastline_width'] = 1
single_map['grid_width']  = 0.7
single_map['grid_label_size']  = 12
single_map['colorbar_title_size']  = 11
single_map['colorbar_label_size']  = 12
single_map['colorbar_width'] = 4

projections = {}
projections['PlateCarree'] = ccrs.PlateCarree()
projections['Robinson'] = ccrs.Robinson()

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
