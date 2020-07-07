import datetime

import pytz
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
import logging
from django.db.models import Q, Min
from ledger.settings_base import TIME_ZONE

from disturbance.components.approvals.models import Approval
from disturbance.components.das_payments.models import AnnualRentalFee, AnnualRentalFeePeriod
from disturbance.components.das_payments.utils import create_other_invoice_for_annual_rental_fee
from disturbance.components.proposals.models import ApiaryAnnualRentalFeeRunDate, ApiaryAnnualRentalFeePeriodStartDate

logger = logging.getLogger(__name__)


def get_annual_rental_fee_period(target_date):
    """
    Retrieve the annual rental fee period, the invoice for this period should have been issued on the target_date passed as a parameter
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


def get_approvals_valid_in_range(period_start_date, period_end_date):
    # Retrieve the licences which will be valid within this period
    q_objects = Q()
    q_objects &= Q(apiary_approval=True)
    q_objects &= Q(expiry_date__gte=period_start_date)
    q_objects &= Q(status=Approval.STATUS_CURRENT)
    # TODO: More conditions needed?
    # q_objects = Q(id=323)
    approval_qs = Approval.objects.filter(q_objects)

    return approval_qs


class Command(BaseCommand):
    help = 'Send annual rent fee invoices for the apiary'

    def handle(self, *args, **options):
        try:
            # Determine the start and end date of the annual rental fee, for which the invoices should be issued
            today_local = datetime.datetime.now(pytz.timezone(TIME_ZONE)).date()
            period_start_date, period_end_date = get_annual_rental_fee_period(today_local)

            # Retrieve annual rental fee period object for the period calculated above
            # This period should not overwrap the existings, otherwise you will need a refund
            annual_rental_fee_period, created = AnnualRentalFeePeriod.objects.get_or_create(period_start_date=period_start_date, period_end_date=period_end_date)


            # Retrieve the licences which will be valid within the current annual rental fee period
            approval_qs = get_approvals_valid_in_range(period_start_date, period_end_date)

            # Issue the annual rental fee invoices per approval per annual_rental_fee_period
            for approval in approval_qs:

                # TODO: check if it exists per apairy site under this approval
                annual_rental_fee, created = AnnualRentalFee.objects.get_or_create(approval=approval, annual_rental_fee_period=annual_rental_fee_period)

                if not annual_rental_fee.invoice_reference:

                    # Issue an invoice for the approval
                    invoice = create_other_invoice_for_annual_rental_fee(approval)  # TODO: calculate the fee accounting for the number of sites

                    # Update annual_rental_fee obj
                    annual_rental_fee.invoice_reference = invoice.reference
                    annual_rental_fee.invoice_period_start_date = annual_rental_fee_period.period_start_date
                    annual_rental_fee.invoice_period_end_date = annual_rental_fee_period.period_end_date
                    annual_rental_fee.save()

                    # TODO: Store the apiary sites which the invoice has been issued for (create AnnualRentalFeeApiarySite)

                    # TODO: Attach the invoice and send emails

        except Exception as e:
            logger.error('Error command {}'.format(__name__))
