import os
from io import BytesIO

from django.conf import settings
from docxtpl import DocxTemplate
from disturbance.components.main.models import ApiaryGlobalSettings


def create_apiary_licence_pdf_contents(approval):
    # print ("Letter File")
    # confirmation_doc = None
    # if booking.annual_booking_period_group.letter:
    #     print (booking.annual_booking_period_group.letter.path)
    #     confirmation_doc = booking.annual_booking_period_group.letter.path
    # confirmation_doc = settings.BASE_DIR+"/mooring/templates/doc/AnnualAdmissionStickerLetter.docx"

    licence_template = ApiaryGlobalSettings.objects.get(key=ApiaryGlobalSettings.KEY_APIARY_LICENCE_TEMPLATE_FILE)

    doc = DocxTemplate(licence_template._file.path)
    # address = ''
    # if len(booking.details.get('postal_address_line_2', '')) > 0:
    #     address = '{}, {}'.format(booking.details.get('postal_address_line_1', ''),
    #                               booking.details.get('postal_address_line_2', ''))
    # else:
    #     address = '{}'.format(booking.details.get('postal_address_line_1', ''))
    # bookingdate = booking.created + timedelta(hours=8)
    # todaydate = datetime.utcnow() + timedelta(hours=8)
    # stickercreated = ''
    # if booking.sticker_created:
    #     sc = booking.sticker_created + timedelta(hours=8)
    #     stickercreated = sc.strftime('%d %B %Y')

    context = {
        'approval_id': 'aho',
        # 'customername': '{} {}'.format(booking.details.get('first_name', ''), booking.details.get('last_name', '')),
        # 'customeraddress': address, "customersuburb": booking.details.get('suburb', ''),
        # "customerstate": booking.details.get('state', ''), 'customerpostcode': booking.details.get('post_code', ''),
        # 'bookingyear': '{}/{}'.format(booking.annual_booking_period_group.start_time.strftime('%Y'),
        #                               booking.annual_booking_period_group.finish_time.strftime('%y')),
        # 'admissionsexpiry': booking.annual_booking_period_group.finish_time.strftime('%d %B %Y'),
        # 'vessel': booking.details.get('vessel_rego', ''), 'customerfirstname': booking.details.get('first_name', ''),
        # 'bookingdate': booking.created.strftime('%d %B %Y'), 'todaydate': todaydate.strftime('%d %B %Y'),
        # 'stickercreated': stickercreated}
    }
    doc.render(context)

    temp_directory = settings.BASE_DIR + "/tmp/"
    try:
        os.stat(temp_directory)
    except:
        os.mkdir(temp_directory)

    f_name = temp_directory + 'apiary_licence_' + str(approval.id)
    new_doc_file = f_name + '.docx'
    new_pdf_file = f_name + '.pdf'
    doc.save(new_doc_file)
    os.system("libreoffice --headless --convert-to pdf " + new_doc_file + " --outdir " + temp_directory)

    file_contents = None
    with open(new_pdf_file, 'rb') as f:
        file_contents = f.read()
    os.remove(new_doc_file)
    os.remove(new_pdf_file)
    return file_contents
