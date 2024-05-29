from django.core.management.base import BaseCommand
from django.conf import settings

import time
from datetime import datetime, timedelta
from django.utils import timezone

from disturbance.components.main.models import DASMapLayer
from disturbance.components.proposals.api import get_sqs_url

import requests 
from requests.auth import HTTPBasicAuth 
import json 

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    '''
    NOTE: Script not yet complete - response timeout on large geojson layer_load from KMI
    TODO: either implement script to push through TaskQueue or use the current PROD method - run layer_loader mgt command from SQS shell
    '''
    help = f'Creates/Updates Layer on SQS: ./manage_ds.py create_sqs_layers --layer_name CPT_DBCA_REGIONS --layer_url https://kaartdijin-boodja.dbca.wa.gov.au/api/catalogue/entries/CPT_DBCA_REGIONS/layer/'
           
    def add_arguments(self, parser):
        parser.add_argument('--layer_name', type=str, help='Layer Name', required=False)
        parser.add_argument('--layer_url', type=str, help='Layer URL', required=False)

    def handle(self, *args, **options):

        start_time = time.time()                
        layer_name = options['layer_name']
        layer_url = options['layer_url']
        logger.info(f'Running command {__name__}')

        qs = DASMapLayer.objects.filter(layer_name=layer_name) if layer_name and layer_url else DASMapLayer.objects.all()

        for layer in qs:
            logger.info(f'Updating {layer.layer_url} ...')

            data = {'layer_details': json.dumps({'layer_name': layer.layer_name, 'layer_url': layer.layer_url}), 'system': settings.SYSTEM_NAME_SHORT} 
            url = get_sqs_url(f'add_layer/')
            #url='http://localhost:8002/api/v1/add_layer' 
            resp = requests.post(url=url, data=data, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False, timeout=settings.REQUEST_TIMEOUT*10)

            if resp.status_code != 200:
                logger.error(f'SpatialQuery API call error: {resp.content}')
            #else:
            #    logger.info(f'{resp.json()}')
                

        logger.info(f'Command completed {__name__} (Time Taken {round(time.time() - start_time, 2)} secs)')
        start_time = time.time()                


