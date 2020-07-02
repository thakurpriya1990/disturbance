from django.core.management.base import BaseCommand
import logging

from disturbance.components.approvals.models import Approval
from disturbance.components.das_payments.utils import create_other_invoice_for_annual_rental_fee

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send annual rent fee invoices for the apiary'

    def handle(self, *args, **options):
        try:
            # TODO: Retrieve the apiary licences (id=323 for develop)
            approval = Approval.objects.get(id=323)

            # Create invoices
            invoice = create_other_invoice_for_annual_rental_fee(approval)

            # 2. Create invoice
            # TODO: Attach the invoice and send emails
            pass

        except Exception as e:
            logger.error('Error command {}'.format(__name__))
