from rest_framework_gis.serializers import GeoFeatureModelSerializer

from disturbance.components.approvals.models import ApiarySiteOnApproval


class ApiarySiteOnApprovalSerializer(GeoFeatureModelSerializer):
    """
    For reading
    """

    class Meta:
        model = ApiarySiteOnApproval
        geo_field = 'wkb_geometry'
        fields = (
            'wkb_geometry',
            'site_status'
        )


class ApiarySiteOnApprovalSaveSerializer(GeoFeatureModelSerializer):
    """
    For saving
    """

    class Meta:
        model = ApiarySiteOnApproval
        geo_field = 'wkb_geometry'
        fields = (
            'wkb_geometry'
        )


