"""Copyright 2014 Cyrus Dasadia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from django import forms
from cito_engine.models import Incident


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        exclude = ['close_time']


class IncidentToggleForm(forms.Form):
    incident_id = forms.IntegerField()
    incident_status = forms.CharField(max_length=15)
    redirect_to = forms.CharField()


class ElementSearchForm(forms.Form):
    search_term = forms.CharField(max_length=255, required=True, label='Element name')

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        # change a widget attribute:
        self.fields['search_term'].widget.attrs["placeholder"] = 'Element Name'

class BulkToggleIncidentForm(forms.Form):
    STATUS_CHOICES = (
        ('Acknowledged', 'Acknowledged'),
        ('Cleared', 'Cleared')
    )
    incidents = forms.CharField()
    toggle_status = forms.ChoiceField(choices=STATUS_CHOICES)
