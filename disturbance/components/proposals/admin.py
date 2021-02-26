import os

from django.contrib import admin
from ledger.accounts.models import EmailUser

import disturbance
from disturbance.components.proposals import models
from disturbance.components.proposals import forms
from disturbance.components.main.models import ActivityMatrix, SystemMaintenance, ApplicationType, GlobalSettings, \
    ApiaryGlobalSettings
#from disturbance.components.main.models import Activity, SubActivityLevel1, SubActivityLevel2, SubCategory
from reversion.admin import VersionAdmin
from django.conf.urls import url
from django.template.response import TemplateResponse
from django.http import HttpResponse, HttpResponseRedirect

from disturbance.components.proposals.models import SiteCategory, ApiarySiteFee, ApiarySiteFeeType, \
    ApiaryAnnualRentalFee, \
    ApiaryAnnualRentalFeeRunDate, ApiaryAnnualRentalFeePeriodStartDate
from disturbance.utils import create_helppage_object
from disturbance.helpers import is_apiary_admin, is_disturbance_admin, is_das_apiary_admin
# Register your models here.

@admin.register(models.ProposalType)
class ProposalTypeAdmin(admin.ModelAdmin):
    list_display = ['name','description', 'version']
    ordering = ('name', '-version')
    list_filter = ('name',)
    #exclude=("site",)

class ProposalDocumentInline(admin.TabularInline):
    model = models.ProposalDocument
    extra = 0

@admin.register(models.AmendmentReason)
class AmendmentReasonAdmin(admin.ModelAdmin):
    list_display = ['reason']

@admin.register(models.Proposal)
class ProposalAdmin(VersionAdmin):
    inlines =[ProposalDocumentInline,]

@admin.register(models.ProposalAssessorGroup)
class ProposalAssessorGroupAdmin(admin.ModelAdmin):
    list_display = ['name','default']
    filter_horizontal = ('members',)
    form = forms.ProposalAssessorGroupAdminForm
    readonly_fields = ['default']
    #readonly_fields = ['regions', 'activities']

    def has_delete_permission(self, request, obj=None):
        if obj and obj.default:
            return False
        return super(ProposalAssessorGroupAdmin, self).has_delete_permission(request, obj)

@admin.register(models.ProposalApproverGroup)
class ProposalApproverGroupAdmin(admin.ModelAdmin):
    list_display = ['name','default']
    filter_horizontal = ('members',)
    form = forms.ProposalApproverGroupAdminForm
    readonly_fields = ['default']
    #readonly_fields = ['default', 'regions', 'activities']

    def has_delete_permission(self, request, obj=None):
        if obj and obj.default:
            return False
        return super(ProposalApproverGroupAdmin, self).has_delete_permission(request, obj)

