from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from disturbance.components.proposals.models import (
                                    Proposal,
                                    ProposalApiarySiteLocation,
                                    ProposalApiaryTemporaryUse,
                                    ProposalApiarySiteTransfer,
                                    ProposalApiaryDocument,
                                )

from disturbance.components.main.serializers import CommunicationLogEntrySerializer
from rest_framework import serializers
from django.db.models import Q
from reversion.models import Version

class ProposalApiarySiteLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProposalApiarySiteLocation
        fields = ('id', 'title', 'proposal')
        #fields = '__all__'


class ProposalApiaryTemporaryUseSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProposalApiaryTemporaryUse
        fields = '__all__'


class ProposalApiarySiteTransferSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProposalApiarySiteTransfer
        fields = '__all__'


class ProposalApiaryDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalApiaryDocument
        fields = ('id', 'name', '_file')

class SaveProposalApiarySiteLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalApiarySiteLocation
        fields = ('id', 'title', 'proposal')


class ProposalApiarySerializer(serializers.ModelSerializer):
    readonly = serializers.SerializerMethodField(read_only=True)
    documents_url = serializers.SerializerMethodField()
    proposal_type = serializers.SerializerMethodField()
    get_history = serializers.ReadOnlyField()
    #fee_invoice_url = serializers.SerializerMethodField()

    submitter = serializers.CharField(source='submitter.get_full_name')
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)

    application_type = serializers.CharField(source='application_type.name', read_only=True)
    apiary_site_location = ProposalApiarySiteLocationSerializer()
    apiary_temporary_use = ProposalApiaryTemporaryUseSerializer()
    apiary_site_transfer = ProposalApiarySiteTransferSerializer()

    class Meta:
        model = Proposal
        fields = (
                'id',
                'application_type',
                'proposal_type',
                'title',
                'customer_status',
                'processing_status',
                'review_status',
                #'applicant_type',
                'applicant',
                #'org_applicant',
                #'proxy_applicant',
                'submitter',
                'assigned_officer',
                'previous_application',
                'get_history',
                'lodgement_date',
                'modified_date',
                'documents',
                'requirements',
                'readonly',
                'can_user_edit',
                'can_user_view',
                'documents_url',
                'reference',
                'lodgement_number',
                'lodgement_sequence',
                'can_officer_process',
                'proposal_type',
                #'pending_amendment_request',
                #'is_amendment_proposal',

                #'applicant_details',
                #'training_completed',
                #'fee_invoice_url',
                #'fee_paid',
                'apiary_site_location',
                'apiary_temporary_use',
                'apiary_site_transfer',

                )
        read_only_fields=('documents',)



    def get_documents_url(self,obj):
        return '/media/{}/proposals/{}/documents/'.format(settings.MEDIA_APP_DIR, obj.id)

    def get_readonly(self,obj):
        return False

    def get_processing_status(self,obj):
        return obj.get_processing_status_display()

    def get_review_status(self,obj):
        return obj.get_review_status_display()

    def get_customer_status(self,obj):
        return obj.get_customer_status_display()

    def get_proposal_type(self,obj):
        return obj.get_proposal_type_display()

    def get_fee_invoice_url(self,obj):
        return '/cols/payments/invoice-pdf/{}'.format(obj.fee_invoice_reference) if obj.fee_paid else None


