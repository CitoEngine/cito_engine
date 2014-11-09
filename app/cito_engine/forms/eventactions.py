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

from django.forms import ModelForm, HiddenInput, ValidationError
from cito_engine.models import EventAction


class EventActionForm(ModelForm):
    class Meta:
        model = EventAction
        widgets = {'event': HiddenInput}

    def clean_threshold_count(self):
        threshold_count = self.cleaned_data['threshold_count']
        if threshold_count <= 0:
            raise ValidationError(u"Threshold count cannot be less than zero, that's blasphemy!")
        else:
            return threshold_count

    def clean_threshold_timer(self):
        threshold_timer = self.cleaned_data['threshold_timer']
        if threshold_timer <= 0:
            raise ValidationError(u"Threshold timer cannot be less than zero, that's blasphemy!")
        else:
            return threshold_timer
