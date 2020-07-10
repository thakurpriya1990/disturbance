from mixer.backend.django import mixer
from django.conf import settings
from importlib import import_module
from .models import *
from ledger.accounts.models import EmailUser, EmailUserManager
import random
import string
import json, io
from rest_framework.test import (
        APIRequestFactory, 
        force_authenticate, 
        APITestCase,
        APILiveServerTestCase,
        RequestsClient,
        )
from rest_framework import status
from ledger.accounts.models import EmailUser, Address
from ledger.address.models import UserAddress
from requests.auth import HTTPBasicAuth
from disturbance.components.proposals.models import (
        ProposalType,
        ApplicationType,
        ApiaryApplicantChecklistQuestion,
        ApiaryApplicantChecklistAnswer,
        ProposalAssessorGroup,
        ApiaryAssessorGroup,
        ApiaryApproverGroup,
        )

class APITestSetup(APITestCase):

    def setUp(self):
        self.superAdminUN = 'test.superadmin@dbcatest.com'
        self.adminUN = 'test.admin@dbcatest.com'
        self.nonAdminUN = 'test.customer@dbcatest.com'
        superadminUser = None
        adminUser = None
        user = None
        eum = EmailUserManager()
        self.superadminUser = EmailUser.objects.create(email=self.superAdminUN, password="pass", is_staff=True, is_superuser=True)
        self.superadminUser.set_password('pass')
        self.superadminUser.save()
        self.adminUser  = EmailUser.objects.create(email=self.adminUN,password="pass",is_staff=True, is_superuser=False)
        self.adminUser.set_password('pass')       
        self.adminUser.save() 

        self.customer = EmailUser.objects.create(email=self.nonAdminUN, password="pass", is_staff=False, is_superuser=False)
        self.customer.set_password('pass')
        self.customer.save()
        # customer UserAddress
        user_address = UserAddress.objects.create(
                country_id= 'AU',
                #is_default_for_billing= True,
                #is_default_for_shipping= True,
                line1= '17 Dick Perry',
                #line2: '',
                #line3': u'',
                #line4': u'BENTLEY DELIVERY CENTRE',
                #notes': u'',
                #num_orders': 0,
                #phone_number': None,
                postcode= '6151',
                #'search_text': u'',
                state= 'WA',
                #title': u'',
                user_id= self.customer.id
                )

        customer_address = Address.objects.create(user=self.customer, oscar_address=user_address)
        self.customer.residential_address = customer_address
        self.customer.save()

        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

        # ProposalAssessorGroup - add adminUser (internal assessment/approval)
        #new_proposal_assessor_group = ProposalAssessorGroup.objects.create(name="Default Group", default=True)
        #new_proposal_assessor_group.members.add(self.adminUser)

        # ApiaryAssessorGroup - add adminUser (internal assessment/approval)
        new_apiary_assessor_group = ApiaryAssessorGroup.objects.create()
        new_apiary_assessor_group.members.add(self.adminUser)

        # ApiaryApproverGroup - add adminUser (internal assessment/approval)
        new_apiary_approver_group = ApiaryApproverGroup.objects.create()
        new_apiary_approver_group.members.add(self.adminUser)

        # Checklist questions/answers
        apiary_qu_1 = ApiaryApplicantChecklistQuestion.objects.create(answer_type='yes_no', checklist_type="apiary", text="first_question")
        apiary_qu_2 = ApiaryApplicantChecklistQuestion.objects.create(answer_type='yes_no', checklist_type="apiary", text="second_question")
        apiary_qu_3 = ApiaryApplicantChecklistQuestion.objects.create(answer_type='yes_no', checklist_type="apiary", text="third_question")
        apiary_site_transfer_qu_1 = ApiaryApplicantChecklistQuestion.objects.create(answer_type='yes_no', checklist_type="site_transfer", text="first_question")
        apiary_site_transfer_qu_2 = ApiaryApplicantChecklistQuestion.objects.create(answer_type='yes_no', checklist_type="site_transfer", text="second_question")
        apiary_site_transfer_qu_3 = ApiaryApplicantChecklistQuestion.objects.create(answer_type='yes_no', checklist_type="site_transfer", text="third_question")

        # Create ProposalTypes
        ProposalType.objects.create(name='Apiary', schema='[{}]')
        ProposalType.objects.create(name='Disturbance', schema='[{}]')
        ProposalType.objects.create(name='Site Transfer', schema='[{}]')
        ProposalType.objects.create(name='Temporary Use', schema='[{}]')
        # create_proposal_data
        #proposal_type_id = ProposalType.objects.get(name='Apiary').id

        # Create ApplicationTypes
        ApplicationType.objects.create(name='Apiary', application_fee=13)
        ApplicationType.objects.create(name='Disturbance', application_fee=0)
        ApplicationType.objects.create(name='Site Transfer', application_fee=0)
        ApplicationType.objects.create(name='Temporary Use', application_fee=0)
        # create_proposal_data
        application_type_id = ApplicationType.objects.get(name='Apiary').id
        self.create_proposal_data = {
            u'profile': 132376, 
            u'application': application_type_id, 
            u'behalf_of': u'individual', 
            }
        # submit_proposal_data
        #with open('submit_schema.json', 'r') as submit_schema_file:
         #   submit_schema = json.load(submit_schema_file)
        with open('all_the_features.json', 'r') as features_file:
            self.all_the_features = json.load(features_file)
        #all_the_features_list = []
        #all_the_features_list.append(json.dumps(all_the_features))

        #self.draft_proposal_data = {}
        #"proposal_id": null,
        #self.draft_proposal_data["schema"]["proposal_apiary"] = {
        self.draft_schema = {
            "proposal_apiary": {
                "title": "test_title",
                "checklist_answers": [
                        {
                        "id": apiary_qu_1.id,
                        "answer": True
                        },
                        {
                        "id": apiary_qu_2.id,
                        "answer": False
                        },
                        {
                        "id": apiary_qu_3.id,
                        "answer": True
                        },
                    ]
                }
            #"all_the_features": [json.dumps(all_the_features),],
            #"all_the_features": json.dumps(all_the_features),
            }

    def random_email(self):
        """Return a random email address ending in dbca.wa.gov.au
        """
#        print time
#        time.sleep(5)
        # import time as systime
        # systime.sleep(2)
        s = ''.join(random.choice(string.ascii_letters) for i in range(80))
        return '{}@dbca.wa.gov.au'.format(s)

def json_filewriter_example():
    with io.open('filename', 'w', encoding="utf8") as json_file:
        data = json.dumps(d, ensure_ascii=False, encoding="utf8")
        json_file.write(unicode(data))

