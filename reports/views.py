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

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from cito_engine.models import Team, Event
from . import actions
from .forms import AllIncidentsReportForm, EventsPerTeam, MostAlertedElements, IncidentsPerElement

@login_required(login_url='/login/')
def report_all_incidents(request):
    js_list = ['flot/jquery.flot.min.js',
               'flot/jquery.flot.time.min.js',
    ]
    css_list = None
    form = AllIncidentsReportForm()
    render_vars = {'js_list': js_list,
                   'css_list': css_list,
                   'include_view_reports_js': True,
                   'form': form,
    }

    if request.method == 'POST':
        form = AllIncidentsReportForm(request.POST)
        if form.is_valid():
            result = dict()
            query_params = dict()
            query_params['team_id'] = None
            team_id = int(form.cleaned_data.get('team'))
            timerange = int(form.cleaned_data.get('timerange'))
            query_params['severity'] = form.cleaned_data.get('severity')

            if team_id > 0:
                team = get_object_or_404(Team, pk=team_id)
                query_params['team_id'] = team_id
                render_vars['series_label'] = team.name
            else:
                render_vars['series_label'] = 'All teams'

            if timerange == 1:
                dimension = 'hour'
            else:
                dimension = 'day'
            result = actions.get_report_all_incidents(timerange, **query_params)
            if form.cleaned_data.get('csv_export'):
                return actions.get_report_csv_formatter(result, dimension)
            render_vars['json_data'] = actions.get_report_json_formatter(result, dimension)
            render_vars['page_title'] = 'Incidents for %s ' % render_vars['series_label']
            if query_params['severity'] == 'All':
                render_vars['page_title'] += ' with any severity.'
            else:
                render_vars['page_title'] += ' with %s severity.' % query_params['severity']
        else:
            raise ValueError

    else:
        render_vars['page_title'] = 'Select one or more options to generate the report.'
        render_vars['nothing_selected'] = True
    return render_to_response('reports_all_incidents.html', render_vars, context_instance=RequestContext(request))


@login_required(login_url='/login/')
def report_events_in_system(request):
    render_vars = dict()
    js_list = ['flot/jquery.flot.min.js',
               'flot/jquery.flot.time.min.js',
               'flot/jquery.flot.pie.js']
    css_list = None
    if request.method == 'GET':
        render_vars = {
            'events': actions.get_events_in_system(),
            'page_title': 'Total number of events defined in the system',
            'include_view_pie': True,
            'js_list': js_list,
            'css_list': css_list,
        }

    return render_to_response('reports_events_in_system.html', render_vars,
                              context_instance=RequestContext(request))


@login_required(login_url='/login/')
def report_incidents_per_event(request):
    render_vars = dict()
    render_vars['form'] = EventsPerTeam()
    render_vars['page_title'] = 'Top events codes based on incidents.'
    if request.method == 'POST':
        render_vars['js_list'] = ['flot/jquery.flot.min.js',
                                  'flot/jquery.flot.time.min.js',
                                  'flot/jquery.flot.pie.js']
        render_vars['css_list'] = None
        render_vars['include_view_pie'] = True,
        form = EventsPerTeam(request.POST)
        render_vars['form'] = form
        if form.is_valid():
            query_params = dict()
            team_id = int(form.cleaned_data.get('team'))
            event_id = form.cleaned_data.get('event_id')
            query_params['result_limit'] = int(form.cleaned_data.get('result_limit'))
            query_params['days'] = int(form.cleaned_data.get('timerange'))
            if team_id > 0:
                team = get_object_or_404(Team, pk=team_id)
                query_params['team_id'] = team_id
                render_vars['series_label'] = team.name
            else:
                render_vars['series_label'] = 'All teams'

            if event_id:
                query_params['event_id'] = int(event_id)

            render_vars['incidents'] = actions.get_incidents_per_event(**query_params)

            #get event sumary
            for i in render_vars['incidents']:
                e = Event.objects.get(pk=i['event_id'])
                i.update(summary=e.summary, team_name=e.team.name)

    else:
        render_vars['nothing_selected'] = True
    return render_to_response('reports_incidents_per_event.html', render_vars,
                              context_instance=RequestContext(request))

@login_required(login_url='/login/')
def report_most_alerted_elements(request):
    render_vars = dict()
    render_vars['form'] = MostAlertedElements()
    render_vars['page_title'] = 'Most alerted elements'
    if request.method == 'POST':
        form = MostAlertedElements(request.POST)
        render_vars['form'] = form
        if form.is_valid():
            days = int(form.cleaned_data.get('timerange'))
            result_limit = form.cleaned_data.get('result_limit')
            render_vars['elements_by_incidents'] = actions.get_most_alerted_elements(days, result_limit)
    return render_to_response('reports_most_alerted_elements.html', render_vars,
                              context_instance=RequestContext(request))


def report_incidents_per_element(request):
    render_vars = dict()
    render_vars['page_title'] = 'Incidents per Element / Hostname'
    render_vars['form'] = IncidentsPerElement()
    if request.method == 'POST':
        form = IncidentsPerElement(request.POST)
        render_vars['form'] = form
        if form.is_valid():
            days = int(form.cleaned_data.get('timerange'))
            result_limit = form.cleaned_data.get('result_limit')
            element = form.cleaned_data.get('element')
            render_vars['element'] = element
            render_vars['days'] = days
            render_vars['incidents'] = actions.get_incidents_for_element(days=days,
                                                                         element=element,
                                                                         result_limit=result_limit)
    return render_to_response('reports_incidents_per_element.html',
                              render_vars, context_instance=RequestContext(request))
