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
from __future__ import absolute_import
from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.views.static import serve
from api.incident_listener import IncidentListenerAPI
from rules_engine.views import SuppressionSearchView, SuppressionAddView, RemoveSuppression
from cito_engine.views.jira import JIRAAddView, JIRAUpdateView, JIRABulkUpdateView
from cito_engine.views.incidents import BulkToggleIncidents
import cito_engine.views
import cito_engine.views.categories
import cito_engine.views.dashboards
import cito_engine.views.eventactions
import cito_engine.views.events
import cito_engine.views.incidents
import cito_engine.views.pluginservers
import cito_engine.views.teams
import cito_engine.views.tools
import cito_engine.views.userviews
import comments.views
import appauth.views
import reports.views
admin.autodiscover()

urlpatterns = [
    url(r'^$', cito_engine.views.incidents.view_all_incidents, name='view_all_incidents'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^events/add/$', cito_engine.views.events.add_event, name='events_add_event'),
    url(r'^events/view/$', cito_engine.views.events.view_events, name='events_view_events'),
    url(r'^events/$', cito_engine.views.events.view_events, name='events_view_events_root'),
    url(r'^events/view/(?P<event_id>\d+)', cito_engine.views.events.view_single_event, name='events_view_single_event'),
    url(r'^events/edit/(?P<event_id>\d+)', cito_engine.views.events.edit_event, name='events_edit_event'),
    # Teams
    url(r'^teams/$', cito_engine.views.teams.view_all_teams, name='teams_view_all_teams'),
    url(r'^teams/add/$', cito_engine.views.teams.add_team, name='teams_add_team'),
    url(r'^teams/edit/(?P<team_id>\d+)', cito_engine.views.teams.edit_team, name='teams_edit_team'),
    # Categories
    url(r'^categories/$', cito_engine.views.categories.view_all_categories, name='categories_view_all'),
    url(r'^categories/add/$', cito_engine.views.categories.add_category, name='categories_add'),
    url(r'^categories/edit/(?P<category_id>\d+)', cito_engine.views.categories.edit_category, name='categories_edit'),
    # Event actions
    url(r'^eventactions/add/(?P<event_id>\d+)', cito_engine.views.eventactions.add_eventaction, name=''),
    url(r'^eventactions/edit/(?P<eventaction_id>\d+)', cito_engine.views.eventactions.edit_eventaction, name=''),
    # Pluginserver
    url(r'^pluginservers/$', cito_engine.views.pluginservers.view_all_pluginservers, name='pluginserver_view_all'),
    url(r'^pluginservers/add/$', cito_engine.views.pluginservers.add_pluginserver, name='pluginserver_add_server'),
    url(r'^pluginservers/view/(?P<pluginserver_id>\d+)', cito_engine.views.pluginservers.view_single_pluginserver, name='pluginserver_view'),
    url(r'^pluginservers/edit/(?P<pluginserver_id>\d+)', cito_engine.views.pluginservers.edit_pluginserver, name='pluginserver_edit'),
    url(r'^pluginservers/refresh/(?P<pluginserver_id>\d+)', cito_engine.views.pluginservers.refresh_pluginserver,
        name='pluginserver_refresh'),
    # Incidents
    url(r'^incidents/$', cito_engine.views.incidents.view_all_incidents, name='incidents_view_all'),
    url(r'^incidents/view/(?P<incident_id>\d+)/$', cito_engine.views.incidents.view_single_incident, name='incidents_view'),
    url(r'^incidents/view/(?P<incident_status>\w+)/$', cito_engine.views.incidents.view_all_incidents, name='incidents_view_all'),
    url(r'^incidents/view/(?P<team_id>\d+)/(?P<incident_status>\w+)/$',
        cito_engine.views.incidents.view_all_incidents, name='incidents_view_by_team'),
    url(r'^incidents/toggle/$', cito_engine.views.incidents.toggle_incident_status, name='incidents_toggle'),
    url(r'^incidents/search/element/$', cito_engine.views.incidents.view_element, name='incidents_search_by_element'),
    # JIRA
    url(r'^jira/add/$', JIRAAddView.as_view()),
    url(r'^jira/update/$', JIRAUpdateView.as_view()),
    # Comments
    url(r'^comments/add/$', comments.views.add_comment, name='comments_add'),
    # Auth
    url(r'^login/$', appauth.views.login_user, name='login'),
    url(r'^logout/$', appauth.views.logout_user, name='logout'),
    # User and Team management
    url(r'^users/$', cito_engine.views.userviews.view_all_users, name='users_view_all'),
    url(r'^users/create/$', cito_engine.views.userviews.create_user, name='users_create'),
    url(r'^users/toggle/$', cito_engine.views.userviews.toggle_user, name='users_toggle'),
    url(r'^users/team/(?P<toggle>\w+)/$', cito_engine.views.userviews.modify_user_team_membership, name='users_team_toggle'),
    url(r'^users/view/(?P<user_id>\d+)/$', cito_engine.views.userviews.view_single_user, name='users_view_single'),
    url(r'^users/edit/(?P<user_id>\d+)/$', cito_engine.views.userviews.edit_user, name='users_edit'),
    url(r'^users/perms/update/$', cito_engine.views.userviews.update_user_perms, name='users_update_perms'),
    # Dashboard
    url(r'^dashboard/$', cito_engine.views.dashboards.teamview, name='dashboard_teamview'),
    # TODO: Remove after 1.10
    url(r'^addevent/$', IncidentListenerAPI.as_view()),
    url(r'^api/v1/incidents/add/$', IncidentListenerAPI.as_view()),
    # Suppression
    url(r'^suppression/view/$', SuppressionSearchView.as_view()),
    url(r'^suppression/add/$', SuppressionAddView.as_view()),
    url(r'^suppression/remove/$', RemoveSuppression.as_view()),
    # Reports
    url(r'^reports/$', reports.views.report_all_incidents, name='report_all'),
    url(r'^reports/allincidents/$', reports.views.report_all_incidents, name='report_all_incident'),
    url(r'^reports/allevents/$', reports.views.report_events_in_system, name='report_all_events'),
    url(r'^reports/topincidents/$', reports.views.report_incidents_per_event, name='report_incidents_per_event'),
    url(r'^reports/mostalerted/$', reports.views.report_most_alerted_elements, name='report_most_alerted_elements'),
    url(r'^reports/elements/incidents/$', reports.views.report_incidents_per_element, name='report_incident_per_element'),
    # Bulk toggles
    url(r'^bulk/toggle/$', BulkToggleIncidents.as_view()),
    url(r'^bulk/jira_update/$', JIRABulkUpdateView.as_view()),
    # Bulk upload
    url(r'^tools/bulkupload/(?P<upload_item>\w+)/$', cito_engine.views.tools.show_bulk_upload_form, name='bulk_upload_items'),
    url(r'^tools/bulkupload/events/confirm/$', cito_engine.views.tools.bulk_upload_events, name='bulk-enevts_confirm'),
    # Static
    url(r'^content/(?P<path>.*)$', serve, {'document_root': settings.STATIC_FILES}),

]