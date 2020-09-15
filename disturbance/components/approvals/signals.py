from django.db.models.signals import post_save
from django.dispatch import receiver

from disturbance.components.approvals.models import ApiarySiteOnApproval


class ApiarySiteOnProposalListener(object):
    """
    Event listener for the ApiarySiteOnProposal
    """
    @staticmethod
    @receiver(post_save, sender=ApiarySiteOnApproval)
    def _post_save(sender, instance, **kwargs):

        # TODO: update apairy_site.latest_approval_link

        pass

