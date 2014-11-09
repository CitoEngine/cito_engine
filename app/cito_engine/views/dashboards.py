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
from django.template import RequestContext
from django.shortcuts import render_to_response
from cito_engine.models import Incident, Team

@login_required(login_url='/login/')
def teamview(request):
    team_dashboard = dict()
    try:
        teams = Team.objects.all()
    except Team.DoesNotExist:
        teams = None

    for team in teams:
        team_dashboard[team.name] = dict(active=0, acknowledged=0, name=team.name, team_id=team.id)

    try:
        open_incidents = Incident.objects.filter(status='Active')
    except Incident.DoesNotExist:
        open_incidents = None

    try:
        acked_incidents = Incident.objects.filter(status='Acknowledged')
    except Incident.DoesNotExist:
        acked_incidents = None

    for i in open_incidents:
        team_dashboard[i.event.team.name]['active'] += 1

    for i in acked_incidents:
        team_dashboard[i.event.team.name]['acknowledged'] += 1

    return render_to_response('dashboard_team_views.html',
                              {'team_dashboard': team_dashboard,
                               'auto_refresh_page': True},
                              context_instance=RequestContext(request))
