from rest_framework.permissions import BasePermission

from disturbance.helpers import (
    is_das_assessor,
    is_internal,
    is_das_approver,
    is_das_referrer,
)

class InternalProposalPermission(BasePermission):

    def has_permission(self, request, view):
        return is_internal(request)

class ProposalAssessorPermission(BasePermission):

    def has_permission(self, request, view):
        return is_das_assessor(request)

class ProposalApproverPermission(BasePermission):

    def has_permission(self, request, view):
        return is_das_approver(request)
    
class ProposalReferrerPermission(BasePermission):

    def has_permission(self, request, view):
        return is_das_referrer(request)