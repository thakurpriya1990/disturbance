import datetime
import logging

import pytz
from ledger.settings_base import TIME_ZONE

from disturbance.components.main.models import ApplicationType
from disturbance.components.proposals.models import ApiarySiteFeeType, SiteCategory, ApiarySiteFee, ProposalType

logger = logging.getLogger(__name__)


class DefaultDataManager(object):

    def __init__(self):
        # Store default ApiarySiteFeeType data
        for item in ApiarySiteFeeType.FEE_TYPE_CHOICES:
            obj, created = ApiarySiteFeeType.objects.get_or_create(name=item[0])
            if created:
                logger.info("Created apiary site fee type: %s" % obj)

        # Store default SiteCategory data
        for item in SiteCategory.CATEGORY_CHOICES:
            obj, created = SiteCategory.objects.get_or_create(name=item[0])
            if created:
                logger.info("Created apiary site category: %s" % obj)

        # Store default ApiarySiteFee
        today_local = datetime.datetime.now(pytz.timezone(TIME_ZONE)).date()
        for type_choice in ApiarySiteFeeType.FEE_TYPE_CHOICES:
            fee_type = ApiarySiteFeeType.objects.get(name=type_choice[0])
            for cat_choice in SiteCategory.CATEGORY_CHOICES:
                cat = SiteCategory.objects.get(name=cat_choice[0])
                site_fees = ApiarySiteFee.objects.filter(apiary_site_fee_type=fee_type, site_category=cat, date_of_enforcement__lte=today_local)
                if not site_fees.count():
                    new_fee = ApiarySiteFee.objects.create(apiary_site_fee_type=fee_type, site_category=cat, date_of_enforcement=today_local)
                    new_fee.amount = 100
                    new_fee.save()
                    logger.info("Created apiary site fee: %s" % new_fee)

        # Store default

        for type_name in ApplicationType.APPLICATION_TYPES:
            q_set = ApplicationType.objects.filter(name=type_name[0])
            if not q_set:
                visibility = True if type_name[0] in (
                        ApplicationType.DISTURBANCE, 
                        ApplicationType.APIARY, 
                        ApplicationType.POWERLINE_MAINTENANCE
                        ) else False
                obj = ApplicationType.objects.create(
                        name=type_name[0],
                        application_fee=0,
                        oracle_code_application='',
                        visible=visibility,
                        )
                logger.info("Created application type: %s" % obj)

        for name in [ApplicationType.APIARY, ApplicationType.TEMPORARY_USE, ApplicationType.SITE_TRANSFER]:
            qs = ProposalType.objects.filter(name=name)
            if not qs:
                obj = ProposalType.objects.create(name=name, schema=[{}])
                if obj:
                    logger.info("Created proposal type: %s" % obj)

