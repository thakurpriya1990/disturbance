from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
import os, time

#import itertools
#import subprocess

import logging
logger = logging.getLogger(__name__)

#LOGFILE = 'logs/cron_tasks.log'

class Command(BaseCommand):
    help = f'script to clear old export shape files (older than {settings.CLEAR_AFTER_DAYS_FILE_EXPORT} days)'

    def handle(self, *args, **options):
        logger.info('Running command {}'.format(__name__))

        path = "geo_exports"
        now = time.time()
        days = settings.CLEAR_AFTER_DAYS_FILE_EXPORT # delete files older than <days> old
     
        # Delete from the Folder
        count = 0
        for filename in os.listdir(path):
            filestamp = os.stat(os.path.join(path, filename)).st_mtime
            days_ago = now - days * 86400
            if filestamp < days_ago:
                try:
                    filepath = path + os.sep + filename
                    os.remove(filepath)

                    logger.info(f'Deleted: {filepath}')
                    count += 1
                except OSError as e:
                    logger.error(f'Failed to Delete: {e.filename}, {e.strerror}')
                except Exception as ex:
                    logger.error(f'Failed to Delete: {ex}')

        # Delete from the DB Table
        ExportDocument.old_files.all().delete()

#        subject = "DAS - Layers Used CSV"
#        body = "CSV file for Layers used in proposal applications, where:\n\t1. Proposal polygon/layer(s) exist (DAS Phase 2),\n\t2. Approved proposals"
#        message = EmailMessage(subject=subject, body=body, from_email=settings.EMAIL_FROM, to=[settings.NOTIFICATION_EMAIL])
#        message.attach(f'layers_used_{datetime.now().strftime("%Y%m%dT%H%M")}.csv', csvfile.getvalue(), 'text/csv')
#        message.send()

        logger.info(f'Command {__name__} completed: Files deleted {count}')

