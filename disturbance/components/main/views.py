from rest_framework import serializers, views, status
from rest_framework.response import Response
from django.conf import settings


class GeocodingAddressSearchTokenView(views.APIView):
    def get(self, request, format=None):
        return Response({"access_token": settings.GEOCODING_ADDRESS_SEARCH_TOKEN})
