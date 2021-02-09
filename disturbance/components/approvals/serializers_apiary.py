from ledger.accounts.models import EmailUser
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from disturbance.components.approvals.models import ApiarySiteOnApproval
from disturbance.components.main.utils import get_category, get_tenure, get_region_district, get_status_for_export
from disturbance.components.organisations.models import Organisation


class ApiarySiteOnApprovalMinimalGeometrySerializer(GeoFeatureModelSerializer):
    id = serializers.IntegerField(source='apiary_site__id')
    status = serializers.CharField(source='site_status')
    site_category = serializers.CharField(source='site_category__name')
    is_vacant = serializers.BooleanField(source='apiary_site__is_vacant')
    site_guid = serializers.CharField(source='apiary_site__site_guid')

    class Meta:
        model = ApiarySiteOnApproval
        geo_field = 'wkb_geometry'
        fields = (
            'id',
            'is_vacant',
            'wkb_geometry',
            'site_category',
            'status',
            'site_guid',
        )

class ApiarySiteOnApprovalGeometrySerializer(GeoFeatureModelSerializer):
    """
    For reading
    """
    id = serializers.IntegerField(source='apiary_site.id')
    site_guid = serializers.CharField(source='apiary_site.site_guid')
    status = serializers.CharField(source='site_status')
    site_category = serializers.CharField(source='site_category.name')
    previous_site_holder_or_applicant = serializers.SerializerMethodField()
    is_vacant = serializers.BooleanField(source='apiary_site.is_vacant')
    stable_coords = serializers.SerializerMethodField()

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
            'stable_coords',
            'previous_site_holder_or_applicant',
        )

    def get_stable_coords(self, obj):
        return obj.wkb_geometry.get_coords()

    def get_previous_site_holder_or_applicant(self, obj):
        try:
            relevant_applicant_name = obj.approval.relevant_applicant_name
            return relevant_applicant_name
        except:
            return ''


class ApiarySiteOnApprovalGeometryExportSerializer(ApiarySiteOnApprovalGeometrySerializer):
    status = serializers.SerializerMethodField()
    category = serializers.CharField(source='site_category.name')
    surname = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    telephone = serializers.SerializerMethodField()
    mobile = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    organisation_name = serializers.SerializerMethodField()

    class Meta(ApiarySiteOnApprovalGeometrySerializer.Meta):
        fields = (
            'status',
            'category',
            'surname',
            'first_name',
            'address',
            'telephone',
            'mobile',
            'email',
            'organisation_name',
        )

    def get_organisation_name(self, relation):
        relevant_applicant = relation.approval.relevant_applicant
        if isinstance(relevant_applicant, Organisation):
            return relevant_applicant.organisation.name
        else:
            return ''

    def get_status(self, relation):
        return get_status_for_export(relation)

    # def get_category(self, relation):
    #     return relation.site_category.name

    def get_surname(self, relation):
        relevant_applicant = relation.approval.relevant_applicant
        if isinstance(relevant_applicant, EmailUser):
            return relevant_applicant.last_name
        else:
            return ''

    def get_first_name(self, relation):
        relevant_applicant = relation.approval.relevant_applicant
        if isinstance(relevant_applicant, EmailUser):
            return relevant_applicant.first_name
        else:
            return ''

    def get_address(self, relation):
        try:
            address = relation.approval.relevant_applicant_address
            return address.summary
        except:
            return ''

    def get_telephone(self, relation):
        relevant_applicant = relation.approval.relevant_applicant
        if isinstance(relevant_applicant, EmailUser):
            return relevant_applicant.phone_number
        else:
            return ''

    def get_mobile(self, relation):
        relevant_applicant = relation.approval.relevant_applicant
        if isinstance(relevant_applicant, EmailUser):
            return relevant_applicant.phone_number
        else:
            return ''

    def get_email(self, relation):
        return relation.approval.relevant_applicant_email


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
