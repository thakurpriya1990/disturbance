from .test_setup import APITestSetup
from disturbance.components.proposals.models import (
        ProposalType,
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
        try:
            print("test_create_proposal_apiary")
            #self.client.login(email=self.adminUN, password='pass')
            self.client.login(email=self.customer, password='pass')
            self.client.enforce_csrf_checks=True
            response = self.client.post('/api/proposal/', self.create_proposal_data)

            print(type(response))
            print(response.status_code)
            print(response.json())
            print(response.data)

        except Exception as e:
            raise e

    def test_submit_proposal(self):
        try:
            #import ipdb; ipdb.set_trace()
            print("test_submit_proposal")
            #import ipdb;ipdb.set_trace()
            self.client.login(email=self.customer, password='pass')
            self.client.enforce_csrf_checks=True
            # create proposal
            create_response = self.client.post('/api/proposal/', self.create_proposal_data)
            # get proposal
            url = 'http://localhost:8071/api/proposal_apiary/{}.json'.format(create_response.data.get('id'))
            print("url")
            print(url)
            #response = self.client.get('http://localhost:8071/api/proposal_apiary/{}.json'.format(self.test_proposal_id))
            response = self.client.get(url)

            print(type(response))
            print(response.status_code)
            print(response.json())
            print(response.data)
        except Exception as e:
            raise e

    #def test_get_proposal_as_admin(self):
    #    try:
    #        import ipdb;ipdb.set_trace()
    #        self.client.login(email=self.adminUN, password='pass')
    #        self.client.enforce_csrf_checks=True
    #        print("test_get_proposal_as_admin")

    #        #response = self.client.get('/api/proposal_apiary/143.json')
    #        response = self.client.get('http://localhost:8071/api/proposal_apiary/{}.json'.format(self.test_proposal_id))
    #        #response = self.client.get('http://localhost:8071/api/proposal_apiary/143.json')

    #        print(type(response))
    #        print(response.status_code)
    #        print(response.json())
    #        print(response.data)
    #    except Exception as e:
    #        raise e

    #def test_submit_proposal(self):
     #   try:
      #      request_data = 


            #response = client.get('/api/proposal_apiary/143.json')

            #print(type(response))
            #print(response.status_code)
            #print(response.json())
            #print(response.data)


##class ProposalTests(APITestCase):
#class LiveProposalTests(APILiveServerTestCase):
#    def test_get_proposal(self):
#        #import ipdb;ipdb.set_trace()
#        #factory = APIRequestFactory()
#        client = RequestsClient()
#        client.auth = HTTPBasicAuth(username='brendan.blackford@dbca.wa.gov.au', password='test')
#        #client.headers.update({'x-test': 'true'})
#
#        #request = factory.get('/api/proposal_apiary/143.json')
#        #force_authenticate(request, user=user)
#        response = client.get('http://localhost:8071/api/proposal_apiary/143.json')
#
#        print(type(response))
#        print(response.status_code)
#        print(response.json())
#        print(response.data)

        #user = EmailUser.objects.get(email='brendan.blackford@dbca.wa.gov.au')
        #print("EmailUser.objects.count()")
        #print(EmailUser.objects.count())
#        #client = RequestsClient()
#        #client.auth = HTTPBasicAuth('brendan.blackford@dbca.wa.gov.au', 'test')
#        #client.headers.update({'x-test': 'true'})
#        self.client.login(username='brendan.blackford@dbca.wa.gov.au', password='test')
#        print(self.client)
#
#        #request = factory.get('/api/proposal_apiary/143.json')
#        #force_authenticate(request, user=user)
#        #response = self.client.get('http://localhost:8071/api/proposal_apiary/143.json')
#        response = self.client.get('/api/proposal_apiary/143.json')
#
#        print(type(response))
#        print(response.status_code)
#        print(response.data)


#class ProposalTests2(APITestCase):
#    def test_get_proposal_2(self):
#        factory = APIRequestFactory()
#        #user = EmailUser.objects.get(email='brendan.blackford@dbca.wa.gov.au')
#
#        request = factory.get('/api/proposal_apiary/143.json')
#        #force_authenticate(request, user=user)
#        force_authenticate(request, user='brendan.blackford@dbca.wa.gov.au')
#        response = self.client.get(request)
#
#        print(type(response))
#        print(response.data)
 


#request = factory.post('', {}, format='json')

#request = factory.post('/notes/', json.dumps({'title': 'new idea'}), content_type='application/json')


