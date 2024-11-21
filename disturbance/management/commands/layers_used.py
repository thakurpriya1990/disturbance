from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from disturbance.components.approvals.models import Proposal
#from ledger.accounts.models import EmailUser
from datetime import datetime
from six.moves import StringIO
import csv

#import itertools
#import subprocess

import logging
logger = logging.getLogger(__name__)

#LOGFILE = 'logs/cron_tasks.log'

class Command(BaseCommand):
    help = 'Run the Disturbance Layers User script'

    def handle(self, *args, **options):
        logger.info('Running command {}'.format(__name__))

        csvfile = StringIO()
        csvwriter = csv.writer(csvfile)

        #rows = []
        #rows.append(('Proposal Number', 'Proposal Submitter', 'Status', 'Proposal Section', 'Layer Name', 'Layer Version', 'Layer Modified Date', 'SQS Timestamp'))
        csvwriter.writerow(('Proposal Number', 'Proposal Submitter', 'Status', 'Proposal Section', 'Layer Name', 'Layer Version', 'Layer Modified Date', 'SQS Timestamp'))
        #for p in Proposal.objects.filter(layer_data__isnull=False):
        for p in Proposal.objects.filter(layer_data__isnull=False, processing_status=Proposal.PROCESSING_STATUS_APPROVED):
            for data in p.layer_data:
                #rows.append((p.lodgement_number, p.submitter, p.processing_status, data['name'], data['layer_name'], data['layer_version'], data['layer_modified_date'], data['sqs_timestamp']))
                csvwriter.writerow(
                    (p.lodgement_number, p.submitter, p.processing_status, data['name'], data['layer_name'], data['layer_version'], data['layer_modified_date'], data['sqs_timestamp'])
                )

#        for row in rows:
#            csvwriter.writerow(row)  

        subject = "DAS - Layers Used CSV"
        body = "CSV file for Layers used in proposal applications, where:\n\t1. Proposal polygon/layer(s) exist (DAS Phase 2),\n\t2. Approved proposals"
        message = EmailMessage(subject=subject, body=body, from_email=settings.EMAIL_FROM, to=[settings.NOTIFICATION_EMAIL])
        message.attach(f'layers_used_{datetime.now().strftime("%Y%m%dT%H%M")}.csv', csvfile.getvalue(), 'text/csv')
        message.send()

        logger.info('Command {} completed'.format(__name__))


