""" This module provides generic end points for using with 
    models that are registered with django reversion.

    This api will only if the django apps are in 
    the 'components' directory
"""
import sys
import logging
import datetime
import json
from ast import literal_eval
from deepdiff import DeepDiff
from rest_framework.decorators import detail_route
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from reversion.models import Version
from django.apps import apps

from disturbance.components.main.views import InternalAuthorizationView
from disturbance.components.main.views import InternalAuthorizationViewSet

logger = logging.getLogger(__name__)

class GetVersionView(InternalAuthorizationView):
    """ Will return any serialized verison of any model using any serializer """
    def get(self, request, app_label, component_name, model_name, serializer_name, pk, \
        version_number):
        """ Returns a specific version of any model object

            api/history/app_label/component_name/model_name/serializer_name/pk/version_number/

            Example:

            api/history/disturbance/proposals/Proposal/InternalProposalSerializer/1933/0/

            0 is the most current versions
            1 is one version older
            2 is two older and so on...

        """
        super().get(self)

        logger.info('app_label = %s', app_label)
        logger.info('model_name = %s', model_name)
        logger.info('pk = %s', pk)
        logger.info('version_number =  %s', version_number)
        logger.info('component_name =  %s', component_name)

        model = apps.get_model(app_label=app_label, model_name=model_name)

        logger.info('model = %s', model)

        instance = model.objects.get(pk=int(pk))

        version = Version.objects.get_for_object(instance)[int(version_number)]

        model_class = instance.__class__

        serializer_class = getattr(
            sys.modules[f'{app_label}.components.{component_name}.serializers'],
            serializer_name)

        instance = model_class(**version.field_dict)

        serializer = serializer_class(instance,context={'request':request})

        return Response(serializer.data)

class GetCompareVersionsView(InternalAuthorizationView):
    """ Returns the difference between two specific versions of any model object

        api/history/compare/app_label/model_name/pk/newer_version/older_version/

        Example:

        api/history/compare/disturbance/Proposal/1933/0/1/

        0 is the most current versions
        1 is one version older
        2 is two older and so on...

    """
    def get(self, request, app_label, model_name, pk, newer_version, older_version):
        """ Returns the difference between two specific versions of any model object """
        super().get(self)

        logger.info('app_label = %s', app_label)
        logger.info('model_name = %s', model_name)
        logger.info('pk = %s', pk)

        model = apps.get_model(app_label=app_label, model_name=model_name)

        logger.info('model = %s', model)

        instance = model.objects.get(pk=int(pk))

        newer_version = Version.objects.get_for_object(instance)[int(newer_version)]
        older_version = Version.objects.get_for_object(instance)[int(older_version)]

        differences = DeepDiff(newer_version.field_dict, older_version.field_dict, ignore_order=True)

        default_mapping = {datetime.datetime: lambda d: str(d)}

        formatted_differences = json.dumps(json.loads(differences.to_json(
            default_mapping=default_mapping)), indent=4, sort_keys=True)

        logger.info('\n\nformatted_differences = %s \n\n', formatted_differences)   

        return Response(literal_eval(formatted_differences))

class GetCompareFieldVersionsView(InternalAuthorizationView):
    """ Returns the difference for a specific field
     between two specific versions of any model object

        api/history/compare/app_label/model_name/pk/newer_version/older_version/compare_field/

        Example:

        api/history/compare/disturbance/Proposal/1933/0/2/data/

    """
    def get(self, request, app_label, model_name, pk, newer_version, older_version, compare_field):
        """ Returns the difference between two specific versions of any model object """
        super().get(self)

        logger.info('app_label = %s', app_label)
        logger.info('model_name = %s', model_name)
        logger.info('pk = %s', pk)

        model = apps.get_model(app_label=app_label, model_name=model_name)

        logger.info('model = %s', model)

        instance = model.objects.get(pk=int(pk))

        newer_version = Version.objects.get_for_object(instance)[int(newer_version)]
        older_version = Version.objects.get_for_object(instance)[int(older_version)]

        differences = DeepDiff(newer_version.field_dict[compare_field], older_version.field_dict[compare_field], ignore_order=True)

        default_mapping = {datetime.datetime: lambda d: str(d)}

        formatted_differences = json.dumps(json.loads(differences.to_json(
            default_mapping=default_mapping)), indent=4, sort_keys=True)

        logger.info('\n\nformatted_differences = %s \n\n', formatted_differences)   

        return Response(literal_eval(formatted_differences))