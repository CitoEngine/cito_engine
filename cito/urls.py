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

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from cito_engine.api import IncidentResource
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', 'cito_engine.views.incidents.view_all_incidents'),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^api/', include(IncidentResource().urls)),
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

urlpatterns += patterns('',
                        url(r'^reports/$', 'reports.views.report_all_incidents'),
                        url(r'^reports/allincidents/$', 'reports.views.report_all_incidents'),
                        url(r'^reports/allevents/$', 'reports.views.report_events_in_system'),
                        url(r'^reports/topincidents/$', 'reports.views.report_incidents_per_event'),
                        )

# urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns('',
                        url(r'^content/(?P<path>.*)$', 'django.views.static.serve',
                            {'document_root': settings.STATIC_FILES}),)

urlpatterns += patterns('',
                        url(r'^tools/bulkupload/(?P<upload_item>\w+)/$', 'cito_engine.views.tools.show_bulk_upload_form'),
                        url(r'^tools/bulkupload/events/confirm/$', 'cito_engine.views.tools.bulk_upload_events'),
)