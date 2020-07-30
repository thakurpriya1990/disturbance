from disturbance.tests.test_setup import APITestSetup
import json
from disturbance.components.proposals.models import (
        Proposal,
        ApiarySite,
        ProposalStandardRequirement,
        )
from disturbance.management.commands.update_compliance_status import Command

class ProposalTests(APITestSetup):
    def test_create_proposal_apiary(self):
        print("test_create_proposal_apiary")
        self.client.login(email=self.customer, password='pass')
        self.client.enforce_csrf_checks=True
        create_response = self.client.post(
                '/api/proposal/', 
                self.create_proposal_data,
                format='json'
                )

        self.assertEqual(create_response.status_code, 200)
        self.assertTrue(create_response.data.get('id') > 0)

