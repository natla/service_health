from django import forms
from django.forms import ModelForm

from service_outages.models import ServiceOutageRecord


class AddServiceRecordForm(ModelForm):
    """Class for adding a new service record to the API"""

    class Meta:
        model = ServiceOutageRecord
        # end_time is automatically calculated
        exclude = ('end_time',)

    def __init__(self, *args, **kwargs):
        """Customize the form fields"""

        super().__init__(*args, **kwargs)
        self.fields['service_id'].label = 'Service ID'
        self.fields['duration'].label = 'Service Outage Duration'
        self.fields['start_time'].label = 'Service Outage Start Datetime'

        # Enforce numbers starting from 1 on the client side
        self.fields['service_id'].widget = forms.NumberInput(attrs={'min': '1'})
        self.fields['duration'].widget = forms.NumberInput(attrs={'min': '1'})

        # Enforce datetime formatting
        self.fields['start_time'].widget = forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S')

        # Reset the initial values - we don't want to display in the form
        # the default values that were set for the model, they would confuse the user
        self.fields['service_id'].initial = ''
        self.fields['duration'].initial = ''
        self.fields['start_time'].initial = ''
