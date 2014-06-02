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

from django.forms import ModelForm, Form, ChoiceField, CharField, BooleanField
from cito_engine.models import Event, Team


class EventForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['rows'] = "5"

    class Meta:
        model = Event


class EventSearchForm(Form):
    team_list = [(0, u'All')]
    [team_list.append((t.id, t.name)) for t in Team.objects.all()]
    team = ChoiceField(choices=team_list, label="Team")
    search_term = CharField(max_length=64, required=False, label="Summary")
    csv_export = BooleanField(label="Export as CSV", required=False)

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        # change a widget attribute:
        self.fields['search_term'].widget.attrs["placeholder"] = 'Search event summary'