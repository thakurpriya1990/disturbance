import json
import os

from django.core.management.base import BaseCommand

from disturbance.components.approvals.serializers_apiary import ApiarySiteOnApprovalGeometryExportSerializer
from disturbance.components.main.utils import get_qs_vacant_site, get_qs_proposal, get_qs_approval
from disturbance.components.proposals.models import ProposalType
from disturbance.components.proposals.serializers_apiary import ApiarySiteOnProposalDraftGeometryExportSerializer, \
    ApiarySiteOnProposalProcessedGeometryExportSerializer
from disturbance.settings import BASE_DIR, SPATIAL_DATA_DIR


class Command(BaseCommand):
    help = 'Save the apiary sites as a json file'

    def handle(self, *args, **options):
        # Retrieve 'vacant' sites
        qs_vacant_site_proposal, qs_vacant_site_approval = get_qs_vacant_site()
        # qs_vacant_site_proposal may not have the wkb_geometry_processed if the apiary site is the selected 'vacant' site

        serializer_vacant_proposal_d = ApiarySiteOnProposalDraftGeometryExportSerializer(qs_vacant_site_proposal.filter(wkb_geometry_processed__isnull=True), many=True)
        serializer_vacant_proposal = ApiarySiteOnProposalProcessedGeometryExportSerializer(qs_vacant_site_proposal.filter(wkb_geometry_processed__isnull=False), many=True)
        serializer_vacant_approval = ApiarySiteOnApprovalGeometryExportSerializer(qs_vacant_site_approval, many=True)

        # ApiarySiteOnProposal
        qs_on_proposal_draft, qs_on_proposal_processed = get_qs_proposal()
        serializer_proposal_processed = ApiarySiteOnProposalProcessedGeometryExportSerializer(qs_on_proposal_processed, many=True)
        serializer_proposal_draft = ApiarySiteOnProposalDraftGeometryExportSerializer(qs_on_proposal_draft, many=True)

        # ApiarySiteOnApproval
        qs_on_approval = get_qs_approval()
        serializer_approval = ApiarySiteOnApprovalGeometryExportSerializer(qs_on_approval, many=True)

        # Merge all the data above
        serializer_approval.data['features'].extend(serializer_proposal_draft.data['features'])
        serializer_approval.data['features'].extend(serializer_proposal_processed.data['features'])
        serializer_approval.data['features'].extend(serializer_vacant_proposal_d.data['features'])
        serializer_approval.data['features'].extend(serializer_vacant_proposal.data['features'])
        serializer_approval.data['features'].extend(serializer_vacant_approval.data['features'])

        save_dir = os.path.join(BASE_DIR, SPATIAL_DATA_DIR)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        file_path = os.path.join(save_dir, 'test.json')  # TODO: we jsut want to keep latest 3 files or so.
        with open(file_path, 'w') as fp:
            json.dump(serializer_approval.data, fp)
