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
from cito_engine.views import incidents
from cito_engine.models import Incident
from . import factories


class TestIncidentViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='hodor', password='hodor',
                                             first_name='Hodor', last_name='HodorHodor',
                                             email='hodor@hodor.hodor')
        Perms.objects.create(user=self.user, access_level=1).save()

    def login(self):
        self.client.login(username='hodor', password='hodor')

    def test_get_incident_status_all(self):
        """Get incident status summary for all incidents.
        """
        test_incidents = []
        [test_incidents.append(factories.IncidentFactory.create()) for i in range(10)]
        i = incidents.get_incident_stats()
        # Make sure we have 10 active incidents
        self.assertEquals(i['active'], 10)
        self.assertEquals(Incident.objects.filter().count(), 10)
        # Lets change the status of a few incidents
        test_incidents[0].status = 'Acknowledged'
        test_incidents[1].status = 'Acknowledged'
        test_incidents[2].status = 'Acknowledged'
        test_incidents[3].status = 'Cleared'
        test_incidents[4].status = 'Cleared'
        test_incidents[5].status = 'Cleared'
        [test_incidents[i].save() for i in range(10)]
        i = incidents.get_incident_stats()
        self.assertEquals(i['active'], 4)
        self.assertEquals(i['acknowledged'], 3)
        self.assertEquals(i['cleared'], 3)

    def test_get_incident_status_team(self):
        """Get incident status summary with team_id.
        """
        t1 = factories.TeamFactory.create()
        t2 = factories.TeamFactory.create()
        e1 = factories.EventFactory.create(team=t1)
        e2 = factories.EventFactory.create(team=t2)
        t1_incidents = []
        t2_incidents = []
        [t1_incidents.append(factories.IncidentFactory.create(event=e1)) for i in range(10)]
        [t2_incidents.append(factories.IncidentFactory.create(event=e2)) for i in range(10)]
        i = incidents.get_incident_stats()
        # Make sure we have 20 active incidents
        self.assertEquals(i['active'], 20)
        self.assertEquals(Incident.objects.filter().count(), 20)
        # Lets change the status of a few incidents by team
        t2_incidents[0].status = 'Acknowledged'
        t2_incidents[1].status = 'Acknowledged'
        t2_incidents[2].status = 'Acknowledged'
        t2_incidents[3].status = 'Cleared'
        t2_incidents[4].status = 'Cleared'
        t2_incidents[5].status = 'Cleared'
        [t2_incidents[i].save() for i in range(10)]
        i = incidents.get_incident_stats(team_id=t2.id)
        self.assertEquals(i['active'], 4, msg="Team (t2) incidents do not validate after update")
        self.assertEquals(i['acknowledged'], 3)
        self.assertEquals(i['cleared'], 3)

    def test_incident_views_without_login(self):
        """All incident views without login
        """
        i1 = factories.IncidentFactory.create()
        t1 = factories.TeamFactory.create()
        response = self.client.get('/incidents/')
        self.assertRedirects(response, '/login/?next=/incidents/')
        response = self.client.get("/incidents/view/%s/" % i1.id)
        self.assertRedirects(response, '/login/?next=/incidents/view/%s/' % i1.id)
        response = self.client.get('/incidents/view/active/')
        self.assertRedirects(response, '/login/?next=/incidents/view/active/')
        response = self.client.get('/incidents/view/1/active/')
        self.assertRedirects(response, '/login/?next=/incidents/view/1/active/')
        response = self.client.post('/incidents/toggle/')
        self.assertRedirects(response, '/login/?next=/incidents/toggle/')

    # TODO: Migrate this test to selenium
    def test_view_all_incidents(self):
        """Test view_all_incidents with login and proper perms
        """
        self.login()
        [factories.IncidentFactory.create(status='Active') for i in range(20)]
        [factories.IncidentFactory.create(status='Acknowledged') for i in range(10)]
        [factories.IncidentFactory.create(status='Cleared') for i in range(30)]
        response = self.client.get('/incidents/')
        self.assertContains(response, '<div class="dig">20</div>')
        self.assertContains(response, '<div class="dig">10</div>')
        self.assertContains(response, '<div class="dig">30</div>')

    def test_view_incidents_of_specific_status(self):
        """Test view_all_incidents with login and proper perms
        """
        self.login()
        for incident_status in ['Active', 'active', 'Acknowledged', 'acknowledged', 'Cleared', 'cleared']:
            response = self.client.get('/incidents/view/%s/' % incident_status)
            self.assertEquals(response.status_code, 200, msg="Got response %s " % response)
        # Test a wrong status code
        response = self.client.get('/incidents/view/abracadabra/')
        self.assertEquals(response.status_code, 404)

    def test_view_incidents_of_specific_status_by_team(self):
        """Testing incident views by team
        """
        t1 = factories.TeamFactory.create()
        self.login()
        for incident_status in ['Active', 'active', 'Acknowledged', 'acknowledged', 'Cleared', 'cleared']:
            response = self.client.get('/incidents/view/%d/%s/' % (t1.id, incident_status))
            self.assertEquals(response.status_code, 200, msg="Got response %s " % response)
        # Test a wrong status code
        response = self.client.get('/incidents/view/%d/abracadabra/' % t1.id)
        self.assertEquals(response.status_code, 404)

    def test_view_single_incident(self):
        """Viewing single incident
        """
        i = factories.IncidentFactory.create()
        self.login()
        response = self.client.get('/incidents/view/%d/' % i.id)
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/incidents/view/20000/')
        self.assertEquals(response.status_code, 404)

    def test_toggle_incident_status(self):
        """Toggle incident status
        """
        factory_incident = factories.IncidentFactory.create()
        self.user.team_set.add(factory_incident.event.team)
        self.login()

        # Test for a non existing status
        response = self.client.post('/incidents/toggle/', data={'incident_id': factory_incident.id,
                                                                'incident_status': 'Borked',
                                                                'redirect_to': '/incidents/'})
        self.assertRedirects(response, '/incidents/')

        model_incident = Incident.objects.get(pk=factory_incident.id)
        self.assertEquals(model_incident.status, 'Active')

        # Test acknowledged
        response = self.client.post('/incidents/toggle/', data={'incident_id': factory_incident.id,
                                                                'incident_status': 'Acknowledged',
                                                                'redirect_to': '/incidents/'})
        self.assertRedirects(response, '/incidents/')

        model_incident = Incident.objects.get(pk=factory_incident.id)
        self.assertEquals(model_incident.status, 'Acknowledged')

        # Test cleared
        response = self.client.post('/incidents/toggle/', data={'incident_id': factory_incident.id,
                                                                'incident_status': 'Cleared',
                                                                'redirect_to': '/incidents/'})
        self.assertRedirects(response, '/incidents/')

        model_incident = Incident.objects.get(pk=factory_incident.id)
        self.assertEquals(model_incident.status, 'Cleared')

        # Try toggle again after incident is cleared
        response = self.client.post('/incidents/toggle/', data={'incident_id': factory_incident.id,
                                                                'incident_status': 'Acknowledged',
                                                                'redirect_to': '/incidents/'})
        self.assertRedirects(response, '/incidents/')

        model_incident = Incident.objects.get(pk=factory_incident.id)
        self.assertEquals(model_incident.status, 'Cleared')

        # Try toggle with non-existing incident id
        response = self.client.post('/incidents/toggle/', data={'incident_id': 9999,
                                                                'incident_status': 'Acknowledged',
                                                                'redirect_to': '/incidents/'})

        self.assertEquals(response.status_code, 404)