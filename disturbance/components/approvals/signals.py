from django.db.models.signals import post_save
from django.dispatch import receiver

from disturbance.components.approvals.models import ApiarySiteOnApproval


class ApiarySiteOnApprovalListener(object):
    """
    Event listener for the ApiarySiteOnApproval
    """
    @staticmethod
    @receiver(post_save, sender=ApiarySiteOnApproval)
    def _post_save(sender, instance, **kwargs):
        instance.apiary_site.latest_approval_link = instance
        instance.apiary_site.save()

