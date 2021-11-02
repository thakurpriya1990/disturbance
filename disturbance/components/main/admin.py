from django.contrib import admin

from disturbance.components.main.models import MapLayer


@admin.register(MapLayer)
class AmendmentReasonAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'layer_name', 'option_for_internal', 'option_for_external',]
