from disturbance.test_setup import APITestSetup
import json
from disturbance.components.proposals.models import (
        Proposal,
        ApiarySite,
        ProposalStandardRequirement,
        )
from disturbance.management.commands.update_compliance_status import Command
#import subprocess
#from disturbance.components.proposals.serializers_apiary import ApiarySiteSerializer


class ApiaryIntegrationTests(APITestSetup):
    def test_proposal_apiary_workflow(self):
        #import ipdb; ipdb.set_trace()
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
        #######################
        proposal = Proposal.objects.get(id=proposal_id)
        draft_schema = {
            "proposal_apiary": {
                "id": proposal_id,
                "title": "test_title",
                "checklist_answers": [
                        {
                        #"id": self.apiary_qu_1.id,
                        "id": proposal.proposal_apiary.apiary_applicant_checklist.order_by('id')[0].id,
                        "answer": True
                        },
                        {
                        #"id": self.apiary_qu_2.id,
                        "id": proposal.proposal_apiary.apiary_applicant_checklist.order_by('id')[1].id,
                        "answer": False
                        },
                        {
                        #"id": self.apiary_qu_3.id,
                        "id": proposal.proposal_apiary.apiary_applicant_checklist.order_by('id')[2].id,
                        "answer": True
                        },
                    ]
                }
            #"all_the_features": [json.dumps(all_the_features),],
            #"all_the_features": json.dumps(all_the_features),
            }

        #draft_schema['proposal_apiary']['id'] = proposal_id
        draft_proposal_data = {
                "schema": json.dumps(draft_schema),
                #"all_the_features": json.dumps(self.all_the_features)
                "all_the_features": self.all_the_features_1
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

        # add requirements
        proposal_standard_req_r1_id = ProposalStandardRequirement.objects.get(code='R1').id
        add_requirements_data_1 = {
                #"due_date": "16/08/2020",
                "due_date": self.today_plus_1_week_str,
                "standard": True,
                "recurrence": True,
                "recurrence_pattern": "1",
                "proposal": proposal_id,
                "standard_requirement": str(proposal_standard_req_r1_id),
                "recurrence_schedule": "1",
                "free_requirement": ""
                }
        add_requirements_response_1 = self.client.post(
                '/api/proposal_requirements.json', 
                add_requirements_data_1, 
                format='json'
                #content_type='application/json'
                )
        #proposal_requirement_1_id = add_requirements_response_1.data.get('id')
        self.assertEqual(add_requirements_response_1.status_code, 201)

        proposal_standard_req_a1_id = ProposalStandardRequirement.objects.get(code='A1').id
        add_requirements_data_2 = {
                #"due_date": "16/08/2020",
                "due_date": self.today_plus_1_week_str,
                "standard": True,
                "recurrence": False,
                "recurrence_pattern": "1",
                "proposal": proposal_id,
                "standard_requirement": str(proposal_standard_req_a1_id),
                #"recurrence_schedule": "1",
                "free_requirement": ""
                }
        add_requirements_response_2 = self.client.post(
                '/api/proposal_requirements.json', 
                add_requirements_data_2, 
                format='json'
                #content_type='application/json'
                )
        #proposal_requirement_2_id = add_requirements_response_2.data.get('id')
        self.assertEqual(add_requirements_response_2.status_code, 201)

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
                #"expiry_date": "15/07/2021",
                "expiry_date": self.today_plus_26_weeks_str,
                #"start_date": "02/07/2020",
                "start_date": self.today_str,
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
                '/api/proposal_apiary/{}/final_approval/'.format(proposal_id), 
                final_approval_data, 
                format='json'
                #content_type='application/json'
                )
        self.assertEqual(final_approval_response.status_code, 200)

        print("new apiary proposal for same licence")
        self.client.login(email=self.customer, password='pass')
        self.client.enforce_csrf_checks=True
        # create proposal
        create_response_2 = self.client.post(
                '/api/proposal/', 
                self.create_proposal_data,
                format='json'
                )
        proposal_id_2 = create_response_2.data.get('id')
        # get proposal
        url = 'http://localhost:8071/api/proposal_apiary/{}.json'.format(proposal_id_2)
        get_response_2 = self.client.get(url)

        self.assertEqual(get_response_2.status_code, 200)
        #######################
        proposal_2 = Proposal.objects.get(id=proposal_id_2)
        draft_schema_2 = {
            "proposal_apiary": {
                "id": proposal_id_2,
                "title": "test_title",
                "checklist_answers": [
                        {
                        "id": proposal_2.proposal_apiary.apiary_applicant_checklist.order_by('id')[0].id,
                        "answer": True
                        },
                        {
                        "id": proposal_2.proposal_apiary.apiary_applicant_checklist.order_by('id')[1].id,
                        "answer": False
                        },
                        {
                        "id": proposal_2.proposal_apiary.apiary_applicant_checklist.order_by('id')[2].id,
                        "answer": True
                        },
                    ]
                }
            }

        draft_proposal_data_2 = {
                "schema": json.dumps(draft_schema_2),
                "all_the_features": self.all_the_features_2
                }
        draft_response_2 = self.client.post(
                '/api/proposal/{}/draft/'.format(proposal_id_2),
                draft_proposal_data_2, 
                format='json'
                )
        self.assertEqual(draft_response_2.status_code, 302)

        # Simulate Proposal submission by changing status instead of going through the payment gateway
        saved_proposal_2 = Proposal.objects.get(id=proposal_id_2)
        saved_proposal_2.processing_status = 'with_assessor'
        saved_proposal_2.customer_status = 'with_assessor'
        saved_proposal_2.save()

        # referrals testing goes here

        # Move status to 'With Assessor (Requirements)
        saved_proposal_2.processing_status = 'with_assessor_requirements'
        saved_proposal_2.save()

        # login as internal 
        self.client.login(email=self.adminUser, password='pass')
        self.client.enforce_csrf_checks=True

        # add requirements
        proposal_standard_req_r2_id = ProposalStandardRequirement.objects.get(code='R2').id
        add_requirements_data_3 = {
                #"due_date": "26/08/2020",
                "due_date": self.today_plus_1_week_str,
                "standard": True,
                "recurrence": True,
                "recurrence_pattern": "1",
                "proposal": proposal_id_2,
                "standard_requirement": str(proposal_standard_req_r2_id),
                "recurrence_schedule": "1",
                "free_requirement": ""
                }
        add_requirements_response_3 = self.client.post(
                '/api/proposal_requirements.json', 
                add_requirements_data_3, 
                format='json'
                #content_type='application/json'
                )
        #proposal_requirement_3_id = add_requirements_response_3.data.get('id')
        self.assertEqual(add_requirements_response_3.status_code, 201)

        proposal_standard_req_a2_id = ProposalStandardRequirement.objects.get(code='A2').id
        add_requirements_data_4 = {
                #"due_date": "26/08/2020",
                "due_date": self.today_plus_1_week_str,
                "standard": True,
                "recurrence": False,
                "recurrence_pattern": "1",
                "proposal": proposal_id_2,
                "standard_requirement": str(proposal_standard_req_a2_id),
                #"recurrence_schedule": "1",
                "free_requirement": ""
                }
        add_requirements_response_4 = self.client.post(
                '/api/proposal_requirements.json', 
                add_requirements_data_4, 
                format='json'
                #content_type='application/json'
                )
        #proposal_requirement_4_id = add_requirements_response_4.data.get('id')
        self.assertEqual(add_requirements_response_4.status_code, 201)

        ## delete requirement
        requirement_to_delete_id = Proposal.objects.get(id=proposal_id_2).requirements.filter(standard_requirement__code="A1")[0].id
        delete_requirement_response_2 = self.client.get(
                '/api/proposal_requirements/{}/discard.json'.format(requirement_to_delete_id)
                )
        self.assertEqual(delete_requirement_response_2.status_code, 200)

        # Propose to approve
        apiary_sites_2 = []
        for site in saved_proposal_2.proposal_apiary.apiary_sites.all():
            apiary_sites_2.append({
                #"id": "{}".format(site.id),
                "id": site.id,
                "checked": True
                })
        propose_to_approve_data_2 = {
                "details": "test details",
                #"expiry_date": "15/07/2020",
                #"start_date": "01/07/2020",
                "apiary_sites": apiary_sites_2
                }
        print(propose_to_approve_data_2)
        propose_to_approve_response_2 = self.client.post(
                '/api/proposal/{}/proposed_approval/'.format(proposal_id_2), 
                propose_to_approve_data_2, 
                format='json'
                )

        self.assertEqual(propose_to_approve_response_2.status_code, 200)

        # Final approval with unchanged data
        #import ipdb; ipdb.set_trace()
        final_approval_data_2 = propose_to_approve_data_2
        final_approval_response_2 = self.client.post(
                '/api/proposal_apiary/{}/final_approval/'.format(proposal_id_2), 
                final_approval_data_2, 
                format='json'
                )
        self.assertEqual(final_approval_response_2.status_code, 200)


        # Show properties of newly created approval
        final_proposal = Proposal.objects.get(id=proposal_id_2)
        final_proposal_proposal_apiary_id = final_proposal.proposal_apiary.id
        print(Proposal.objects.get(id=proposal_id).approval.apiary_approval)
        print(Proposal.objects.get(id=proposal_id).processing_status)
        print("APPROVAL SITES")
        for approval_site in ApiarySite.objects.filter(approval=final_proposal.approval):
            print(approval_site)
        # Compliance creation test
        approval_standard_requirements = []
        for compliance in final_proposal.approval.compliances.all():
            #print('{}, {}, {}, {}, {}'.format(
            #    compliance.id, 
            #    compliance.lodgement_number, 
            #    str(compliance.requirement.standard_requirement), 
            #    compliance.processing_status,
            #    str(compliance.due_date)
            #    )
            #)
            approval_standard_requirements.append(compliance.requirement.standard_requirement_id)
        #print("approval_requirements")
        #print(approval_standard_requirements)
        #print(proposal_standard_req_r1_id)
        #print(proposal_standard_req_a1_id)
        #print(proposal_standard_req_r2_id)
        #print(proposal_standard_req_a2_id)
        self.assertIn(proposal_standard_req_r1_id, approval_standard_requirements)
        # This requirement is deleted earlier
        self.assertNotIn(proposal_standard_req_a1_id, approval_standard_requirements)
        self.assertIn(proposal_standard_req_r2_id, approval_standard_requirements)
        self.assertIn(proposal_standard_req_a2_id, approval_standard_requirements)

        # check Reversion endpoint
        url = '/api/proposal_apiary/{}/proposal_history/'.format(final_proposal_proposal_apiary_id)
        reversion_response = self.client.get(url)
        self.assertEqual(reversion_response.status_code, 200)

        # Update newly created Compliance status values
        #subprocess.call('python manage_ds.py update_compliance_status', shell=True)
        cron_job = Command()
        cron_job.handle()
        #for compliance in Proposal.objects.get(id=proposal_id_2).approval.compliances.all():
        #    print('{}, {}, {}, {}, {}, {}, {}'.format(
        #        final_proposal.approval.status,
        #        str(final_proposal.approval.expiry_date),
        #        compliance.id, 
        #        compliance.lodgement_number, 
        #        str(compliance.requirement.standard_requirement), 
        #        compliance.processing_status,
        #        str(compliance.due_date)
        #        )
        #    )
        # Compliance with standard_requirement code "A2" should now have status "due"
        compliance_a2 = Proposal.objects.get(id=proposal_id_2).approval.compliances.filter(requirement__standard_requirement__code="A2")[0]
        self.assertEqual(compliance_a2.processing_status, "due")