@admin.register(models.ApiaryReferralGroup)
class ApiaryReferralGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)
    list_display = ['name']
    exclude = ('site',)
    actions = None

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "members":
            kwargs["queryset"] = EmailUser.objects.filter(is_staff=True)
        return super(ApiaryReferralGroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(models.ApiaryAssessorGroup)
class ApiaryAssessorGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)
    exclude = ('site',)
    actions = None

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "members":
            #kwargs["queryset"] = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')
            kwargs["queryset"] = EmailUser.objects.filter(is_staff=True)
        return super(ApiaryAssessorGroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def has_add_permission(self, request):
        return True if models.ApiaryAssessorGroup.objects.count() == 0 else False

    def has_delete_permission(self, request, obj=None):
        return False 


@admin.register(models.ApiaryApproverGroup)
class ApiaryApproverGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)
    exclude = ('site',)
    actions = None

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "members":
            #kwargs["queryset"] = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')
            kwargs["queryset"] = EmailUser.objects.filter(is_staff=True)
        return super(ApiaryApproverGroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def has_add_permission(self, request):
        return True if models.ApiaryApproverGroup.objects.count() == 0 else False

    def has_delete_permission(self, request, obj=None):
        return False 


@admin.register(models.ProposalStandardRequirement)
class ProposalStandardRequirementAdmin(admin.ModelAdmin):
    list_display = ['code','text','system','obsolete']
    #readonly_fields=('system',)
    #list_filter=('system',)

    def get_queryset(self, request):
        #import ipdb;ipdb.set_trace()
        # filter based on membership of Apiary Admin or Disturbance Admin
        qs = super(ProposalStandardRequirementAdmin, self).get_queryset(request)
        if request.user.is_superuser or is_das_apiary_admin(request):
            return qs
        group_list = []
        if is_apiary_admin(request):
            group_list.append('apiary')
        if is_disturbance_admin(request):
            group_list.append('disturbance')
        return qs.filter(system__in=group_list)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'system':
            if (request.user.is_superuser or is_das_apiary_admin(request) or 
                    (is_apiary_admin(request) and is_disturbance_admin(request))
                    ):
                # user will see both choices
                kwargs["choices"] = (
                        ('apiary', 'Apiary'),
                        ('disturbance', 'Disturbance'),
                        )
            elif is_apiary_admin(request):
                kwargs["choices"] = (('apiary', 'Apiary'),)
            elif is_disturbance_admin(request):
                kwargs["choices"] = (('disturbance', 'Disturbance'),)
        return super(ProposalStandardRequirementAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)


@admin.register(models.HelpPage)
class HelpPageAdmin(admin.ModelAdmin):
    list_display = ['application_type','help_type', 'description', 'version']
    form = forms.DisturbanceHelpPageAdminForm
    change_list_template = "disturbance/help_page_changelist.html"
    ordering = ('application_type', 'help_type', '-version')
    list_filter = ('application_type', 'help_type')


    def get_urls(self):
        urls = super(HelpPageAdmin, self).get_urls()
        my_urls = [
            url('create_disturbance_help/', self.admin_site.admin_view(self.create_disturbance_help)),
            url('create_apiary_help/', self.admin_site.admin_view(self.create_apiary_help)),
            url('create_disturbance_help_assessor/', self.admin_site.admin_view(self.create_disturbance_help_assessor)),
            url('create_apiary_help_assessor/', self.admin_site.admin_view(self.create_apiary_help_assessor)),
        ]
        return my_urls + urls

    def create_disturbance_help(self, request):
        create_helppage_object(application_type='Disturbance', help_type=models.HelpPage.HELP_TEXT_EXTERNAL)
        return HttpResponseRedirect("../")

    def create_apiary_help(self, request):
        create_helppage_object(application_type='Apiary', help_type=models.HelpPage.HELP_TEXT_EXTERNAL)
        return HttpResponseRedirect("../")

    def create_disturbance_help_assessor(self, request):
        create_helppage_object(application_type='Disturbance', help_type=models.HelpPage.HELP_TEXT_INTERNAL)
        return HttpResponseRedirect("../")

    def create_apiary_help_assessor(self, request):
        create_helppage_object(application_type='Apiary', help_type=models.HelpPage.HELP_TEXT_INTERNAL)
        return HttpResponseRedirect("../")


@admin.register(ActivityMatrix)
class ActivityMatrixAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'version']
    ordering = ('name', '-version')


@admin.register(SystemMaintenance)
class SystemMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'start_date', 'end_date', 'duration']
    ordering = ('start_date',)
    readonly_fields = ('duration',)
    form = forms.SystemMaintenanceAdminForm


@admin.register(ApplicationType)
class ApplicationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'visible', 'domain_used',]
    ordering = ('order',)


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']
    ordering = ('key',)


@admin.register(ApiaryGlobalSettings)
class ApiaryGlobalSettingsAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        if obj.key == ApiaryGlobalSettings.KEY_APIARY_LICENCE_TEMPLATE_FILE:
            return ['key', '_file',]
        else:
            return ['key', 'value',]

    def get_readonly_fields(self, request, obj=None):
        return ['key',]

    def get_form(self, request, obj=None, **kwargs):
        form = super(ApiaryGlobalSettingsAdmin, self).get_form(request, obj, **kwargs)
        if obj.key == ApiaryGlobalSettings.KEY_APIARY_SITES_LIST_TOKEN:
            link_to = '/api/apiary_site/export/?' + ApiaryGlobalSettings.KEY_APIARY_SITES_LIST_TOKEN + '=' + obj.value
            http_host = request.META['HTTP_HOST']
            display_link_to = http_host + link_to
            form.base_fields['value'].help_text = '<a href="' + link_to + '">' + display_link_to + '</a>'
        return form

    list_display = ['key', 'value', '_file',]
    ordering = ('key',)


