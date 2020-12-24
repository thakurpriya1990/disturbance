import datetime
import json
import os

import pytz
from django.core.management.base import BaseCommand
from ledger.settings_base import TIME_ZONE

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

        datetime_local = datetime.datetime.now(pytz.timezone(TIME_ZONE)).strftime('%Y%m%d-%H%M%S')
        file_path = os.path.join(save_dir, '{}-apiary-sites.json'.format(datetime_local))
        with open(file_path, 'w') as fp:
            json.dump(serializer_approval.data, fp)

        files = os.listdir(save_dir)
        files = sorted(files, reverse=True)  # sort by descending order
        for file in files[3:]:
            os.remove(os.path.join(save_dir, file))
