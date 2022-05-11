""" This module provides generic end points for using with 
    models that are registered with django reversion.

"""
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

    def get(self, request, app_label, model_name, pk, version_number, **kwargs):
        """ Returns a specific version of any model object
        

            api/history/app_label/model_name>/pk/version_number/

            0 is the most current versions
            1 is one version older
            2 is two older and so on...

        """
        super().get(self)

        logger.info(f'app_label = {app_label}')

        logger.info(f'model_name = {model_name}')

        logger.info(f'pk = {pk}')

        logger.info(f'version_number = {version_number}')

        model = apps.get_model(app_label=app_label, model_name=model_name)

        logger.info(f'model = {model}')

        instance = model.objects.get(pk=int(pk))

        logger.info(f'instance sql = {instance}')

        version = Version.objects.get_for_object(instance)[int(version_number)]

        serialized_version = version.serialized_data

        json_version = json.loads(serialized_version)

        return Response(json_version)

class ReversionViewSet(InternalAuthorizationViewSet):
    """ A viewset that provides useful methods for any model that
        is registered with django reversion

        Authorization: Internal users only.
    """

    # A ModelViewSet needs a queryset so we give it one but
    # never intend to use this for performance reasons
    queryset = Version.objects.all()[:1]

    serializer_class = serializers.Serializer

    def get_queryset(self):
        """  """
        app_label = self.request.GET.get("app_label")
        model_name = self.request.GET.get("model_name")
        instance = apps.get_model(app_label=app_label, model_name=model_name)
        versions = Version.objects.get_for_model(instance)
        return versions

    @detail_route(methods=['GET',])
    def get_version(self, request):
        """ Returns a specific version of any model object
        

            api/reversion/app_label/model_name>/pk/version_number/

            0 is the most current versions
            1 is one version older
            2 is two older and so on...

        """
        app_label = request.GET.get("app_label")

        model_name = request.GET.get("model_name")

        primary_key = request.GET.get("pk")

        version_number = request.GET.get("version_number")

        instance = apps.get_model(app_label=app_label, model_name=model_name).get(primary_key)

        version = Version.objects.get_for_object(instance)[version_number]

        return Response(version)

    @detail_route(methods=['GET'])
    def get_version_differences(self, request, *args, **kwargs):
        """ Returns a json response containing the differences between two
            versions.

            default_mapping may be passed in kwargs if there are any custom
            fields that deepdiff will be comparing.

            See https://deepdiff.readthedocs.io/en/latest/ for more information
            on the default_mapping parameter.

        """
        try:
            newer_version = int(request.GET.get("newer_version"))
            older_version = int(request.GET.get("older_version"))
        except ValueError as exception:
            raise serializers.ValidationError(str(exception))

        instance = self.get_object()

        # Fail if either argument is negative
        if(newer_version<0 or older_version<0):
            raise Exception('The newer_version and older_version arguements must be 0 or higher')

        # Refuse to compare if the newer version is not actually newer
        if newer_version>=older_version:
            raise Exception('The newer_version arguement must be smaller than the older_version \
                argument')

        newer_version = Version.objects.get_for_object(instance)[newer_version]
        older_version = Version.objects.get_for_object(instance)[older_version]

        version_count = Version.objects.get_for_object(instance).count()

        # Complain if either requested version doesn't exist
        if newer_version>=(version_count-1):
            raise IndexError(f'The newer_version you requested "{newer_version}" doesn\'t exist')

        if older_version>(version_count-1):
            raise IndexError(f'The older_version you requested "{older_version}" doesn\'t exist')

        differences = DeepDiff(newer_version.field_dict, older_version.field_dict, ignore_order=\
            True)

        # If no default_mapping was provided in kwargs just handle datetime
        default_mapping = kwargs.get('default_mapping', {datetime.datetime: lambda d: str(d)})

        formatted_differences = json.dumps(json.loads(differences.to_json(default_mapping=\
            default_mapping)),indent=4, sort_keys=True) #[1:-1]

        logger.info('\n\nformatted_differences = \n\n %s', formatted_differences)

        formatted_differences = literal_eval(formatted_differences)

        return Response(formatted_differences)
