from .test_setup import APITestSetup


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
        try:
            print("test_create_proposal_apiary")
            #self.client.login(email=self.adminUN, password='pass')
            self.client.login(email=self.customer, password='pass')
            self.client.enforce_csrf_checks=True
            create_response = self.client.post('/api/proposal/', self.create_proposal_data)

            #print(type(response))
            print(create_response.status_code)
            #print(response.json())
            print(create_response.data)
            self.assertTrue(create_response.data.get('id') > 0)

        except Exception as e:
            raise e

    def test_save_draft_proposal(self):
        try:
            #import ipdb; ipdb.set_trace()
            print("test_submit_proposal")
            #import ipdb;ipdb.set_trace()
            self.client.login(email=self.customer, password='pass')
            self.client.enforce_csrf_checks=True
            # create proposal
            create_response = self.client.post('/api/proposal/', self.create_proposal_data)
            proposal_id = create_response.data.get('id')
            # get proposal
            url = 'http://localhost:8071/api/proposal_apiary/{}.json'.format(proposal_id)
            print("url")
            print(url)
            #response = self.client.get('http://localhost:8071/api/proposal_apiary/{}.json'.format(self.test_proposal_id))
            get_response = self.client.get(url)

            #print(type(response))
            print(get_response.status_code)
            #print(get_response.json())
            print(get_response.data)

            submit_response = self.client.post('/api/proposal/{}/draft/'.format(proposal_id), self.submit_proposal_data, content_type='application/json')
            print(submit_response.status_code)
            #print(submit_response.data)
            self.assertEqual(submit_response.status_code, 302)
            #self.assertTrue(submit_response.data.get('id') > 0)
        except Exception as e:
            raise e

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

