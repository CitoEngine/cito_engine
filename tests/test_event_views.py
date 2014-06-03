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

from django.test import TestCase, Client
from django.contrib.auth.models import User
from appauth.models import Perms
from mock import patch, call, Mock
from requests.exceptions import ConnectionError
from . import factories


class TestEventViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='hodor', password='hodor',
                                             first_name='Hodor', last_name='HodorHodor',
                                             email='hodor@hodor.hodor')
        Perms.objects.create(user=self.user, access_level=1).save()
        self.event = factories.EventFactory()
        self.event_url = '/events/view/%s' % self.event.id
        self.team = factories.TeamFactory.create()
        self.category = factories.CategoryFactory()
        self.team1 = factories.TeamFactory.create(name='Team1')
        self.event1 = factories.EventFactory(summary='Event1', team=self.team1)
        self.team2 = factories.TeamFactory.create(name='Team2')
        self.event2 = factories.EventFactory(summary='Event2', team=self.team2)
        self.team3 = factories.TeamFactory.create(name='Team3')
        self.event3 = factories.EventFactory(summary='Event3', team=self.team3)

    def login(self):
        self.client.login(username='hodor', password='hodor')

    def test_event_views_without_login(self):
        """
        Test event views without login
        """
        # Add
        response = self.client.get('/events/add/')
        self.assertRedirects(response, '/login/?next=/events/add/')

        # View all
        response = self.client.get('/events/view/')
        self.assertRedirects(response, '/login/?next=/events/view/')

        # View single
        response = self.client.get(self.event_url)
        self.assertRedirects(response, '/login/?next=%s' % self.event_url)

        # Edit
        response = self.client.get('/events/edit/%s' % self.event.id)
        self.assertRedirects(response, '/login/?next=/events/edit/%s' % self.event.id)

    def test_add_event(self):
        """
        Add an event
        """
        Perms.objects.filter(user=self.user).update(access_level=2)
        self.login()
        data = {'summary': 'Hodor',
                'description': 'HodorHodor',
                'severity': 'S3',
                'team': self.team.id,
                'category': self.category.id,
                'status': True,
                }
        response = self.client.post('/events/add/', data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'HodorHodor')

    def test_view_an_event(self):
        """
        View a single event
        """
        Perms.objects.filter(user=self.user).update(access_level=3)
        self.login()
        response = self.client.get(self.event_url)
        self.assertContains(response, 'A_Team')

    def test_event_search(self):
        """
        Search event
        """
        # TODO: Figure out why 'team': self.team1.id does not work
        data = {'team': 0, 'search_term': 'event1'}
        self.login()
        response = self.client.post('/events/view/', data)
        self.assertContains(response, 'Event1')
        self.assertNotContains(response, 'Event2')
        self.assertNotContains(response, 'Event3')
        # Query 2
        data = {'team': 0, 'search_term': 'vent2'}
        self.login()
        response = self.client.post('/events/view/', data)
        self.assertContains(response, 'Event2')
        self.assertNotContains(response, 'Event1')
        self.assertNotContains(response, 'Event3')
        # Query 3
        data = {'team': 0, 'search_term': 'eve'}
        self.login()
        response = self.client.post('/events/view/', data)
        self.assertContains(response, 'Event2')
        self.assertContains(response, 'Event1')
        self.assertContains(response, 'Event3')

    def test_view_single_event(self):
        """
        View a single event
        """
        # Add a couple of eventactions
        factories.EventActionFactory(event=self.event1, pluginParameters='eventaction1_param')
        factories.EventActionFactory(event=self.event, pluginParameters='eventaction2_param')
        self.login()

        # Check event 1 with an eventaction
        response = self.client.get('/events/view/%s' % self.event1)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Event1')
        self.assertContains(response, 'eventaction1_param')

        # Check event 2 with an eventaction
        response = self.client.get('/events/view/%s' % self.event)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'A factory made event!')
        self.assertContains(response, 'eventaction2_param')
        self.assertNotContains(response, 'Event1')

    @patch('cito_engine.actions.event_actions.requests')
    def test_view_single_event_exec_dry_run(self, mock_requests):
        """
        Executes dry_run for eventaction in view_single_event
        """
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.text = 'OK:Computer'
        self.login()
        event_action_param = '{"__EVENTID__", "__INCIDENTID__", "__ELEMENT__", "__MESSAGE__"}'
        event_action = factories.EventActionFactory(event=self.event, pluginParameters=event_action_param)
        response = self.client.post('/events/view/%d' % self.event.id, data={'event_id': self.event.id,
                                                                             'event_action_id': event_action.id})
        expected_json_string = '{"plugin": "%s", "parameters": ' \
                               '{"%s", "test_incident_id", "test_element_name", "test_message"}}' \
                               % (event_action.plugin.name, self.event.id)

        self.assertEquals(mock_requests.post.call_args_list,
                          [call(u'%s' % event_action.plugin.server.url+'/runplugin',
                                verify=event_action.plugin.server.ssl_verify,
                                data=u'%s' % expected_json_string
                                )]
                          )

    # Test a failure scenario
    @patch('cito_engine.actions.event_actions.requests')
    def test_view_single_event_dry_run_with_failure(self, mock_requests):
        """
        Executes dry_run and expects a failure
        """
        mock_requests.post = Mock(side_effect=ConnectionError)
        self.login()
        event_action_param = '{"__EVENTID__", "__INCIDENTID__", "__ELEMENT__", "__MESSAGE__"}'
        event_action = factories.EventActionFactory(event=self.event, pluginParameters=event_action_param)
        response = self.client.post('/events/view/%d' % self.event.id, data={'event_id': self.event.id,
                                                                             'event_action_id': event_action.id})
        self.assertContains(response, 'Error executing Plugin:')

    def test_edit_event(self):
        """
        Edit an event
        """
        data = dict(summary='HodorSummary',
                    description='HodorDescription',
                    team=factories.TeamFactory.create(name='HodorTeam').id,
                    severity='S0',
                    category=factories.CategoryFactory(categoryType='HodorCategory').id,
                    status=True)
        self.login()
        postresponse = self.client.post('/events/edit/%s' % self.event.id, data, follow=True)
        self.assertEqual(postresponse.status_code, 200)
        self.assertContains(postresponse, '<td>HodorSummary</td>')
        self.assertContains(postresponse, '<td>HodorDescription</td>')
        self.assertContains(postresponse, '<td>HodorTeam</td>')
        self.assertContains(postresponse, '<td>S0</td>')
        self.assertContains(postresponse, '<td>HodorCategory</td>')
        self.assertContains(postresponse, 'Enabled</span>')