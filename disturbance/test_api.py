from .test_setup import APITestSetup
from disturbance.components.proposals.models import (
        Proposal,
        )


class ProposalTests(APITestSetup):
    #def __init__(self, *args, **kwargs):
    #    try:
    #        super(ProposalTests, self).__init__(*args, **kwargs)
    #        self.create_proposal_data = {
    #            u'profile': 132376, 
    #            u'application': proposal_type_id, 
    #            u'behalf_of': u'individual', 
    #            }

    #    except Exception as e:
    #        raise e

    def test_create_proposal_apiary(self):
        #try:
        print("test_create_proposal_apiary")
        #self.client.login(email=self.adminUN, password='pass')
        self.client.login(email=self.customer, password='pass')
        self.client.enforce_csrf_checks=True
        create_response = self.client.post('/api/proposal/', self.create_proposal_data)

        #print(create_response.status_code)
        #print(create_response.data)
        self.assertEqual(create_response.status_code, 200)
        self.assertTrue(create_response.data.get('id') > 0)

        #except Exception as e:
         #   raise e

class IntegrationTests(APITestSetup):
    def test_proposal_apiary_workflow(self):
        #try:
        print("test_proposal_apiary_workflow")
        self.client.login(email=self.customer, password='pass')
        self.client.enforce_csrf_checks=True
        # create proposal
        create_response = self.client.post('/api/proposal/', self.create_proposal_data)
        proposal_id = create_response.data.get('id')
        # get proposal
        url = 'http://localhost:8071/api/proposal_apiary/{}.json'.format(proposal_id)
        #print("url")
        #print(url)
        #response = self.client.get('http://localhost:8071/api/proposal_apiary/{}.json'.format(self.test_proposal_id))
        get_response = self.client.get(url)

        #print(get_response.status_code)
        #print(get_response.data)
        self.assertEqual(get_response.status_code, 200)

        import ipdb; ipdb.set_trace()
        draft_response = self.client.post(
                '/api/proposal/{}/draft/'.format(proposal_id), 
                self.draft_proposal_data, 
                content_type='application/json'
                )
        #print(submit_response.status_code)
        #print(submit_response.data)
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
                "checked": true
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
                #content_type='application/json'
                )

        print("propose_to_approve_response.status_code")
        print(propose_to_approve_response.status_code)
        print("propose_to_approve_response.data")
        print(propose_to_approve_response.data)
        self.assertEqual(propose_to_approve_response.status_code, 200)

        #except Exception as e:
         #   raise e

    #def test_submit_proposal(self):
    #    try:
    #        #import ipdb; ipdb.set_trace()
    #        print("test_submit_proposal")
    #        #import ipdb;ipdb.set_trace()
    #        self.client.login(email=self.customer, password='pass')
    #        self.client.enforce_csrf_checks=True
    #        # create proposal
    #        create_response = self.client.post('/api/proposal/', self.create_proposal_data)
    #        proposal_id = create_response.data.get('id')
    #        # get proposal
    #        url = 'http://localhost:8071/api/proposal_apiary/{}.json'.format(proposal_id)
    #        print("url")
    #        print(url)
    #        #response = self.client.get('http://localhost:8071/api/proposal_apiary/{}.json'.format(self.test_proposal_id))
    #        get_response = self.client.get(url)

    #        #print(type(response))
    #        print(get_response.status_code)
    #        #print(get_response.json())
    #        print(get_response.data)

    #        submit_response = self.client.post('/api/proposal/{}/submit/'.format(proposal_id), self.submit_proposal_data)
    #        print(submit_response.status_code)
    #        print(submit_response.data)
    #        self.assertEqual(submit_response.status_code, 200)
    #        self.assertTrue(submit_response.data.get('id') > 0)
    #    except Exception as e:
    #        raise e

