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
from django.conf import settings
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


def get_report_all_incidents(from_date, to_date, event_id=None, team_id=None, severity=None):
    query = dict()
    if team_id is not None:
        query['team_id'] = team_id
    if event_id is not None:
        query['event_id'] = event_id
    if severity != 'All' and severity is not None:
        query['severity'] = severity

    query['day__gte'] = from_date
    query['day__lte'] = to_date

    return DailyData.objects.filter(**query)

def get_detailed_report_of_all_incidents(from_date, to_date, event_id=None, team_id=None, severity=None):
    query = dict()
    # time_range = timezone.make_aware(datetime.today() - timedelta(days=days), timezone.get_current_timezone())

    if team_id is not None:
        query['event__team__id'] = team_id
    if event_id is not None:
        query['event_id'] = event_id
    if severity != 'All' and severity is not None:
        query['severity'] = severity

    query['lastEventTime__gte'] = from_date
    query['lastEventTime__lte'] = to_date

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="citoengine_report.csv"'
    writer = csv.writer(response)

    report_header = ['severity', 'incident_id', 'event_id', 'event_summary', 'element',
                     'firstoccurence', 'lastoccurence', 'total_count', 'team', 'category',
                     'acknowledged_time', 'close_time', 'acknowledged_by', 'closed_by', 'is_suppressed']
    if settings.JIRA_ENABLED:
        report_header.append('jira_ticket')
        report_header.append('jira_creation_time')
        report_header.append('jira_created_by')

    writer.writerow(report_header)
    for i in Incident.objects.filter(**query):
        csv_row = [i.event.severity, i.id, i.event.id, i.event.summary, i.element,
                   i.firstEventTime, i.lastEventTime, i.total_incidents, i.event.team, i.event.category,
                   i.acknowledged_time, i.close_time, i.acknowledged_by, i.closed_by, i.is_suppressed]
        if settings.JIRA_ENABLED:
            # Only one jira is allowed per incident, hence we fetch only one jiraticket
            jira = i.jiratickets_set.last()
            if jira:
                csv_row.append(jira.ticket)
                csv_row.append(jira.creation_time)
                csv_row.append(jira.user.username)

        writer.writerow(csv_row)
    return response



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


def get_incidents_for_element(days, element, result_limit=10):
    """
    Fetch incidents for an element
    :param days:
    :param result_limit:
    :return:
    """
    time_range = timezone.make_aware(datetime.today() - timedelta(days=days), timezone.get_current_timezone())
    incidents = Incident.objects.filter(element__exact=element, firstEventTime__gte=time_range)[:result_limit]
    return incidents