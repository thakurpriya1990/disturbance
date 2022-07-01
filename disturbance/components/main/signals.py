from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from disturbance.components.main.models import ApiaryGlobalSettings

logger = logging.getLogger(__name__)


class ApiaryGlobalSettingsListener(object):
    """
    Event listener for the ApiarySiteOnApproval
    """
    @staticmethod
    @receiver(post_save, sender=ApiaryGlobalSettings)
    def _post_save(sender, instance, **kwargs):
        from disturbance.components.main.utils import overwrite_regions_polygons, overwrite_districts_polygons

        if instance.key == ApiaryGlobalSettings.KEY_DBCA_REGIONS_FILE:
            overwrite_regions_polygons(instance._file.path)
        elif instance.key == ApiaryGlobalSettings.KEY_DBCA_DISTRICTS_FILE:
            overwrite_districts_polygons(instance._file.path)

