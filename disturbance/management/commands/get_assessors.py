from django.core.management.base import BaseCommand
from disturbance.components.proposals.models import ProposalUserAction
from django.db.models.query_utils import Q


class Command(BaseCommand):
    help = 'Change the status of Compliances from future to due when they are close to due date'

    def handle(self, *args, **options):

        print(f'User_ID, User, Action')
        for i in ProposalUserAction.objects.filter(Q(what__icontains='proposed for approval') | Q(what__icontains='Assign proposal') | Q(what__icontains='Request amendments') |Q(what__icontains='Decline proposal') | Q(what__icontains='proposed for decline') | Q(what__icontains='Enter Requirements') | Q(what__icontains='Send referral')):
            print(f'{i.id}, {i.who}, {i.what}')
