from django.conf import settings
from ledger.payments.helpers import is_payment_admin


def apiary_url(request):
    if settings.DOMAIN_DETECTED == 'apiary':
        template_group = 'apiary'
        PUBLIC_URL = 'https://apiary.dbca.wa.gov.au/'
        application_group = 'apiary'
        displayed_system_name = settings.APIARY_SYSTEM_NAME
        support_email = settings.APIARY_SUPPORT_EMAIL
        settings.SYSTEM_NAME = settings.APIARY_SYSTEM_NAME
        settings.SYSTEM_NAME_SHORT = 'Apiary'
        settings.BASE_EMAIL_TEXT = 'disturbance/emails/apiary_base_email.txt'
        settings.BASE_EMAIL_HTML = 'disturbance/emails/apiary_base_email.html'
    else:
        template_group = 'das'
        PUBLIC_URL = 'https://das.dbca.wa.gov.au'
        application_group = 'das'
        displayed_system_name = settings.SYSTEM_NAME
        support_email = settings.SUPPORT_EMAIL
        settings.BASE_EMAIL_TEXT = 'disturbance/emails/base_email.txt'
        settings.BASE_EMAIL_HTML = 'disturbance/emails/base_email.html'

    is_payment_officer = is_payment_admin(request.user)

    return {
        'DOMAIN_DETECTED': settings.DOMAIN_DETECTED,
        'DEV_STATIC': settings.DEV_STATIC,
        'DEV_STATIC_URL': settings.DEV_STATIC_URL,
        'TEMPLATE_GROUP': template_group,
        'SYSTEM_NAME': settings.SYSTEM_NAME,
        'PUBLIC_URL': PUBLIC_URL,
        'APPLICATION_GROUP': application_group,
        'DISPLAYED_SYSTEM_NAME': displayed_system_name,
        'SUPPORT_EMAIL': support_email,
        'is_payment_admin': is_payment_officer,
    }
