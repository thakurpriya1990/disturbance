from django.core.management.base import BaseCommand
from disturbance.components.approvals.models import ApiarySiteOnApproval

import xlsxwriter                                                                                                                                                                                     
from io import BytesIO
from datetime import datetime
from django.core.mail import EmailMessage


class Command(BaseCommand):
    help = 'Write Apiary Sites to Excel file and emails the file as an attachment (emails to apiary@dpaw.wa.gov.au)'

    def handle(self, *args, **options):

        date_str = datetime.now().date().strftime('%Y%m%d')                                                                                                                                                   
        output = BytesIO()
        col = 0
        with xlsxwriter.Workbook(output,{'in_memory': True}) as wb:                                                                                                                                           
            sheet = wb.add_worksheet()                                                                                                                                                                        

            line = ['Applicant', 'Site ID', 'Site Status', 'Zone', 'Licensed Site']
            sheet.write_row(0, col, line)
            for row, asoa in enumerate(ApiarySiteOnApproval.objects.all().order_by('approval__current_proposal__applicant'), 1):
                line = [asoa.approval.current_proposal.applicant.name, asoa.apiary_site_id, asoa.site_status, asoa.zone, asoa.licensed_site]
                sheet.write_row(row, col, line)

        email = EmailMessage(
            subject=f'Apiary Sites List - {date_str}',
            body='Please find attached Excel WB with list of Apiary Sites.',
            from_email='no-reply@dbca.wa.gov.au',
            #to=['apiary@dpaw.wa.gov.au'],
            to=['jawaid.mushtaq@dbca.wa.gov.au'],
            cc=[],
            reply_to=['no-reply@dbca.wa.gov.au'],
            headers=None,
        )

        email.attach(f'apiary_sites_{date_str}.xlsx', output.getvalue() , 'application/vnd.ms-excel')
        email.send()



