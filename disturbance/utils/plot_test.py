from django.conf import settings
from disturbance.components.proposals.models import Proposal

#from sqs.utils.das_tests.equals import checkbox_equals
import geopandas as gpd
import json
import requests
import subprocess
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('TkAgg')
#matplotlib.use('GTKAgg')
#matplotlib.use('Agg')

import logging
logger = logging.getLogger(__name__)


def plot_buffer(proposal_id, buffer=20000):
    '''
    Converts Polar Projection from EPSG:4326 (in deg) to Cartesian Projection (in meters),
    add buffer (in meters) to the new projection, then reverts the buffered polygon to 
    the original projection

    from disturbance.utils.plot_buffer import plot_buffer
    plot_buffer(1772, 2000)
    '''
    mpl.use('WebAgg') # opens a browser window with the plot and is fully interactive

    p = Proposal.objects.get(id=proposal_id)
    polygon_geojson = p.shapefile_json

    mpoly = gpd.read_file(json.dumps(polygon_geojson))
    crs_orig = mpoly.crs.srs

    mpoly_cart = mpoly.to_crs(settings.CRS_CARTESIAN)
    mpoly_cart_buffer = mpoly_cart.buffer(buffer)

    mpoly_polar_buffer = mpoly_cart_buffer.to_crs(crs_orig)

    fig, ax = plt.subplots(figsize=(10,10))

    mpoly.plot(ax=ax, color='yellow', alpha=.5)
    mpoly_polar_buffer.plot(ax=ax, color='blue', alpha=.5)

    plt.show()

def round_coordinates(geom, ndigits=2):
    ''' Rounds the grometry coords to given number of decimal places
       
        https://gis.stackexchange.com/questions/321518/rounding-coordinates-to-five-decimals-in-geopandas 
    '''
    
    from shapely.ops import transform
    def _round_coords(x, y, z=None):
        x = round(x, ndigits)
        y = round(y, ndigits)

        if z is not None:
            z = round(x, ndigits)
            return (x,y,z)
        else:
            return (x,y)
   
    return transform(_round_coords, geom)

def add_buffer(mpoly, buffer_size):
    '''
    Converts Polar Projection from EPSG:xxxx (eg. EPSG:4326) in deg to Cartesian Projection (in meters),
    add buffer (in meters) to the new projection, then reverts the buffered polygon to 
    the original projection

    Input: buffer_size -- in meters

    Returns the the original polygon, perimeter increased by the buffer size
    '''
    if buffer_size:
        try:
            buffer_size = float(buffer_size)
            crs_orig =  mpoly.crs.srs

            # convert to new projection so that buffer can be added in meters
            mpoly_cart = mpoly.to_crs(settings.CRS_CARTESIAN)
            mpoly_cart['geometry'] = mpoly_cart['geometry'].buffer(buffer_size)

            # revert to original projection
            mpoly_cart.to_crs(crs_orig, inplace=True)

            return mpoly_cart

        except Exception as e:
            logger.error(f'Error adding buffer {buffer_size} to polygon\n{e}')

    return mpoly


