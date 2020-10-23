from datetime import datetime

import requests
import json
import pytz
from django.conf import settings
from django.contrib.gis.measure import Distance
from django.core.cache import cache
from django.db import connection
from django.db.models.query_utils import Q
from rest_framework import serializers

from disturbance.components.main.decorators import timeit
from disturbance.components.main.models import CategoryDbca, RegionDbca, DistrictDbca, WaCoast
from disturbance.settings import SITE_STATUS_DRAFT, SITE_STATUS_APPROVED, SITE_STATUS_TRANSFERRED, RESTRICTED_RADIUS, \
    SITE_STATUS_PENDING


def retrieve_department_users():
    try:
       # import ipdb; ipdb.set_trace()
        res = requests.get('{}/api/users?minimal'.format(settings.CMS_URL), auth=(settings.LEDGER_USER,settings.LEDGER_PASS), verify=False)
        res.raise_for_status()
        cache.set('department_users',json.loads(res.content).get('objects'),10800)
    except:
        raise

def get_department_user(email):
    try:
        res = requests.get('{}/api/users?email={}'.format(settings.CMS_URL,email), auth=(settings.LEDGER_USER,settings.LEDGER_PASS), verify=False)
        res.raise_for_status()
        data = json.loads(res.content).get('objects')
        if len(data) > 0:
            return data[0]
        else:
            return None
    except:
        raise

def to_local_tz(_date):
    local_tz = pytz.timezone(settings.TIME_ZONE)
    return _date.astimezone(local_tz)

def check_db_connection():
    """  check connection to DB exists, connect if no connection exists """
    try:
        if not connection.is_usable():
            connection.connect()
    except Exception as e:
        connection.connect()


def convert_utc_time_to_local(utc_time_str_with_z):
    """
    This function converts datetime str like '', which is in UTC, to python datetime in local
    """
    if utc_time_str_with_z:
        # Serialized moment obj is supposed to be sent. Which is UTC timezone.
        date_utc = datetime.strptime(utc_time_str_with_z, '%Y-%m-%dT%H:%M:%S.%fZ')
        # Add timezone (UTC)
        date_utc = date_utc.replace(tzinfo=pytz.UTC)
        # Convert the timezone to TIME_ZONE
        date_perth = date_utc.astimezone(pytz.timezone(settings.TIME_ZONE))
        return date_perth
    else:
        return utc_time_str_with_z


def get_template_group(request):
    web_url = request.META.get('HTTP_HOST', None)
    template_group = None
    if web_url in settings.APIARY_URL:
       template_group = 'apiary'
    else:
       template_group = 'das'
    return template_group


def get_category(wkb_geometry):
    from disturbance.components.proposals.models import SiteCategory
    category = SiteCategory.objects.get(name=SiteCategory.CATEGORY_REMOTE)
    zones = CategoryDbca.objects.filter(wkb_geometry__contains=wkb_geometry)
    if zones:
        category_name = zones[0].category_name.lower()
        if 'south' in category_name and 'west' in category_name:
            category = SiteCategory.objects.get(name=SiteCategory.CATEGORY_SOUTH_WEST)
    return category


def _get_params(layer_name, coords):
    return {
        'SERVICE': 'WMS',
        'VERSION': '1.1.1',
        'REQUEST': 'GetFeatureInfo',
        'FORMAT': 'image/png',
        'TRANSPARENT': True,
        'QUERY_LAYERS': layer_name,
        'STYLES': '',
        'LAYERS': layer_name,
        'INFO_FORMAT': 'application/json',
        'FEATURE_COUNT': 1,  # Features should not be overwrapped
        'X': 50,
        'Y': 50,
        'SRS': 'EPSG:4283',
        'WIDTH': 101,
        'HEIGHT': 101,
        'BBOX': str(coords[0] - 0.0001) + ',' + str(coords[1] - 0.0001) + ',' + str(coords[0] + 0.0001) + ',' + str( coords[1] + 0.0001),
    }


def get_feature_in_wa_coastline_original(wkb_geometry):
    return get_feature_in_wa_coastline(wkb_geometry, False)


def get_feature_in_wa_coastline_smoothed(wkb_geometry):
    return get_feature_in_wa_coastline(wkb_geometry, True)


