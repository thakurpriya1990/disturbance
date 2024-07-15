from datetime import datetime

import requests
import json
import pytz
from django.conf import settings
#from django.db.models.query_utils import Q
from rest_framework import serializers

from rest_framework.renderers import JSONRenderer


import logging
logger = logging.getLogger(__name__)


class SpatialQueryBuilder():
    def __init__(self, proposal, url='http://localhost:8002/api/layers/das/spatial_query.json', queryset=None):
        self.proposal = proposal
        self.url = url
        self.queryset = queryset

        self.grouped_layers = self.get_questions_grouped_by_layers()
        self.shapefile_json = self.get_shapefile_json()
        self.sqs_response = None

    def get_questions_grouped_by_layers(self):
        """
        Returns masterlistquestions as JSON, needed to query SQS via API call.
        Questions returned are grouped by layer_name.
        """
        from disturbance.components.proposals.serializers import DTSpatialQueryQuestionSerializer
        from disturbance.components.proposals.models import SpatialQueryQuestion
        queryset = self.queryset
        if not queryset:
            queryset = SpatialQueryQuestion.objects.all()
        serializer = DTSpatialQueryQuestionSerializer(queryset, many=True)
        rendered = JSONRenderer().render(serializer.data).decode('utf-8')
        sqq_json = json.loads(rendered)

        layer_names = [i['layer_name'] for i in sqq_json]
        unique_layer_names = list(set(layer_names))
        unique_layer_list = [{'layer_name': i, 'questions': []} for i in unique_layer_names]
        for layer_dict in unique_layer_list:
            for sqq_record in sqq_json:
                #print(j['layer_name'])
                if layer_dict['layer_name'] in sqq_record.values():
                    layer_dict['questions'].append(sqq_record)

        return unique_layer_list

    def get_shapefile_json(self):
        """
            a simple rectangle intersecting WA regions [GOLDFIELDS, SOUTH COAST]
        """
        shapefile = '''{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[124.12353515624999,-30.391830328088137],[124.03564453125,-31.672083485607377],[126.69433593749999,-31.615965936476076],[127.17773437499999,-29.688052749856787],[124.12353515624999,-30.391830328088137]]]}}]}'''
        return json.loads(shapefile)

    def run_query(self):
        """
        Executes SQS API request --> response JSON

        Sends to SQS: 
            1. masterlist questions, grouped_by layer, to SQS. SQS response is a JSON object (map)
            2. geojson/polygon
            3. proposal (schema, data, layer_data, add_info_assessor)
        used for lookup by class disturbance.components.proposals.utils.PrefillData

        Example:
            from disturbance.components.main.spatial import SpatialQueryBuilder

            p=Proposal.objects.get(id=1350
            builder = SpatialQueryBuilder(proposal=p)
            builder.run_query()

        """
        try:
            #url = 'http://localhost:8002/api/layers/das/spatial_query.json'
            headers = {'Content-type': 'application/json'}

            masterlist_questions = self.grouped_layers #get_questions_grouped_by_layers()
            shapefile_json = self.shapefile_json #get_shapefile_json()
#            p_schema = self.proposal.schema #get_shapefile_json()
#            p_data = self.proposal.data #get_shapefile_json()
#            p_layer_data = self.proposal.layer_data
#            p_add_info_assessor = self.proposal.add_info_assessor

            sqs_request_data=dict(
                masterlist_questions=masterlist_questions,
                geojson=shapefile_json,
                proposal=dict(
                    id=self.proposal.id,
                    schema=self.proposal.schema,
                    data=self.proposal.data,
                    layer_data=self.proposal.layer_data,
                    add_info_assessor=self.proposal.add_info_assessor,
                )
            )
            res = requests.post(self.url, json=sqs_request_data, headers=headers, verify=False)
            self.sqs_response = res.json()
            return self.sqs_response
        except Exception as e:
            logger.error(f'Error Querying SQS: {e}')

#    def find(self, question, answer, widget_type):
#        """
#        Checks if question-answer combination is found in JSON map 'self.sqs_response' (SQS API response JSON)
#
#        Example:
#            self.find(question='2.0 What is the land tenure or classification?', answer='National park') --> returns label list
#
#            for Checkbox:
#                sqs_values = [self.sqs_builder.find(question=item['label'], answer=child['label']) for child in item['children']] --> --> ['cb_label1', 'cb_label2', ...]
#
#            for Multi-Select:
#                sqs_value=[self.sqs_builder.find(question=item['label'], answer=option['label']) for option in item['options']] --> ['ms_label1', 'ms_label2', ...]
#        """
#        try:
#            for _dict in self.sqs_response:
#                if widget_type in ['checkbox', 'multi-select', 'radiobuttons', 'select']:
#                    if _dict['question']==question and _dict['answer']==answer:
#                        return _dict['assessor_answer'] if widget_type=='radiobuttons' else _dict['answer']
#                elif widget_type == 'other':
#                    if question==_dict['question']:
#                        return _dict.get('proponent_answer') if _dict['visible_to_proponent'] else _dict.get('assessor_answer')
#        except Exception as e:
#            logger.error(f'Error Finding Question/Answer comination in SQS Response JSON: {question}/{answer}\n{e}')
#
#        return None


