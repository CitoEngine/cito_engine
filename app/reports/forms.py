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

from django.forms import Form, ChoiceField, IntegerField, BooleanField, CharField
from datetime import datetime
from cito_engine.models import Team


class AllIncidentsReportForm(Form):

    status_choices = (
        (u'All', u'All'),
        (u'Active', u'Active'),
        (u'Acknowledged', u'Acknowledged'),
        (u'Cleared', u'Cleared')
    )
    event_severity = (
        (u'All', u'All'),
        (u'S0', u'S0'),
        (u'S1', u'S1'),
        (u'S2', u'S2'),
        (u'S3', u'S3'),
    )

    team = ChoiceField(label="Team")
    from_date = CharField(label="From")
    to_date = CharField(label="To")
    severity = ChoiceField(choices=event_severity, label='Severity')
    csv_export = BooleanField(label="Export as CSV", required=False)

    def __init__(self, *args, **kwargs):
        super(AllIncidentsReportForm, self).__init__(*args, **kwargs)
        self.team_list = [(0, u'All')]
        for team in Team.objects.all():
            self.team_list.append((team.id, team.name))
        self.fields['team'].choices = self.team_list

    def clean(self):
        cleaned_data = super(AllIncidentsReportForm, self).clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')
        try:
            datetime.strptime(from_date, '%Y-%m-%d')
        except Exception as e:
            self._errors["from_date"] = self.error_class(['Invalid date'])

        try:
            datetime.strptime(to_date, '%Y-%m-%d')
        except Exception as e:
            self._errors["to_date"] = self.error_class(['Invalid date'])

        return cleaned_data


class EventsPerTeam(Form):

    time_choices = (
        ('1', 'Last 24hours'),
        ('7', 'Last week'),
        ('30', '4 weeks'),
    )
    result_limit_choices = (
        ('10', '10'),
        ('25', '25'),
        ('50', '50'),
        ('100', '100'),
    )

    team = ChoiceField(label="Team")
    timerange = ChoiceField(choices=time_choices, label="Range")
    event_id = IntegerField(required=False, min_value=1, label="Event ID")
    result_limit = ChoiceField(choices=result_limit_choices, label="Results")

    def __init__(self, *args, **kwargs):
        super(EventsPerTeam, self).__init__(*args, **kwargs)
        # change a widget attribute:
        self.fields['event_id'].widget.attrs["placeholder"] = 'Search by EventID or leave blank'
        self.team_list = [(0, u'All')]
        for team in Team.objects.all():
            self.team_list.append((team.id, team.name))
        self.fields['team'].choices = self.team_list



class MostAlertedElements(Form):
    time_choices = (
        ('1', 'Last 24hours'),
        ('7', 'Last week'),
        ('30', '4 weeks'),
    )
    result_limit_choices = (
        ('10', '10'),
        ('25', '25'),
        ('50', '50'),
        ('100', '100'),
    )

    timerange = ChoiceField(choices=time_choices, label="Range")
    result_limit = ChoiceField(choices=result_limit_choices, label="Results")


class IncidentsPerElement(Form):
    time_choices = (
        ('1', 'Last 24hours'),
        ('7', 'Last week'),
        ('30', '4 weeks'),
    )
    result_limit_choices = (
        ('10', '10'),
        ('25', '25'),
        ('50', '50'),
        ('100', '100'),
    )

    timerange = ChoiceField(choices=time_choices, label="Range (days)")
    result_limit = ChoiceField(choices=result_limit_choices, label="Results")
    element = CharField(label="Element/Hostname")