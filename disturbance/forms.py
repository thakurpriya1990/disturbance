from __future__ import unicode_literals
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Row, Column, Field
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms import Form, ModelForm, CharField, ValidationError, EmailField
from django import forms

from ledger.accounts.models import Profile, Address, Organisation


User = get_user_model()


class LoginForm(Form):
    email = EmailField(max_length=254)

class PersonalForm(ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_emailuserprofile_update'
        self.helper.attrs = {'novalidate': ''}
        # Define the form layout.
        self.helper.layout = Layout(
            'first_name', 'last_name', 
            FormActions(
                Submit('save', 'Save', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )

class ContactForm(ModelForm):

    class Meta:
        model = User
        fields = ['email', 'phone_number','mobile_number']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_emailuserprofile_update'
        self.helper.attrs = {'novalidate': ''}
        # Define the form layout.
        self.helper.layout = Layout(
            'phone_number', 'mobile_number','email', 
            FormActions(
                Submit('save', 'Save', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )


class AddressForm(ModelForm):

    class Meta:
        model = Address
        fields = ['line1', 'line2', 'locality', 'state', 'postcode']

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_address'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class OrganisationAdminForm(ModelForm):
    """ModelForm that is used in the Django admin site.
    """
    model = Organisation

    def clean_abn(self):
        data = self.cleaned_data['abn']
        # If it's changed, check for any existing organisations with the same ABN.
        if data and self.instance.abn != data and Organisation.objects.filter(abn=data).exists():
            raise ValidationError('An organisation with this ABN already exists.')
        return data


class OrganisationForm(OrganisationAdminForm):

    class Meta:
        model = Organisation
        fields = ['name', 'abn', 'identification']

    def __init__(self, *args, **kwargs):
        super(OrganisationForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Company name'
        self.fields['identification'].label = 'Certificate of incorporation'
        self.fields['identification'].help_text = 'Electronic copy of current certificate (e.g. image/PDF)'
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_organisation'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class DelegateAccessForm(Form):

    def __init__(self, *args, **kwargs):
        super(DelegateAccessForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.add_input(Submit('confirm', 'Confirm', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class UnlinkDelegateForm(ModelForm):

    class Meta:
        model = Organisation
        exclude = ['name', 'abn', 'identification', 'postal_address', 'billing_address', 'delegates']

    def __init__(self, *args, **kwargs):
        super(UnlinkDelegateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.add_input(Submit('unlink', 'Unlink user', css_class='btn-lg btn-danger'))
        self.helper.add_input(Submit('cancel', 'Cancel'))



class BaseFormHelper(FormHelper):
    """
    Base helper class for rendering forms via crispy_forms.
    To remove the default "Save" button from the helper, instantiate it with
    inputs=[]
    E.g. helper = BaseFormHelper(inputs=[])
    """
    def __init__(self, *args, **kwargs):
        super(BaseFormHelper, self).__init__(*args, **kwargs)
        self.form_class = 'horizontal col-lg-2'
        self.help_text_inline = True
        self.form_method = 'POST'
        save_btn = Submit('submit', 'Save')
        save_btn.field_classes = 'btn btn-primary'
        cancel_btn = Submit('cancel', 'Cancel')
        self.add_input(save_btn)
        self.add_input(cancel_btn)
 
 
class HelperModelForm(forms.ModelForm):
    """
    Stock ModelForm with a property named ``helper`` (used by crispy_forms to
    render in templates).
    """
    @property
    def helper(self):
        helper = BaseFormHelper()
        return helper


from disturbance.settings import SITE_STATUS_DRAFT, SITE_STATUS_APPROVED, SITE_STATUS_CURRENT, SITE_STATUS_DENIED, SITE_STATUS_NOT_TO_BE_REISSUED, SITE_STATUS_VACANT, SITE_STATUS_TRANSFERRED, SITE_STATUS_DISCARDED, SITE_STATUS_SUSPENDED
class ApiarySiteStatusForm(forms.Form):

    SITE_STATUS_CHOICES = (
        ('', 'Select status ...'),
        #(SITE_STATUS_DRAFT, 'Draft'),
        #(SITE_STATUS_PENDING, 'Pending'),
        #(SITE_STATUS_APPROVED, 'Approved'),
        (SITE_STATUS_DENIED, 'Denied'),
        (SITE_STATUS_CURRENT, 'Current'),
        (SITE_STATUS_NOT_TO_BE_REISSUED, 'Not to be reissued'),
        (SITE_STATUS_SUSPENDED, 'Suspended'),
        #(SITE_STATUS_TRANSFERRED, 'Transferred'),
        #(SITE_STATUS_VACANT, 'Vacant'),
        (SITE_STATUS_DISCARDED, 'Discarded'),
    )

    site_id = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Site ID'}))
    status = forms.ChoiceField(choices=SITE_STATUS_CHOICES)

    def __init__(self, *args, **kwargs):
        super(ApiarySiteStatusForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.id = 'id_apiary_site_status_form'
        #self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Field('site_id', wrapper_class='col-md-4'),
                Field('status', wrapper_class='col-md-4'),
                css_class = "row"
            ),
            Submit('submit_apiary_site_status_form', 'Update'),
        )


class ApiarySiteLonLatForm(forms.Form):
    site_id = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Site ID'}))
    longitude = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder': 'Site Longitude'}))
    latitude = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder': 'Site Latitude'}))

    def __init__(self, *args, **kwargs):
        super(ApiarySiteLonLatForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.id = 'id_apiary_site_lonlat_form'
        #self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Field('site_id', wrapper_class='col-md-4'),
                Field('longitude', wrapper_class='col-md-4'),
                Field('latitude', wrapper_class='col-md-4'),
                css_class = "row"
            ),
            Submit('submit_apiary_site_lonlat_form', 'Update'),
        )