def plot_overlay(proposal_id, layer_name, column_name, buffer_size=None):
    '''
    import requests
    from disturbance.utils.plot_buffer import plot3
    plot_overlay(1772, 'CPT_LOCAL_GOVT_AREAS', 'LGA_LGA_NAME')
    plot_overlay(1778, 'CPT_FOREST_BLOCK_COMPT', 'SFC_COMPARTMENT')

    plot_overlay(1780, 'CPT_FOREST_BLOCK_COMPT', 'SFC_COMPARTMENT', buffer_size=0)
    plot_overlay(1780, 'CPT_THREATENED_PRIO_FLORA', 'TPF_POPSTATUS', buffer_size=0

    '''

    mpl.use('WebAgg') # opens a browser window with the plot and is fully interactive
 
    p = Proposal.objects.get(id=proposal_id)
    polygon_geojson = p.shapefile_json

    resp = requests.get(f'http://localhost:8003/api/spatial_query/{layer_name}/get_sqs_layer_geojson')
    layer_geojson = resp.json()

    #layer_gdf = gpd.GeoDataFrame.from_features(layer_geojson)
    #polygon_gdf = gpd.GeoDataFrame.from_features(polygon_geojson)
    layer_gdf = gpd.read_file(json.dumps(layer_geojson))
    crs_layer =  layer_gdf.crs.srs

    polygon_gdf = gpd.read_file(json.dumps(polygon_geojson))

    if buffer_size:
        polygon_gdf = add_buffer(polygon_gdf, buffer_size=buffer_size)

    print(f'layer:   {layer_gdf.crs}')
    print(f'polygon: {polygon_gdf.crs}')

    if polygon_gdf.crs.srs.lower() != crs_layer.lower():
        polygon_gdf.to_crs(crs_layer, inplace=True)

    #layer_gdf.to_crs(settings.CRS, inplace=True)

    print(f'layer:   {layer_gdf.crs}')
    print(f'polygon: {polygon_gdf.crs}')

    #fig, ax = plt.subplots(figsize=(10,10))
    overlay_gdf = layer_gdf.overlay(polygon_gdf, how='intersection')
    print(overlay_gdf)
    #print(overlay_gdf.SFC_COMPARTMENT.unique())
    ax = overlay_gdf.plot(cmap='tab10')

    layer_gdf.boundary.plot(ax=ax, color='black', alpha=0.5)
    polygon_gdf.plot(ax=ax, color='darkgreen', alpha=.5)

    layer_gdf['coords'] = layer_gdf['geometry'].apply(lambda x: x.representative_point().coords[:])
    layer_gdf['coords'] = [coords[0] for coords in layer_gdf['coords']]

    for idx, row in layer_gdf.iterrows():
       plt.annotate(text=row[column_name], xy=row['coords'], horizontalalignment='center', color='blue')

    plt.show()

def plot_overlay2(layer_name, column_name):
    '''
    import requests
    from disturbance.utils.plot_buffer import plot3
    plot_overlay('CPT_LOCAL_GOVT_AREAS', 'LGA_LGA_NAME')
    plot_overlay('CPT_FOREST_BLOCK_COMPT', 'SFC_COMPARTMENT')
    '''

    mpl.use('WebAgg') # opens a browser window with the plot and is fully interactive
 
    resp = requests.get(f'http://localhost:8003/api/spatial_query/{layer_name}/get_sqs_layer_geojson')
    layer_geojson = resp.json()
    layer_gdf = gpd.read_file(json.dumps(layer_geojson))

    #polygon_gdf= gpd.read_file('/var/www/sqs/whicher01c.json') # GeoJSON example created by ogr2ogr  from shapefile .shp
    result = subprocess.run(f'{settings.OGR2OGR} -f GeoJSON /vsistdout/ /home/jawaidm/Downloads/Whicher01.shp', capture_output=True, text=True, check=True, shell=True)
    shp_json = json.loads(result.stdout)
    polygon_gdf = gpd.read_file(json.dumps(shp_json))
    print(f'layer:   {layer_gdf.crs}')
    print(f'polygon: {polygon_gdf.crs}')

    #layer_gdf.to_crs(CRS_POLAR, inplace=True)
    #polygon_gdf.to_crs(CRS_POLAR, inplace=True)

    print(f'layer:   {layer_gdf.crs}')
    print(f'polygon: {polygon_gdf.crs}')

    fig, ax = plt.subplots(figsize=(10,10))

    layer_gdf.boundary.plot(ax=ax, color='black', alpha=0.5)
    polygon_gdf.plot(ax=ax, color='darkgreen', alpha=.5)

    layer_gdf['coords'] = layer_gdf['geometry'].apply(lambda x: x.representative_point().coords[:])
    layer_gdf['coords'] = [coords[0] for coords in layer_gdf['coords']]

    for idx, row in layer_gdf.iterrows():
       plt.annotate(text=row[column_name], xy=row['coords'], horizontalalignment='center', color='blue')

    plt.show()

