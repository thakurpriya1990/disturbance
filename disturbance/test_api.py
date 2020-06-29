## required for test discovery by ./manage.py test
#from django.test import TestCase
##
from .test_setup import APITestSetup 


#class LiveProposalTests(APILiveServerTestCase):
class ProposalTests(APITestSetup):
    def test_get_proposal(self):
        try:
            #import ipdb;ipdb.set_trace()
            self.client.login(email=self.adminUN, password='pass')
            self.client.enforce_csrf_checks=True
            print("LiveProposalTests test_get_proposal")

            #response = self.client.get('/api/proposal_apiary/143.json')
            response = self.client.get('http://localhost:8071/api/proposal_apiary/143.json')

            print(type(response))
            print(response.status_code)
            print(response.json())
            print(response.data)
        except Exception as e:
            raise e

            #response = client.get('/api/proposal_apiary/143.json')

            #print(type(response))
            #print(response.status_code)
            #print(response.json())
            #print(response.data)


#class ProposalTests(APITestCase):
class LiveProposalTests(APILiveServerTestCase):
    def test_get_proposal(self):
        import ipdb;ipdb.set_trace()
        #factory = APIRequestFactory()
        client = RequestsClient()
        client.auth = HTTPBasicAuth('brendan.blackford@dbca.wa.gov.au', 'test')
        client.headers.update({'x-test': 'true'})

        #request = factory.get('/api/proposal_apiary/143.json')
        #force_authenticate(request, user=user)
        response = client.get('http://localhost:8071/api/proposal_apiary/143.json')

        print(type(response))
        print(response.status_code)
        print(response.json())
        print(response.data)

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


