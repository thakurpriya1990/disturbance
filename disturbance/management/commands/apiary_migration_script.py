from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from pathlib import Path
from disturbance.utils.migration_utils import ApiaryLicenceReader
import datetime

import itertools
import subprocess

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run the Apiary Migrations Script'

    def handle(self, *args, **options):
        alr=ApiaryLicenceReader('disturbance/utils/apiary_migration_file_07Jun2021.csv')
        alr.run_migration()
