from datetime import datetime

import requests
import json
import pytz
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import Distance
from django.core.cache import cache
from django.db import connection, transaction
from django.db.models.query_utils import Q
from rest_framework import serializers
from ledger.accounts.models import EmailUser

from rest_framework.renderers import JSONRenderer
#from disturbance.components.proposals.serializers import SpatialQueryQuestionSerializer

from disturbance.components.main.decorators import timeit
from disturbance.settings import SITE_STATUS_DRAFT, SITE_STATUS_APPROVED, SITE_STATUS_TRANSFERRED, RESTRICTED_RADIUS, \
    SITE_STATUS_PENDING, SITE_STATUS_DISCARDED, SITE_STATUS_VACANT, SITE_STATUS_DENIED, SITE_STATUS_CURRENT, \
    SITE_STATUS_NOT_TO_BE_REISSUED, SITE_STATUS_SUSPENDED

import logging
logger = logging.getLogger(__name__)


#def retrieve_department_users():
#    try:
#        res = requests.get('{}/api/users?minimal'.format(settings.CMS_URL), auth=(settings.LEDGER_USER,settings.LEDGER_PASS), verify=False)
#        res.raise_for_status()
#        cache.set('department_users',json.loads(res.content).get('objects'),10800)
#    except:
#        raise
#
#
#def get_department_user(email):
#    try:
#        res = requests.get('{}/api/users?email={}'.format(settings.CMS_URL,email), auth=(settings.LEDGER_USER,settings.LEDGER_PASS), verify=False)
#        res.raise_for_status()
#        data = json.loads(res.content).get('objects')
#        if len(data) > 0:
#            return data[0]
#        else:
#            return None
#    except:
#        raise
#


def retrieve_department_users():
    try:
        res = requests.get('{}/api/users?minimal'.format(settings.CMS_URL), auth=(settings.LEDGER_USER,settings.LEDGER_PASS), verify=False)
        res.raise_for_status()
        cache.set('department_users',json.loads(res.content).get('objects'),10800)
    except:
        raise


def get_department_user(email):
    if (EmailUser.objects.filter(email__iexact=email.strip()) and 
            EmailUser.objects.get(email__iexact=email.strip()).is_staff):
        return True
    return False


def to_local_tz(_date):
    local_tz = pytz.timezone(settings.TIME_ZONE)
    return _date.astimezone(local_tz)


def check_db_connection():
    """  check connection to DB exists, connect if no connection exists """
    try:
        if not connection.is_usable():
            connection.connect()
    except Exception as e:
        connection.connect()


def convert_utc_time_to_local(utc_time_str_with_z):
    """
    This function converts datetime str like '', which is in UTC, to python datetime in local
    """
    if utc_time_str_with_z:
        # Serialized moment obj is supposed to be sent. Which is UTC timezone.
        date_utc = datetime.strptime(utc_time_str_with_z, '%Y-%m-%dT%H:%M:%S.%fZ')
        # Add timezone (UTC)
        date_utc = date_utc.replace(tzinfo=pytz.UTC)
        # Convert the timezone to TIME_ZONE
        date_perth = date_utc.astimezone(pytz.timezone(settings.TIME_ZONE))
        return date_perth
    else:
        return utc_time_str_with_z


def get_template_group(request):
    return 'das'


def _get_params(layer_name, coords):
    return {
        'SERVICE': 'WMS',
        'VERSION': '1.1.1',
        'REQUEST': 'GetFeatureInfo',
        'FORMAT': 'image/png',
        'TRANSPARENT': True,
        'QUERY_LAYERS': layer_name,
        'STYLES': '',
        'LAYERS': layer_name,
        'INFO_FORMAT': 'application/json',
        'FEATURE_COUNT': 1,  # Features should not be overwrapped
        'X': 50,
        'Y': 50,
        'SRS': 'EPSG:4283',
        'WIDTH': 101,
        'HEIGHT': 101,
        'BBOX': str(coords[0] - 0.0001) + ',' + str(coords[1] - 0.0001) + ',' + str(coords[0] + 0.0001) + ',' + str( coords[1] + 0.0001),
    }

def get_feature_in_wa_coastline_original(wkb_geometry):
    return get_feature_in_wa_coastline(wkb_geometry, False)


@timeit
def get_feature_in_wa_coastline_smoothed(wkb_geometry):
    return get_feature_in_wa_coastline(wkb_geometry, True)


def get_feature_in_wa_coastline(wkb_geometry, smoothed):
    from disturbance.components.main.models import WaCoast

    try:
        features = WaCoast.objects.filter(wkb_geometry__contains=wkb_geometry, smoothed=smoothed)
        if features:
            return features[0]
        else:
            return None
    except:
        return None


def get_feature_in_wa_coastline_kmi(wkb_geometry):
    try:
        URL = 'https://kmi.dpaw.wa.gov.au/geoserver/public/wms'
        coords = wkb_geometry.get_coords()
        PARAMS = _get_params('public:wa_coast_pub', coords)
        res = requests.get(url=URL, params=PARAMS)
        geo_json = res.json()
        feature = None
        if len(geo_json['features']) > 0:
            feature = geo_json['features'][0]
        return feature
    except:
        return None


def get_tenure(wkb_geometry):
    try:
        URL = 'https://kmi.dpaw.wa.gov.au/geoserver/public/wms'
        coords = wkb_geometry.get_coords()
        PARAMS = _get_params('public:dpaw_lands_and_waters', coords)
        res = requests.get(url=URL, params=PARAMS)
        geo_json = res.json()
        tenure_name = ''
        if len(geo_json['features']) > 0:
            tenure_name = geo_json['features'][0]['properties']['tenure']
        return tenure_name
    except:
        return ''


def get_region_district(wkb_geometry):
    from disturbance.components.main.models import RegionDbca
    from disturbance.components.main.models import DistrictDbca

    try:
        regions = RegionDbca.objects.filter(wkb_geometry__contains=wkb_geometry, enabled=True)
        districts = DistrictDbca.objects.filter(wkb_geometry__contains=wkb_geometry, enabled=True)
        text_arr = []
        if regions:
            text_arr.append(regions.first().region_name)
        if districts:
            text_arr.append(districts.first().district_name)

        ret_text = '/'.join(text_arr)
        return ret_text
    except:
        return ''


def handle_validation_error(e):
    # if hasattr(e, 'error_dict'):
    #     raise serializers.ValidationError(repr(e.error_dict))
    # else:
    #     raise serializers.ValidationError(repr(e[0].encode('utf-8')))
    if hasattr(e, 'error_dict'):
        raise serializers.ValidationError(repr(e.error_dict))
    else:
        if hasattr(e, 'message'):
            raise serializers.ValidationError(e.message)
        else:
            raise


def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def custom_strftime(format_str, t):
    return t.strftime(format_str).replace('{S}', str(t.day) + suffix(t.day))


