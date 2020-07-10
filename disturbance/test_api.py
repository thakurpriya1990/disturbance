from .test_setup import APITestSetup
import json
from disturbance.components.proposals.models import (
        Proposal,
        ApiarySite,
        )


class ProposalTests(APITestSetup):
    def test_create_proposal_apiary(self):
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

class IntegrationTests(APITestSetup):
    def test_proposal_apiary_workflow(self):
        #try:
        print("test_proposal_apiary_workflow")
        self.client.login(email=self.customer, password='pass')
        self.client.enforce_csrf_checks=True
        # create proposal
        create_response = self.client.post(
                '/api/proposal/', 
                self.create_proposal_data,
                format='json'
                #content_type='application/json'
                )
        proposal_id = create_response.data.get('id')
        # get proposal
        url = 'http://localhost:8071/api/proposal_apiary/{}.json'.format(proposal_id)
        get_response = self.client.get(url)

        self.assertEqual(get_response.status_code, 200)

        self.draft_schema['proposal_apiary']['id'] = proposal_id
        draft_proposal_data = {
                "schema": json.dumps(self.draft_schema),
                #"all_the_features": json.dumps(self.all_the_features)
                "all_the_features": self.all_the_features
                }
        draft_response = self.client.post(
                '/api/proposal/{}/draft/'.format(proposal_id),
                draft_proposal_data, 
                format='json'
                #content_type='application/json'
                )
        self.assertEqual(draft_response.status_code, 302)
        #self.assertTrue(submit_response.data.get('id') > 0)

        # Simulate Proposal submission by changing status instead of going through the payment gateway
        saved_proposal = Proposal.objects.get(id=proposal_id)
        saved_proposal.processing_status = 'with_assessor'
        saved_proposal.customer_status = 'with_assessor'
        saved_proposal.save()

        # referrals testing goes here

        # Move status to 'With Assessor (Requirements)
        saved_proposal.processing_status = 'with_assessor_requirements'
        saved_proposal.save()

        # login as internal 
        self.client.login(email=self.adminUser, password='pass')
        self.client.enforce_csrf_checks=True

        # Propose to approve
        apiary_sites = []
        for site in saved_proposal.proposal_apiary.apiary_sites.all():
            apiary_sites.append({
                #"id": "{}".format(site.id),
                "id": site.id,
                "checked": True
                })
        propose_to_approve_data = {
                "details": "test details",
                "expiry_date": "15/07/2020",
                "start_date": "01/07/2020",
                #"apiary_sites": "{}".format(apiary_sites)
                "apiary_sites": apiary_sites
                }
        print(propose_to_approve_data)
        propose_to_approve_response = self.client.post(
                '/api/proposal/{}/proposed_approval/'.format(proposal_id), 
                propose_to_approve_data, 
                format='json'
                #content_type='application/json'
                )

        self.assertEqual(propose_to_approve_response.status_code, 200)

        # Final approval with unchanged data
        final_approval_data = propose_to_approve_data
        final_approval_response = self.client.post(
                '/api/proposal/{}/final_approval/'.format(proposal_id), 
                final_approval_data, 
                format='json'
                #content_type='application/json'
                )

        self.assertEqual(final_approval_response.status_code, 200)

        # Show properties of newly created approval
        print(Proposal.objects.get(id=proposal_id).approval)
        print(Proposal.objects.get(id=proposal_id).approval.apiary_approval)
        print(Proposal.objects.get(id=proposal_id).processing_status)

