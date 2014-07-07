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

import csv
from datetime import datetime, timedelta
from django.db.models import Count, Sum
from django.utils import timezone
from django.http import HttpResponse
from cito_engine.models import Team, Event, Incident, IncidentLog

from reports.models import DailyData, HourlyData


def update_reports(incident):
    base_values = {'event_id': incident.event.id,
                   'team_id': incident.event.team.id,
                   'severity': incident.event.severity,
                   'category': incident.event.category.categoryType,
    }
    hourly_report_values = base_values.copy()
    hourly_report_values['hour'] = incident.lastEventTime.replace(minute=0, second=0, microsecond=0)
    daily_report_value = base_values.copy()
    daily_report_value['day'] = incident.lastEventTime.date()

    hourly_data, create = HourlyData.objects.get_or_create(**hourly_report_values)
    hourly_data.total_incidents += 1
    hourly_data.save()

    daily_data, create = DailyData.objects.get_or_create(**daily_report_value)
    daily_data.total_incidents += 1
    daily_data.save()


def get_report_all_incidents(days, event_id=None, team_id=None, severity=None):
    query = dict()
    time_range = timezone.make_aware(datetime.today() - timedelta(days=days), timezone.get_current_timezone())
    if team_id:
        query['team_id'] = team_id
    if event_id:
        query['event_id'] = event_id
    if severity != 'All':
        query['severity'] = severity
    if days == 1:
        query['hour__gte'] = time_range
        return HourlyData.objects.filter(**query)
    else:
        query['day__gte'] = time_range
        return DailyData.objects.filter(**query)


def get_report_json_formatter(data, dimension):
    response = dict()
    for record in data:
        timestamp = getattr(record, dimension)
        timestamp = int(datetime.strftime(timestamp, "%s")) * 1000
        try:
            response[timestamp] += int(record.total_incidents)
        except KeyError:
            response[timestamp] = int(record.total_incidents)
    return response


def get_report_csv_formatter(data, dimension, filename='cito_report.csv'):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    writer = csv.writer(response)
    if data:
        writer.writerow([unicode(fieldname) for fieldname in data[0]._meta.get_all_field_names()])
    for record in data:
        writer.writerow([unicode(getattr(record, field)) for field in record._meta.get_all_field_names()])
    return response


def get_events_in_system():
    result = []
    for team in Team.objects.all().values('id', 'name'):
        for event in Event.objects.all().values('team').annotate(count=Count('id')):
            if team['id'] == event['team']:
                result.append({'team_name': team['name'],
                               'team_id': team['id'],
                               'count': event['count'],
                })
    return result


def get_incidents_per_event(days, event_id=None, team_id=None, result_limit=10):
    # TODO: Add range limit
    result = []
    query_params = dict()
    time_range = timezone.make_aware(datetime.today() - timedelta(days=days), timezone.get_current_timezone())
    if team_id:
        team = Team.objects.filter(pk=team_id).values('id', 'name')
        query_params['team_id'] = team_id
    if event_id:
        query_params['event_id'] = event_id
    query_params['day__gte'] = time_range
    for event in DailyData.objects.values('event_id', 'team_id').filter(**query_params).annotate(
            total_count=Sum('total_incidents')).order_by('-total_count')[:result_limit]:
        try:
            result.append({'team_id': event['team_id'],
                           'event_id': event['event_id'],
                           'total_count': event['total_count'],
            })
        except:
            print "Error querying for %s" % '__name__'

    return result


def get_most_alerted_elements(days, result_limit=10):
    """
    Get most alerted elements
    :param days:
    :param result_limit:
    :return:
    """
    time_range = timezone.make_aware(datetime.today() - timedelta(days=days), timezone.get_current_timezone())
    elements_by_unique_incidents = Incident.objects.values('element'). \
                                       filter(firstEventTime__gte=time_range). \
                                       annotate(uniq_count=Count('id'), total_count=Sum('total_incidents')). \
                                       order_by('-uniq_count')[:result_limit]
    return elements_by_unique_incidents