def get_feature_in_wa_coastline(wkb_geometry, smoothed):
    try:
        features = WaCoast.objects.filter(wkb_geometry__contains=wkb_geometry, smoothed=smoothed)
        if features:
            return features[0]
        else:
            return None
    except:
        return None


def get_feature_in_wa_coastline_kmi(wkb_geometry):
    try:
        URL = 'https://kmi.dpaw.wa.gov.au/geoserver/public/wms'
        coords = wkb_geometry.get_coords()
        PARAMS = _get_params('public:wa_coast_pub', coords)
        res = requests.get(url=URL, params=PARAMS)
        geo_json = res.json()
        feature = None
        if len(geo_json['features']) > 0:
            feature = geo_json['features'][0]
        return feature
    except:
        return None


def get_tenure(wkb_geometry):
    try:
        URL = 'https://kmi.dpaw.wa.gov.au/geoserver/public/wms'
        coords = wkb_geometry.get_coords()
        PARAMS = _get_params('public:dpaw_lands_and_waters', coords)
        res = requests.get(url=URL, params=PARAMS)
        geo_json = res.json()
        tenure_name = ''
        if len(geo_json['features']) > 0:
            tenure_name = geo_json['features'][0]['properties']['tenure']
        return tenure_name
    except:
        return ''


def get_region_district(wkb_geometry):
    try:
        regions = RegionDbca.objects.filter(wkb_geometry__contains=wkb_geometry)
        districts = DistrictDbca.objects.filter(wkb_geometry__contains=wkb_geometry)
        text_arr = []
        if regions:
            text_arr.append(regions.first().region_name)
        if districts:
            text_arr.append(districts.first().district_name)

        ret_text = '/'.join(text_arr)
        return ret_text
    except:
        return ''


def get_vacant_apiary_site():
    from disturbance.components.proposals.models import ApiarySite, ApiarySiteOnProposal

    # ApiarySite with is_vacant==True and making_payment==False
    q = Q(making_payment=True)  # Making payment is True from CC screen to success screen
    q |= Q(site_status=SITE_STATUS_PENDING)  # Once payment success, site_status gets PENDING
    # qs_vacant_site = ApiarySite.objects.filter(is_vacant=True).exclude(apiarysiteonproposal__in=ApiarySiteOnProposal.objects.filter(q)).distinct()
    qs_vacant_site = ApiarySite.objects.filter(is_vacant=True).distinct()
    return qs_vacant_site


def get_qs_vacant_site():
    from disturbance.components.proposals.models import ApiarySiteOnProposal
    from disturbance.components.approvals.models import ApiarySiteOnApproval

    qs_vacant_site = get_vacant_apiary_site()

    # apiary_site_proposal_ids = qs_vacant_site.all().values('proposal_link_for_vacant__id')
    apiary_site_proposal_ids = qs_vacant_site.all().values('latest_proposal_link__id')  # <== Always latest_proposal_link should have the latest site_status, shouldn't it?
    qs_vacant_site_proposal = ApiarySiteOnProposal.objects.filter(id__in=apiary_site_proposal_ids)

    apiary_site_approval_ids = qs_vacant_site.all().values('approval_link_for_vacant__id')
    qs_vacant_site_approval = ApiarySiteOnApproval.objects.filter(id__in=apiary_site_approval_ids)

    return qs_vacant_site_proposal, qs_vacant_site_approval


# def get_qs_proposal(proposal_id=None):
def get_qs_proposal():
    from disturbance.components.proposals.models import ApiarySite, ApiarySiteOnProposal, Proposal

    # 1. ApiarySiteOnProposal
    q_include_proposal = Q()
    q_exclude_proposal = Q()

    # 1.1. Include
    q_include_proposal &= Q(id__in=(ApiarySite.objects.all().values('latest_proposal_link__id')))  # Include only the intermediate objects which are on the ApiarySite.latest_proposal_links

    # 1.2. Exclude
    q_exclude_proposal |= Q(site_status__in=(SITE_STATUS_DRAFT,)) & Q(making_payment=False)  # Purely 'draft' site
    q_exclude_proposal |= Q(site_status__in=(SITE_STATUS_APPROVED,))  # 'approved' site should be included in the approval as a 'current'
    q_exclude_proposal |= Q(apiary_site__in=ApiarySite.objects.filter(is_vacant=True))  # Vacant sites are already picked up above.  We don't want to pick up them again here.

