from datetime import datetime

import requests
import json
import pytz
from django.conf import settings
from django.core.cache import cache
from django.db import connection


def retrieve_department_users():
    try:
       # import ipdb; ipdb.set_trace()
        res = requests.get('{}/api/users?minimal'.format(settings.CMS_URL), auth=(settings.LEDGER_USER,settings.LEDGER_PASS), verify=False)
        res.raise_for_status()
        cache.set('department_users',json.loads(res.content).get('objects'),10800)
    except:
        raise

def get_department_user(email):
    try:
        res = requests.get('{}/api/users?email={}'.format(settings.CMS_URL,email), auth=(settings.LEDGER_USER,settings.LEDGER_PASS), verify=False)
        res.raise_for_status()
        data = json.loads(res.content).get('objects')
        if len(data) > 0:
            return data[0]
        else:
            return None
    except:
        raise

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
