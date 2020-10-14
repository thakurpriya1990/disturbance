from django.conf import settings
#from mooring import models
from ledger.payments import helpers

from disturbance import helpers

def apiary_url(request):
    #web_url = request.META['HTTP_HOST']
    web_url = request.META.get('HTTP_HOST', None)
    if web_url in settings.APIARY_URL:
       template_group = 'apiary'
       #TERMS  = "https://www.rottnestisland.com/~/media/Files/boating-documents/marine-hire-facilities-tcs.pdf?la=en"
       PUBLIC_URL='https://apiary.dbca.wa.gov.au/'
       application_group = 'apiary'
       displayed_system_name = settings.APIARY_SYSTEM_NAME
       support_email = settings.APIARY_SUPPORT_EMAIL
    else:
       template_group = 'das'
       #TERMS = "/know/online-mooring-site-booking-terms-and-conditions"
       PUBLIC_URL='https://das.dbca.wa.gov.au'
       application_group = 'das'
       displayed_system_name = settings.SYSTEM_NAME
       support_email = settings.SUPPORT_EMAIL


    #is_officer = False
    #is_inventory = False
    #is_admin = False
    #is_payment_officer = False
    #is_customer = False
 
    #failed_refund_count = 0
    # if request.user.is_authenticated:
    #     if request.user.is_staff or request.user.is_superuser:
    #         failed_refund_count = models.RefundFailed.objects.filter(status=0).count()
    #     is_officer = helpers.is_officer(request.user)
    #     is_inventory = helpers.is_inventory(request.user)
    #     is_admin = helpers.is_admin(request.user)
    #     is_payment_officer = helpers.is_payment_officer(request.user)
    #     is_customer = helpers.is_customer(request.user)
    is_payment_admin = helpers.is_payment_admin(request.user)

    return {
        #'EXPLORE_PARKS_SEARCH': '/map',
        #'EXPLORE_PARKS_CONTACT': '/contact-us',
        #'EXPLORE_PARKS_CONSERVE': '/know/conserving-our-moorings',
        #'EXPLORE_PARKS_PEAK_PERIODS': '/know/when-visit',
        #'EXPLORE_PARKS_ENTRY_FEES': '/know/entry-fees',
        #'EXPLORE_PARKS_TERMS': TERMS,
        #'PARKSTAY_EXTERNAL_URL': settings.PARKSTAY_EXTERNAL_URL,
        'DEV_STATIC': settings.DEV_STATIC,
        'DEV_STATIC_URL': settings.DEV_STATIC_URL,
        'TEMPLATE_GROUP' : template_group,
        #'GIT_COMMIT_DATE' : settings.GIT_COMMIT_DATE,
        #'GIT_COMMIT_HASH' : settings.GIT_COMMIT_HASH,
        'SYSTEM_NAME' : settings.SYSTEM_NAME,
        #'REFUND_FAILED_COUNT': failed_refund_count,
        #'IS_OFFICER' : is_officer,
        #'IS_INVENTORY' : is_inventory,
        #'IS_ADMIN' : is_admin,
        #'IS_PAYMENT_OFFICER' : is_payment_officer,
        #'IS_CUSTOMER' : is_customer,
        'PUBLIC_URL' : PUBLIC_URL,
        #'MOORING_GROUP': mooring_group
        'APPLICATION_GROUP': application_group,
        'DISPLAYED_SYSTEM_NAME': displayed_system_name,
        'SUPPORT_EMAIL': support_email,
        'is_payment_admin': is_payment_admin
        }


def template_context(request):
    """Pass extra context variables to every template.
    """
    context = apiary_url(request)

    return context



