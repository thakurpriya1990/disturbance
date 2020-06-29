#from django.test import TestCase
#from django.test import Client
from mixer.backend.django import mixer
from django.conf import settings
from importlib import import_module
#import time
from .models import *
##from drf_extra_fields.geo_fields import PointField
#from django.contrib.gis.geos import Point
from ledger.accounts.models import EmailUser, EmailUserManager
#from ledger.payments.models import Invoice, OracleInterfaceSystem
#from oscar.apps.order.models import Order
import random
import string

from rest_framework.test import (
        APIRequestFactory, 
        force_authenticate, 
        APITestCase,
        APILiveServerTestCase,
        #CoreAPIClient,
        RequestsClient,
        )
from rest_framework import status
from ledger.accounts.models import EmailUser, Address
from requests.auth import HTTPBasicAuth

class APITestSetup(APITestCase):
#    client = Client()

    def setUp(self):
#        adminUN = "admin@website.domain"
#        nonAdminUN = "nonadmin@website.domain"
        #self.client = APIClient()
        #self.superAdminUN = load_superAdminUN
        #self.adminUN = load_adminUN
        #self.nonAdminUN = load_nonAdminUN

#        self.superAdminUN = self.random_email()
#        self.adminUN = self.random_email()
#        self.nonAdminUN = self.random_email()
        self.superAdminUN = 'test.superadmin@dbcatest.com'
        self.adminUN = 'test.admin@dbcatest.com'
        self.nonAdminUN = 'test.customer@dbcatest.com'
        superadminUser = None
        adminUser = None
        user = None
        eum = EmailUserManager()
#        self.superadminUser = load_customer 
#        self.adminUser = load_adminUser
#        self.customer = load_superadminUser
#        self.superadminUser = EmailUser.objects.create_superuser(pk=1,email=self.superAdminUN, password="pass")
        self.superadminUser = EmailUser.objects.create(email=self.superAdminUN, password="pass", is_staff=True, is_superuser=True)
        self.superadminUser.set_password('pass')
        self.superadminUser.save()
#        self.adminUser = EmailUser.objects.create_user(pk=2,email=self.adminUN, password="pass", )
        self.adminUser  = EmailUser.objects.create(email=self.adminUN,password="pass",is_staff=True, is_superuser=False)
        self.adminUser.set_password('pass')       
        self.adminUser.save() 

        self.customer = EmailUser.objects.create(email=self.nonAdminUN, password="pass", is_staff=False, is_superuser=False)
        self.customer.set_password('pass')
        self.customer.save()
        #ria = MooringAreaGroup.objects.create(name='Rottnest')
        #pvs = MooringAreaGroup.objects.create(name='PVS')

        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

    def random_email(self):
        """Return a random email address ending in dbca.wa.gov.au
        """
#        print time
#        time.sleep(5)
        # import time as systime
        # systime.sleep(2)
        s = ''.join(random.choice(string.ascii_letters) for i in range(80))
        return '{}@dbca.wa.gov.au'.format(s)

        
#def random_email():
#        """Return a random email address ending in dbca.wa.gov.au
#        """
#        s = ''.join(random.choice(string.ascii_letters) for i in range(80))
#        return '{}@dbca.wa.gov.au'.format(s)
#       
#
#load_superAdminUN = random_email()
#load_adminUN = random_email()
#load_nonAdminUN = random_email()
#
#load_superadminUser = EmailUser.objects.create_superuser(email=load_superAdminUN, password="pass")
#load_adminUser = EmailUser.objects.create_user(email=load_adminUN, password="pass", )
#load_customer = EmailUser.objects.create(email=load_nonAdminUN, password="pass", is_staff=False, is_superuser=False)
 
