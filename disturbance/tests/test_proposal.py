from disturbance.tests.test_setup import APITestSetup
import json
from disturbance.components.proposals.models import (
        Proposal,
        ApiarySite,
        ProposalStandardRequirement,
        )
from disturbance.management.commands.update_compliance_status import Command
#import subprocess
#from disturbance.components.proposals.serializers_apiary import ApiarySiteSerializer

class ProposalTests(APITestSetup):
    def test_create_proposal_apiary(self):
        #import ipdb; ipdb.set_trace()
        print("test_create_proposal_apiary")
        self.client.login(email=self.customer, password='pass')
        self.client.enforce_csrf_checks=True
        create_response = self.client.post(
                '/api/proposal/', 
                self.create_proposal_data,
                format='json'
                #content_type='application/json'
                )

        #print(create_response.status_code)
        #print(create_response.data)
        self.assertEqual(create_response.status_code, 200)
        self.assertTrue(create_response.data.get('id') > 0)

