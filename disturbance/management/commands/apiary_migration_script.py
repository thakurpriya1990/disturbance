from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from pathlib import Path
from disturbance.utils.migration_utils import ApiaryLicenceReader
from disturbance.components.proposals.models import Proposal
from disturbance.components.approvals.models import Approval
import datetime

import itertools
import subprocess

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run the Apiary Migrations Script'

    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, *args, **options):
        import ipdb; ipdb.set_trace()
        filename = options['filename']
        #alr=ApiaryLicenceReader('disturbance/utils/apiary_migration_file_07Jun2021.csv')
        alr=ApiaryLicenceReader(filename)
        alr.run_migration()


        proposals = Proposal.objects.filter(migrated=True).count()
        approvals = Approval.objects.filter(migrated=True).count()
        print(f'Proposals {proposals}, Approvals {approvals}')
