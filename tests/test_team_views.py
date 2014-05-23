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
from cito_engine.models import Team
from . import factories


class TestTeamViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='hodor', password='hodor',
                                             first_name='Hodor', last_name='HodorHodor',
                                             email='hodor@hodor.hodor')
        Perms.objects.create(user=self.user, access_level=1).save()

    def login(self):
        self.client.login(username='hodor', password='hodor')

    def test_incident_views_without_login(self):
        """All team views without login
        """
        for view in ['/', '/add/', '/edit/1/']:
            response = self.client.get('/teams%s' % view)
            self.assertRedirects(response, '/login/?next=/teams%s' % view, msg_prefix='Error for view:%s' % view )

    def test_view_all_teams(self):
        """View all teams"""
        t1 = factories.TeamFactory.create(name='PlanetExpress')
        t2 = factories.TeamFactory.create(name='Marklars')
        self.login()
        response = self.client.get('/teams/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'PlanetExpress')
        self.assertContains(response, 'Marklars')

    def test_edit_team_view(self):
        """Testing edit team view"""
        t1 = factories.TeamFactory.create(name='PlanetExpress')
        self.login()
        # Test a wrong team id
        response = self.client.get('/teams/edit/999999/')
        self.assertEquals(response.status_code, 404)
        # Edit a right team
        data = dict(name='Marklars', description='Super Edited Team', members=[self.user.id])
        response = self.client.post('/teams/edit/%d/' % t1.id, data=data, follow=True)
        self.assertRedirects(response, '/teams/')
        team = Team.objects.get(pk=t1.id)
        self.assertEquals(team.name, 'Marklars')
        self.assertEquals(team.description, 'Super Edited Team')
        # Check that user got added to this team
        self.assertEquals(self.user.team_set.get(id=t1.id), team)

        t2 = factories.TeamFactory.create(name='PlanetExpress')
        # Make sure we do not update name to existing team
        data = dict(name='PlanetExpress', description='Super Edited Team', members=[self.user.id])
        response = self.client.post('/teams/edit/%d/' % t1.id, data=data, follow=True)
        self.assertContains(response, 'Team with name &quot;%s&quot; already exists.' % t2.name)

    def test_add_team_view(self):
        """Testing add_team view"""
        t1 = factories.TeamFactory.create(name='PlanetExpress')
        self.login()

        # Try adding a team with existing name
        data = dict(name='PlanetExpress', description='Super Edited Team', members=[self.user.id])
        response = self.client.post('/teams/add/', data=data, follow=True)
        self.assertContains(response, 'Team with name &quot;%s&quot; already exists.' % t1.name)

        # Try a legit team
        data = dict(name='Omicronians', description='Super Edited Team', members=[self.user.id])
        response = self.client.post('/teams/add/', data=data, follow=True)
        self.assertRedirects(response, '/teams/')
        team = Team.objects.get(name='Omicronians')
        self.assertEquals(team.description, 'Super Edited Team')
        # Check that user got added to this team
        self.assertIsNotNone(self.user.team_set.get(id=team.id))


