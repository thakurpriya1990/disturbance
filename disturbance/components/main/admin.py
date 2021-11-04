from django.contrib import admin
from django.forms import ModelForm

from disturbance.components.main.models import MapLayer


class MyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        self.fields['layer_name'].help_text = "Enter the layer name defined in geoserver (<a href='https://kmi.dpaw.wa.gov.au/geoserver/' target='_blank'>GeoServer</a>)<br />" \
        "e.g.<br />public:dbca_legislated_lands_and_waters"


@admin.register(MapLayer)
class AmendmentReasonAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'layer_name', 'option_for_internal', 'option_for_external',]
    form = MyForm
