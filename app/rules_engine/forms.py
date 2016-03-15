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
from cito_engine.models import Event
from .models import ElementSuppressor, EventSuppressor, EventAndElementSuppressor


class SuppressionSearchForm(forms.Form):
    eventid = forms.IntegerField(required=False, label='Event ID')
    element = forms.CharField(max_length=255, required=False, label='Element')

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        # change a widget attribute:
        self.fields['eventid'].widget.attrs['placeholder'] = 'EventID or leave blank'
        self.fields['element'].widget.attrs['placeholder'] = 'Element or leave blank'


class SuppressionAddForm(forms.Form):
    """
    Form to add suppression for single Event, Element or both
    """
    SUPP_CHOICES = ((1, 'EventID'),
                    (2, 'Element'),
                    (3, 'Event and Element'),)

    # eventid = forms.CharField(max_length=12, label='Event ID')
    eventid = forms.IntegerField(label='EventID', min_value=1, required=False)
    element = forms.CharField(max_length=255, label='Element', required=False)
    suppression_type = forms.ChoiceField(choices=SUPP_CHOICES)
    start_date = forms.DateTimeField(required=False, input_formats=['%Y-%m-%d %H:%M'])
    end_date = forms.DateTimeField(required=False, input_formats=['%Y-%m-%d %H:%M'])

    def __init__(self, *args, **kwargs):
        self.event = None
        super(SuppressionAddForm, self).__init__(*args, **kwargs)

    def is_event_valid(self, eventid):
        """
        True if event exists
        :param eventid:
        :return:
        """
        try:
            self.event = Event.objects.get(pk=eventid)
        except Event.DoesNotExist:
            return False
        return True

    def clean(self):
        cleaned_data = super(SuppressionAddForm, self).clean()
        eventid = cleaned_data.get('eventid')
        element = cleaned_data.get('element').strip()
        suppression_type = cleaned_data.get('suppression_type')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date is None and end_date is not None:
            self._errors['end_date'] = self.error_class([u'End date cannot be specified without a start date'])
        if end_date is None and start_date is not None:
            self._errors['start_date'] = self.error_class([u'Start date cannot be specified without an end date'])

        if start_date > end_date:
            self._errors['end_date'] = self.error_class([u'End date cannot be greater than start date'])

        if eventid is None and (element is None or element is u''):
            msg = u'At least one field has to be entered'
            self._errors['eventid'] = self.error_class([msg])
            self._errors['element'] = self.error_class([msg])
            return cleaned_data

        if suppression_type == '1':
            if not self.is_event_valid(eventid):
                self._errors['eventid'] = self.error_class([u'EventID does not exist'])

            elif EventSuppressor.objects.filter(event__pk=eventid).exists():
                self._errors['eventid'] = self.error_class([u'This EventID is already suppressed.'])

        if suppression_type == '2':
            if ElementSuppressor.objects.filter(element=element).exists():
                self._errors['element'] = self.error_class([u'This Element is already suppressed.'])

        if suppression_type == '3':
            if not self.is_event_valid(eventid):
                self._errors['eventid'] = self.error_class([u'EventID does not exist'])
                return cleaned_data
            elif EventAndElementSuppressor.objects.filter(event__pk=eventid, element=element).exists():
                msg = u'This EventID and Element combination are already suppressed.'
                self._errors['eventid'] = self.error_class([msg])
                self._errors['element'] = self.error_class([msg])

        return cleaned_data

    def save(self, user):
        cleaned_data = self.clean()
        # Add Event Suppression
        if cleaned_data.get('suppression_type') == '1':
            EventSuppressor.objects.create(event=self.event, suppressed_by=user,
                                           start_time=cleaned_data.get('start_date'),
                                           end_time=cleaned_data.get('end_date'))

        # Add Element Suppression
        elif cleaned_data.get('suppression_type') == '2':
            ElementSuppressor.objects.create(element=cleaned_data.get('element'), suppressed_by=user,
                                             start_time=cleaned_data.get('start_date'),
                                             end_time=cleaned_data.get('end_date'))

        # Add Event and Element suppression
        elif cleaned_data.get('suppression_type') == '3':
            EventAndElementSuppressor.objects.create(event=self.event,
                                                     element=cleaned_data.get('element'),
                                                     suppressed_by=user,
                                                     start_time=cleaned_data.get('start_date'),
                                                     end_time=cleaned_data.get('end_date'))
        else:
            raise ValueError('Invalid suppression_type received by SuppressionAddForm')
