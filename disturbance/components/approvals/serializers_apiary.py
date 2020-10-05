from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from disturbance.components.approvals.models import ApiarySiteOnApproval
from disturbance.components.main.utils import get_category, get_tenure, get_region_district


class ApiarySiteOnApprovalGeometrySerializer(GeoFeatureModelSerializer):
    """
    For reading
    """
    id = serializers.IntegerField(source='apiary_site.id')
    site_guid = serializers.CharField(source='apiary_site.site_guid')
    status = serializers.SerializerMethodField()
    site_category = serializers.SerializerMethodField()
    previous_site_holder_or_applicant = serializers.SerializerMethodField()
    is_vacant = serializers.SerializerMethodField()

    class Meta:
        model = ApiarySiteOnApproval
        geo_field = 'wkb_geometry'
        fields = (
            'id',
            'site_guid',
            'available',
            'wkb_geometry',
            'site_category',
            'status',
            'is_vacant',
            # 'stable_coords',
            'previous_site_holder_or_applicant',
        )

    def get_is_vacant(self, obj):
        return obj.apiary_site.is_vacant

    def get_status(self, obj):
        return obj.site_status

    def get_site_category(self, obj):
        return obj.site_category.name

    def get_previous_site_holder_or_applicant(self, obj):
        try:
            relevant_applicant_name = obj.approval.relevant_applicant_name
            return relevant_applicant_name
        except:
            return ''


class ApiarySiteOnApprovalGeometrySaveSerializer(GeoFeatureModelSerializer):
    """
    For saving
    """
    def validate(self, attrs):
        # TODO: validate 3km radius, etc
        site_category = get_category(attrs['wkb_geometry'])
        attrs['site_category'] = site_category
        return attrs

    class Meta:
        model = ApiarySiteOnApproval
        geo_field = 'wkb_geometry'
        fields = (
            'wkb_geometry',
            'site_category',
        )


class ApiarySiteOnApprovalLicenceDocSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='apiary_site.id')
    # site_category = serializers.CharField(source='site_category.name')
    site_category = serializers.SerializerMethodField()
    coords = serializers.SerializerMethodField()
    tenure = serializers.SerializerMethodField()
    region_district = serializers.SerializerMethodField()

    class Meta:
        model = ApiarySiteOnApproval

        fields = (
            'id',
            'coords',
            'site_category',
            'tenure',
            'region_district',
        )

    def get_site_category(self, apiary_site_on_approval):
        site_category = apiary_site_on_approval.site_category
        return site_category.display_name

    def get_tenure(self, apiary_site_on_approval):
        try:
            res = get_tenure(apiary_site_on_approval.wkb_geometry)
            return res
        except:
            return ''

    def get_region_district(self, apiary_site_on_approval):
        try:
            res = get_region_district(apiary_site_on_approval.wkb_geometry)
            return res
        except:
            return ''

    def get_coords(self, apiary_site_on_approval):
        try:
            # geometry_condition = self.context.get('geometry_condition', ApiarySite.GEOMETRY_CONDITION_APPROVED)
            # if geometry_condition == ApiarySite.GEOMETRY_CONDITION_APPLIED:
            #     return {'lng': apiary_site.wkb_geometry_applied.x, 'lat': apiary_site.wkb_geometry_applied.y}
            # elif geometry_condition == ApiarySite.GEOMETRY_CONDITION_PENDING:
            #     return {'lng': apiary_site.wkb_geometry_pending.x, 'lat': apiary_site.wkb_geometry_pending.y}
            # else:
            #     return {'lng': apiary_site.wkb_geometry.x, 'lat': apiary_site.wkb_geometry.y}
            return {'lng': apiary_site_on_approval.wkb_geometry.x, 'lat': apiary_site_on_approval.wkb_geometry.y}
        except:
            return {'lng': '', 'lat': ''}
