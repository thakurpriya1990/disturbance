import logging
from rest_framework import viewsets
from rest_framework import views
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

from disturbance.helpers import is_customer, is_internal
from disturbance.components.main.models import ApiaryGlobalSettings

logger = logging.getLogger(__name__)

@api_view(['GET'],)
def deed_poll_url(request):
    deed_poll_url = ApiaryGlobalSettings.objects.get(key=ApiaryGlobalSettings.KEY_PRINT_DEED_POLL_URL)
    return Response(deed_poll_url.value)

class InternalAuthorizationViewSet(viewsets.GenericViewSet): # pylint: disable=too-many-ancestors
    """ This ViewSet adds authorization that only allows internal users to
        return data.
    """
    def get_queryset(self):
        if is_internal(self.request):
            return self.queryset

        raise PermissionDenied()

class InternalAuthorizationView(views.APIView): # pylint: disable=too-many-ancestors
    """ This ViewSet adds authorization that only allows internal users to
        return data.
    """
    def get(self, request):
        """ Deny access to the version history for external users """
        if not is_internal(self.request):
            raise PermissionDenied()
        