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
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from api.incident_listener import IncidentListenerAPI
from rules_engine.views import SuppressionSearchView, SuppressionAddView, RemoveSuppression
from cito_engine.views.jira import JIRAAddView
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', 'cito_engine.views.incidents.view_all_incidents'),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^events/add/$', 'cito_engine.views.events.add_event'),
                       url(r'^events/view/$', 'cito_engine.views.events.view_events'),
                       url(r'^events/$', 'cito_engine.views.events.view_events'),
                       url(r'^events/view/(?P<event_id>\d+)', 'cito_engine.views.events.view_single_event'),
                       url(r'^events/edit/(?P<event_id>\d+)', 'cito_engine.views.events.edit_event'),
                       url(r'^teams/$', 'cito_engine.views.teams.view_all_teams'),
                       url(r'^teams/add/$', 'cito_engine.views.teams.add_team'),
                       url(r'^teams/edit/(?P<team_id>\d+)', 'cito_engine.views.teams.edit_team'),
                       url(r'^categories/$', 'cito_engine.views.categories.view_all_categories'),
                       url(r'^categories/add/$', 'cito_engine.views.categories.add_category'),
                       url(r'^categories/edit/(?P<category_id>\d+)', 'cito_engine.views.categories.edit_category'),
                       url(r'^eventactions/add/(?P<event_id>\d+)', 'cito_engine.views.eventactions.add_eventaction'),
                       url(r'^eventactions/edit/(?P<eventaction_id>\d+)', 'cito_engine.views.eventactions.edit_eventaction'),
                       url(r'^pluginservers/$', 'cito_engine.views.pluginservers.view_all_pluginservers'),
                       url(r'^pluginservers/add/$', 'cito_engine.views.pluginservers.add_pluginserver'),
                       url(r'^pluginservers/view/(?P<pluginserver_id>\d+)', 'cito_engine.views.pluginservers.view_single_pluginserver'),
                       url(r'^pluginservers/edit/(?P<pluginserver_id>\d+)', 'cito_engine.views.pluginservers.edit_pluginserver'),
                       url(r'^pluginservers/refresh/(?P<pluginserver_id>\d+)', 'cito_engine.views.pluginservers.refresh_pluginserver'),
                       )

urlpatterns += patterns('',
                        url(r'^incidents/$', 'cito_engine.views.incidents.view_all_incidents'),
                        url(r'^incidents/view/(?P<incident_id>\d+)/$', 'cito_engine.views.incidents.view_single_incident'),
                        url(r'^incidents/view/(?P<incident_status>\w+)/$', 'cito_engine.views.incidents.view_all_incidents'),
                        url(r'^incidents/view/(?P<team_id>\d+)/(?P<incident_status>\w+)/$', 'cito_engine.views.incidents.view_all_incidents'),
                        url(r'^incidents/toggle/$', 'cito_engine.views.incidents.toggle_incident_status'),
                        url(r'^incidents/search/element/$', 'cito_engine.views.incidents.view_element'),
                        )


urlpatterns += patterns('',
                        url(r'^jira/add/$', JIRAAddView.as_view()),
                        )

urlpatterns += patterns('',
                        url(r'^comments/add/$', 'comments.views.add_comment'),
                        )

urlpatterns += patterns('',
                        url(r'^login/$', 'appauth.views.login_user'),
                        url(r'^logout/$', 'appauth.views.logout_user'),
                        )

urlpatterns += patterns('',
                        url(r'^users/$', 'cito_engine.views.userviews.view_all_users'),
                        url(r'^users/create/$', 'cito_engine.views.userviews.create_user'),
                        url(r'^users/toggle/$', 'cito_engine.views.userviews.toggle_user'),
                        url(r'^users/team/(?P<toggle>\w+)/$', 'cito_engine.views.userviews.modify_user_team_membership'),
                        url(r'^users/view/(?P<user_id>\d+)/$', 'cito_engine.views.userviews.view_single_user'),
                        url(r'^users/edit/(?P<user_id>\d+)/$', 'cito_engine.views.userviews.edit_user'),
                        url(r'^users/perms/update/$', 'cito_engine.views.userviews.update_user_perms'),
                        )

urlpatterns += patterns('',
                        url(r'^dashboard/$', 'cito_engine.views.dashboards.teamview'),
                        )

# #TODO: Remove addevent before releasing v1.0
urlpatterns += patterns('',
                        url(r'^addevent/$', IncidentListenerAPI.as_view()),
                        url(r'^api/v1/incidents/add/$', IncidentListenerAPI.as_view()),
                        )

urlpatterns += patterns('',
                        url(r'^suppression/view/$', SuppressionSearchView.as_view()),
                        url(r'^suppression/add/$', SuppressionAddView.as_view()),
                        url(r'^suppression/remove/$', RemoveSuppression.as_view()),
                        )

urlpatterns += patterns('',
                        url(r'^reports/$', 'reports.views.report_all_incidents'),
                        url(r'^reports/allincidents/$', 'reports.views.report_all_incidents'),
                        url(r'^reports/allevents/$', 'reports.views.report_events_in_system'),
                        url(r'^reports/topincidents/$', 'reports.views.report_incidents_per_event'),
                        url(r'^reports/mostalerted/$', 'reports.views.report_most_alerted_elements'),
                        url(r'^reports/elements/incidents/$', 'reports.views.report_incidents_per_element'),
                        )




# urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns('',
                        url(r'^content/(?P<path>.*)$', 'django.views.static.serve',
                            {'document_root': settings.STATIC_FILES}),)

urlpatterns += patterns('',
                        url(r'^tools/bulkupload/(?P<upload_item>\w+)/$', 'cito_engine.views.tools.show_bulk_upload_form'),
                        url(r'^tools/bulkupload/events/confirm/$', 'cito_engine.views.tools.bulk_upload_events'),
)
