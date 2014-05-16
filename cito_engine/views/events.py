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

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from cito_engine.forms import events
from cito_engine.models import Event, Team, EventAction
from cito_engine.actions.event_actions import dispatcher_dry_run


@login_required(login_url='/login/')
def add_event(request):
    if request.user.perms.access_level > 3:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    page_title = 'Define new event'
    box_title = page_title

    if request.method == "POST":
        form = events.EventForm(request.POST)
        if form.is_valid():
            form_model = form.save()
            return redirect('/events/view/%s' % form_model.id)
    else:
        form = events.EventForm()
    return render_to_response('generic_form.html', locals(), context_instance=RequestContext(request))


@login_required(login_url='/login/')
def view_events(request):
    render_vars = dict()
    if request.user.perms.access_level > 4:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    render_vars['search_form'] = events.EventSearchForm()
    render_vars['page_title'] = "View Events"

    # Do search
    if request.method == 'POST':
        search_form = events.EventSearchForm(request.POST)
        if search_form.is_valid():
            query_params = dict()
            team_id = int(search_form.cleaned_data.get('team'))
            search_term = search_form.cleaned_data.get('search_term').strip()

            if search_term:
                query_params['summary__icontains'] = search_term

            if team_id > 0:
                team = Team.objects.get(pk=team_id)
                query_params['team'] = team
            render_vars['events'] = Event.objects.filter(**query_params)
            render_vars['search_term'] = search_term
            render_vars['search_form'] = search_form

    # Default page, no search
    else:
        render_vars['events'] = Event.objects.all().order_by('id')
    return render_to_response('view_all_events.html', render_vars, context_instance=RequestContext(request))


@login_required(login_url='/login/')
def view_single_event(request, event_id):
    if request.user.perms.access_level > 4:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        event_action_id = request.POST.get('event_action_id')
        event_action = get_object_or_404(EventAction, pk=event_action_id)
        dry_run_response = dispatcher_dry_run(event, event_action)

    page_title = "Viewing EventID: %s" % event.id
    try:
        eventActions = EventAction.objects.filter(event=event)
    except EventAction.DoesNotExist:
        eventActions = None
    return render_to_response('view_event.html', locals(), context_instance=RequestContext(request))


@login_required(login_url='/login/')
def edit_event(request, event_id):
    if request.user.perms.access_level > 3:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    page_title = 'Editing Event'
    box_title = 'Editing Event'
    event = get_object_or_404(Event,pk=event_id)
    if request.method == 'POST':
        form = events.EventForm(request.POST)
        if form.is_valid():
            query = dict(summary=form.cleaned_data['summary'],
                         description=form.cleaned_data['description'],
                         team=form.cleaned_data['team'],
                         severity=form.cleaned_data['severity'],
                         category=form.cleaned_data['category'],
                         status=form.cleaned_data['status'])
            Event.objects.filter(pk=event_id).update(**query)
            return redirect('/events/view/%s' % event_id)
    else:
        form = events.EventForm(instance=event)
    return render_to_response('generic_form.html', locals(), context_instance=RequestContext(request))



