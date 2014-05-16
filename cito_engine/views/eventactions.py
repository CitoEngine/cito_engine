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

from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.utils import timezone
from cito_engine.forms import eventactions
from cito_engine.models import EventAction, Event
import simplejson

@login_required(login_url='/login/')
def edit_eventaction(request, eventaction_id):
    if request.user.perms.access_level > 3:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    page_title = 'Add event action'
    box_title = page_title
    eventaction = get_object_or_404(EventAction, pk=eventaction_id)
    include_eventaction_param_js = True
    if request.method == 'POST':
        form = eventactions.EventActionForm(request.POST)
        if form.is_valid():
            query = dict(event=form.cleaned_data['event'],
                         plugin=form.cleaned_data['plugin'],
                         pluginParameters=form.cleaned_data['pluginParameters'],
                         isEnabled=form.cleaned_data['isEnabled'],
                         threshold_count=form.cleaned_data['threshold_count'],
                         threshold_timer=form.cleaned_data['threshold_timer'],
                         dateUpdated=timezone.now(),
                         )
            EventAction.objects.filter(pk=eventaction_id).update(**query)
            return redirect('/events/view/%s' % eventaction.event.id)
        #Form is invalid, send the plugin params
        else:
            try:
                json_data = simplejson.loads(form.cleaned_data['pluginParameters'])
            except simplejson.JSONDecodeError:
                pass
    else:
        form = eventactions.EventActionForm(instance=eventaction)
        try:
            json_data = simplejson.loads(eventaction.pluginParameters)
        except simplejson.JSONDecodeError:
            pass
    return render_to_response('eventaction_form.html', locals(), context_instance=RequestContext(request))


@login_required(login_url='/login/')
def add_eventaction(request, event_id):
    if request.user.perms.access_level > 3:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    page_title = 'Add event action for EventID: %s' % event_id
    box_title = page_title
    event = get_object_or_404(Event, pk=event_id)
    include_eventaction_param_js = True
    if request.method == 'POST':
        form = eventactions.EventActionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/events/view/%s' % event.id)
        else:
            errors = form.errors
    else:
        form = eventactions.EventActionForm(initial={'event': event_id})
    return render_to_response('eventaction_form.html', locals(), context_instance=RequestContext(request))