#    # 1.3. Exculde the apairy sites which are on the proposal apiary currently being accessed
#    if proposal_id:
#        # When proposal_id is passed as a query_params, which is the one in the URL after the ?
#        # Exculde the apiary_sites included in that proposal
#        proposal = Proposal.objects.get(id=proposal_id)
#        q_exclude_proposal |= Q(proposal_apiary=proposal.proposal_apiary)
#
    # 1.4. Issue query
    qs_on_proposal = ApiarySiteOnProposal.objects.filter(q_include_proposal).exclude(q_exclude_proposal).distinct('apiary_site')
    qs_on_proposal_processed = qs_on_proposal.exclude(wkb_geometry_processed=None)
    qs_on_proposal_draft = qs_on_proposal.filter(wkb_geometry_processed=None)  # For the 'draft' apiary sites with the making_payment=True attribute

    return qs_on_proposal_draft, qs_on_proposal_processed


def get_qs_approval():
    from disturbance.components.proposals.models import ApiarySite
    from disturbance.components.approvals.models import ApiarySiteOnApproval

    q_include_approval = Q()
    q_exclude_approval = Q()

    qs_vacant_site = get_vacant_apiary_site()

    # 2.1. Include
    q_include_approval &= Q(id__in=(ApiarySite.objects.all().values('latest_approval_link__id')))  # Include only the intermediate objects which are on the ApiarySite.latest_approval_links

    # 2.2. Exclude
    q_exclude_approval |= Q(apiary_site__in=qs_vacant_site)  # We don't want to pick up the vacant sites already retrieved above
    q_exclude_approval |= Q(site_status=SITE_STATUS_TRANSFERRED)

    # 2.3. Issue query
    qs_on_approval = ApiarySiteOnApproval.objects.filter(q_include_approval).exclude(q_exclude_approval).distinct('apiary_site')

    return qs_on_approval


def validate_buffer(wkb_geometry, apiary_sites_to_exclude=None):
    """
    This function checks if the wkb_geometry (point) is at least 3km away from the other apiary sites
    @param wkb_geometry: WKB geometry of a point
    @param apiary_sites_to_exclude: List or queryset of the apiary sites to be excluded when validation
    """
    if not apiary_sites_to_exclude:
        from disturbance.components.proposals.models import ApiarySite
        apiary_sites_to_exclude = ApiarySite.objects.none()

    site_too_close_error = serializers.ValidationError(
        ['Apiary Site: (lat: {}, lng: {}) is too close to another apiary site.'.format(
            wkb_geometry.coords[1],
            wkb_geometry.coords[0],
        )])

    qs_vacant_site_proposal, qs_vacant_site_approval = get_qs_vacant_site()
    sites = qs_vacant_site_proposal.exclude(apiary_site__in=apiary_sites_to_exclude).filter(Q(wkb_geometry_processed__distance_lte=(wkb_geometry, Distance(m=RESTRICTED_RADIUS))))
    if sites:
        raise site_too_close_error
    sites = qs_vacant_site_approval.exclude(apiary_site__in=apiary_sites_to_exclude).filter(Q(wkb_geometry__distance_lte=(wkb_geometry, Distance(m=RESTRICTED_RADIUS))))
    if sites:
        raise site_too_close_error

    qs_on_proposal_draft, qs_on_proposal_processed = get_qs_proposal()
    sites = qs_on_proposal_draft.exclude(apiary_site__in=apiary_sites_to_exclude).filter(Q(wkb_geometry_draft__distance_lte=(wkb_geometry, Distance(m=RESTRICTED_RADIUS))))
    if sites:
        raise site_too_close_error
    sites = qs_on_proposal_processed.exclude(apiary_site__in=apiary_sites_to_exclude).filter(Q(wkb_geometry_processed__distance_lte=(wkb_geometry, Distance(m=RESTRICTED_RADIUS))))
    if sites:
        raise site_too_close_error

    qs_on_approval = get_qs_approval()
    sites = qs_on_approval.exclude(apiary_site__in=apiary_sites_to_exclude).filter(Q(wkb_geometry__distance_lte=(wkb_geometry, Distance(m=RESTRICTED_RADIUS))))
    if sites:
        raise site_too_close_error
