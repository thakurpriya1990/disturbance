from django.conf import settings
#from mooring import models
from ledger.payments.helpers import is_payment_admin

from disturbance import helpers

def apiary_url(request):
    #web_url = request.META['HTTP_HOST']
    web_url = request.META.get('HTTP_HOST', None)
    temp = settings
    if web_url in settings.APIARY_URL:
        template_group = 'apiary'
        PUBLIC_URL='https://apiary.dbca.wa.gov.au/'
        application_group = 'apiary'
        displayed_system_name = settings.APIARY_SYSTEM_NAME
        support_email = settings.APIARY_SUPPORT_EMAIL
        settings.SYSTEM_NAME = settings.APIARY_SYSTEM_NAME
        settings.SYSTEM_NAME_SHORT = 'Apiary'
        settings.BASE_EMAIL_TEXT = 'disturbance/emails/apiary_base_email.txt'
        settings.BASE_EMAIL_HTML = 'disturbance/emails/apiary_base_email.html'
        #settings.APIARY_BASE_EMAIL = True
        #base_email_text = 'disturbance/emails/apiary_base_email.txt'
        #base_email_html = 'disturbance/emails/apiary_base_email.html'
        #base_email_text = 'apiary_base_email.txt'
        #base_email_html = 'apiary_base_email.html'
    else:
        template_group = 'das'
        PUBLIC_URL='https://das.dbca.wa.gov.au'
        application_group = 'das'
        displayed_system_name = settings.SYSTEM_NAME
        support_email = settings.SUPPORT_EMAIL
        settings.BASE_EMAIL_TEXT = 'disturbance/emails/base_email.txt'
        settings.BASE_EMAIL_HTML = 'disturbance/emails/base_email.html'
        #base_email_text = 'disturbance/emails/base_email.txt'
        #base_email_html = 'disturbance/emails/base_email.html'

    is_payment_officer = is_payment_admin(request.user)

    return {
        'DEV_STATIC': settings.DEV_STATIC,
        'DEV_STATIC_URL': settings.DEV_STATIC_URL,
        'TEMPLATE_GROUP' : template_group,
        'SYSTEM_NAME' : settings.SYSTEM_NAME,
        'PUBLIC_URL' : PUBLIC_URL,
        'APPLICATION_GROUP': application_group,
        'DISPLAYED_SYSTEM_NAME': displayed_system_name,
        'SUPPORT_EMAIL': support_email,
        'is_payment_admin': is_payment_officer,
        #'BASE_EMAIL_TEXT': base_email_text,
        #'BASE_EMAIL_HTML': base_email_html
        }


def template_context(request):
    """Pass extra context variables to every template.
    """
    context = apiary_url(request)

    return context



