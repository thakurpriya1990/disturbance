from rest_framework import serializers, views, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

from disturbance.components.main.models import ApiaryGlobalSettings


@api_view(['GET'],)
def deed_poll_url(request):
    deed_poll_url = ApiaryGlobalSettings.objects.get(key=ApiaryGlobalSettings.KEY_PRINT_DEED_POLL_URL)
    return Response(deed_poll_url.value)