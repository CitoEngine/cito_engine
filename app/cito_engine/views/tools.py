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

from django.shortcuts import redirect, render
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from cito_engine.forms import tools_form, events


@login_required(login_url='/login/')
def bulk_upload_events(request):
    BulkEventsFormset = formset_factory(events.EventForm, extra=0)
    render_vars = dict()
    if request.method != 'POST':
        return redirect('/incidents/')
    else:
        # If we got a bunch of lines for events
        if 'list_of_items' in request.POST:
            list_of_events = request.POST.get('list_of_items')
            severity = request.POST.get('severity')
            category = request.POST.get('category')
            team = request.POST.get('team')
            initial_data = []
            if list_of_events:
                for event_summary in list_of_events.splitlines():
                    initial_data.append({'summary': event_summary,
                                         'description': event_summary,
                                         'severity': severity,
                                         'team': team,
                                         'category': category,
                                         })
                render_vars['formset'] = BulkEventsFormset(initial=initial_data)
            else:
                render_vars['errors'] = ['List was empty!']

        # We got the formset
        elif 'form-INITIAL_FORMS' in request.POST:
            render_vars['formset'] = BulkEventsFormset(request.POST)
            user_teams = request.user.team_set.all()
            if render_vars['formset'].is_valid():
                for form in render_vars['formset']:
                    if form.cleaned_data.get('team') not in user_teams:
                        render_vars['errors'] = ['Cannot add event for %s, you are not a member of this team.' %
                                                 form.cleaned_data.get('team')]
                        return render(request, 'bulk_upload.html', render_vars)
                    else:
                        form.save()
                return redirect('/events/')
    return render(request, 'bulk_upload.html', render_vars)


@login_required(login_url='/login/')
def show_bulk_upload_form(request, upload_item):
    form = tools_form.BulkUploadForm()
    render_vars = dict()
    render_vars['form'] = form
    render_vars['box_title'] = 'Bulk add events'
    render_vars['page_title'] = 'Bulk add events'

    if upload_item == 'events':
        render_vars['form_action'] = '/tools/bulkupload/events/confirm/'
    return render(request, 'generic_form.html', render_vars)
