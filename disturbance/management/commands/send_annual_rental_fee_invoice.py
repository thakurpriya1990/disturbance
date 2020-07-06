import datetime

import pytz
from django.core.management.base import BaseCommand
import logging
from django.db.models import Q, Min
from ledger.settings_base import TIME_ZONE

from disturbance.components.approvals.models import Approval
from disturbance.components.das_payments.utils import create_other_invoice_for_annual_rental_fee
from disturbance.components.proposals.models import ApiaryAnnualRentalFeeRunDate, ApiaryAnnualRentalFeePeriodStartDate

logger = logging.getLogger(__name__)


def get_annual_rental_fee_period(target_date):
    """
    Retrieve the annual rental fee period, on the target_date the invoice for it should be issued
    """
    target_date_year = target_date.year

    # Calculate cron job period
    run_date = ApiaryAnnualRentalFeeRunDate.objects.get(name=ApiaryAnnualRentalFeeRunDate.NAME_CRON)
    run_date_month = run_date.date_run_cron.month
    run_date_day = run_date.date_run_cron.day

    # Calculate the run_date in the year where the target_date is in
    prev_run_date = datetime.date(year=target_date_year, month=run_date_month, day=run_date_day)
    if prev_run_date > target_date:
        # prev_run_date calculated above is in the future.  Calculate one before that
        prev_run_date = datetime.date(year=prev_run_date.year-1, month=prev_run_date.month, day=prev_run_date.day)

    # Calculate annual rental fee period
    # annual rental fee start date must be between the prev_run_date and next_run_date
    start_date = ApiaryAnnualRentalFeePeriodStartDate.objects.get(name=ApiaryAnnualRentalFeePeriodStartDate.NAME_PERIOD_START)
    period_start_date_month = start_date.period_start_date.month
    period_start_date_day = start_date.period_start_date.day

    # Calculate the period start date in the year where the prev_run_date is in
    period_start_date = datetime.date(year=prev_run_date.year, month=period_start_date_month, day=period_start_date_day)
    if period_start_date < prev_run_date:
        # period_start_date calculated above is before the previous cron job run date.  Calculate the next one
        period_start_date = datetime.date(year=period_start_date.year+1, month=period_start_date.month, day=period_start_date.day)

    period_end_date = datetime.date(year=period_start_date.year+1, month=period_start_date.month, day=period_start_date.day) - datetime.timedelta(days=1)

    return period_start_date, period_end_date


class Command(BaseCommand):
    help = 'Send annual rent fee invoices for the apiary'

    def handle(self, *args, **options):
        try:
            # TODO 1. Determine the start and end date of the annual rental fee, for which the invoices should be issued
            today_local = datetime.datetime.now(pytz.timezone(TIME_ZONE)).date()
            period_start_date, period_end_date = get_annual_rental_fee_period(today_local)

            # TODO 2. Retrieve the licences which will be valid within the current annual rental fee period


            # TODO 3. Issue the invoices if not issued yet
            #       Invoice.objects.exclude(payment_status__in=('paid', 'overpaid')

            q_objects = Q()
            q_objects &= Q(id=323)

            approval_qs = Approval.objects.filter(q_objects)

            for approval in approval_qs:
                invoice = create_other_invoice_for_annual_rental_fee(approval)

                # TODO: Attach the invoice and send emails


        except Exception as e:
            logger.error('Error command {}'.format(__name__))