@admin.register(ApiaryAnnualRentalFee)
class ApiaryAnnualRentalFeeAdmin(admin.ModelAdmin):
    pass


@admin.register(ApiaryAnnualRentalFeeRunDate)
class ApiaryAnnualRentalFeeRunDateAdmin(admin.ModelAdmin):
    pass


# @admin.register(ApiaryAnnualRentalFeePeriodStartDate)
# class ApiaryAnnualRentalFeePeriodStartDateAdmin(admin.ModelAdmin):
#     pass

# class SiteApplicationFeeInline(admin.TabularInline):
#     model = SiteApplicationFee
#     extra = 0
#     can_delete = True


class ApiarySiteFeeInline(admin.TabularInline):
    model = ApiarySiteFee
    extra = 0
    can_delete = True
    fields = ('apiary_site_fee_type', 'amount', 'date_of_enforcement',)


@admin.register(ApiarySiteFeeType)
class ApiarySiteFeeTypeAdmin(admin.ModelAdmin):
    pass


# @admin.register(SiteApplicationFee)
# class SiteApplicationFeeAdmin(admin.ModelAdmin):
#     pass


class SiteCategoryAdmin(admin.ModelAdmin):

    inlines = [ApiarySiteFeeInline,]


admin.site.register(disturbance.components.proposals.models.SiteCategory, SiteCategoryAdmin)

@admin.register(models.ApiaryChecklistQuestion)
class ApiaryChecklistQuestionAdmin(admin.ModelAdmin):
    #list_display = ['text', 'answer_type', 'order']
    ordering = ('order',)


@admin.register(models.QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ['label','value']
    #ordering = ('order',)

@admin.register(models.MasterlistQuestion)
class MasterlistQuestionAdmin(admin.ModelAdmin):
    list_display = ['name', 'question',]
    filter_horizontal = ('option',)
    form = forms.MasterlistQuestionAdminForm
    #exclude = ('site',)
    #actions = None

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     if db_field.name == "members":
    #         #kwargs["queryset"] = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')
    #         kwargs["queryset"] = EmailUser.objects.filter(is_staff=True)
    #     return super(ApiaryAssessorGroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    # def has_add_permission(self, request):
    #     return True if models.ApiaryAssessorGroup.objects.count() == 0 else False

    # def has_delete_permission(self, request, obj=None):
    #     return False 

@admin.register(models.ProposalTypeSection)
class ProposalTypeSectionAdmin(admin.ModelAdmin):
    list_display = ['proposal_type', 'index', 'section_name', 'section_label',]
   
@admin.register(models.SectionQuestion)
class SectionQuestionAdmin(admin.ModelAdmin):
    list_display = ['section', 'question','parent_question','parent_answer']
    #filter_horizontal = ('option',)
    form = forms.SectionQuestionAdminForm

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "parent_question":
    #         #kwargs["queryset"] = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')
    #         kwargs["queryset"] = models.MasterlistQuestion.objects.filter(option__isnull=False).distinct()
    #     # if db_field.name == "parent_answer":
    #     #     #kwargs["queryset"] = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')

    #     #     kwargs["queryset"] = self.parent_question.option.all()
    #     return super(SectionQuestionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)



    # def formfield_for_choice_field(self, db_field, request, **kwargs):
    #     # if db_field.name == "parent_question":
    #     #     #kwargs["queryset"] = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')
    #     #     kwargs["queryset"] = MasterlistQuestion.objects.filter(option__isnull=False).distinct()
    #     if db_field.name == "parent_answer":
    #         #kwargs["queryset"] = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')
    #         kwargs["queryset"] = self.parent_question.option.all()
    #     return super(SectionQuestionAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)

