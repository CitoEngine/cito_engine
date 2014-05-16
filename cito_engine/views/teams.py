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
from django.db.models.query_utils import Q
from cito_engine.models import Team
from cito_engine.forms import teams


@login_required(login_url='/login/')
def view_all_teams(request):
    if request.user.perms.access_level > 4:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    page_title = 'Teams'
    box_title = page_title
    try:
        teams = Team.objects.all().order_by('name')
    except Team.DoesNotExist:
        teams = None

    return render_to_response('view_teams.html', locals(), context_instance=RequestContext(request))


@login_required(login_url='/login/')
def edit_team(request, team_id):
    if request.user.perms.access_level > 2:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    page_title = 'Editing team'
    box_title = page_title
    team = get_object_or_404(Team, pk=team_id)
    if request.method == 'POST':
        form = teams.TeamForm(request.POST)
        if form.is_valid():
            team_name = form.cleaned_data.get('name')
            if Team.objects.filter(~Q(pk=team_id), name__iexact=team_name).count() > 0:
                errors = ['Team with name \"%s\" already exists.' % team_name]
            else:
                team.name = team_name
                team.description = form.cleaned_data.get('description')
                team.members = form.cleaned_data.get('members')
                team.save()
                return redirect('/teams/')
    else:
        form = teams.TeamForm(instance=team)
    return render_to_response('generic_form.html', locals(), context_instance=RequestContext(request))


@login_required(login_url='/login/')
def add_team(request):
    if request.user.perms.access_level > 1:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    page_title = 'Add a new team'
    box_title = page_title
    if request.method == 'POST':
        form = teams.TeamForm(request.POST)
        if form.is_valid():
            team_name = form.cleaned_data['name']
            if Team.objects.filter(name__iexact=team_name).count() > 0:
                errors = ['Team named \"%s\" already exists' % team_name]
            else:
                form.save()
                return redirect('/teams/')
    else:
        form = teams.TeamForm()
    return render_to_response('generic_form.html', locals(), context_instance=RequestContext(request))
