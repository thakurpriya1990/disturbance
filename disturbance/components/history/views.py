""" This module provides some useful Mixins for adding django reversion
    functionity to ViewSets.
"""
import logging
import datetime
import json
from ast import literal_eval
from deepdiff import DeepDiff
from rest_framework.decorators import detail_route
from rest_framework import serializers
from rest_framework.response import Response
from reversion.models import Version


from disturbance.components.main.views import InternalAuthorizationViewSet

logger = logging.getLogger(__name__)

class ReversionViewSetMixin(InternalAuthorizationViewSet):
    """ A viewset that provides useful methods for any model that
        is registered with django reversion

        Authorization: Internal users only.
    """
    @detail_route(methods=['GET',])
    def get_version(self, request):
        """ Returns a specific version of any model object

            0 is the most current versions
            1 is one version older
            2 is two older and so on...

        """
        instance = self.get_object()
        version_number = request.GET.get("version_number")

        version = Version.objects.get_for_object(instance)[version_number]

        return Response(version)

    @detail_route(methods=['GET'])
    def version_differences(self, request, *args, **kwargs):
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
