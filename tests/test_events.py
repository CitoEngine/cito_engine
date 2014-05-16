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

from time import time
from datetime import datetime
from django.utils.timezone import utc
from django.test import TestCase
from cito_engine.models import *
from cito_engine.actions.incidents import add_incident
from . import factories


class TeamTestCase(TestCase):
    def setUp(self):
        self.team = factories.TeamFactory()

    def test_team_name(self):
        self.assertEquals(self.team.name, 'The_A_Team')


class EventTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        self.team = factories.TeamFactory(name='TheATeam',description='The awesome A-TestTeam')
        self.category = factories.CategoryFactory(categoryType='TestCategoryType')
        self.event = factories.EventFactory(summary='TestEventSummary', description='TestEventDescription',
                                            team=self.team, category=self.category)
        self.incident_time1 = time()
        self.incident_time2 = self.incident_time1 + 10
        self.incident_time3 = self.incident_time2 + 10

        self.incident = add_incident({'eventid': self.event.id, 'element': 'host.cito.com',
                                      'message': 'host is down'}, self.incident_time1)

    def test_event_creation(self):
        self.event = Event.objects.get(id=self.event.id)
        self.assertEqual(self.event.team, self.team)
        self.assertEqual(self.event.category, self.category)
        self.assertEqual(self.event.summary, 'TestEventSummary')
        self.assertEqual(self.event.description, 'TestEventDescription')

    def test_add_incident(self):
        incident = Incident.objects.get(pk=self.incident.id)
        self.assertIsNotNone(incident)
        self.assertEquals(self.incident.id, incident.id)

    def test_incident_timestamps(self):
        # check timestamp
        t1 = datetime.fromtimestamp(float(self.incident_time1), tz=utc)
        t2 = datetime.fromtimestamp(float(self.incident_time2), tz=utc)

        incident = add_incident({'eventid': self.event.id, 'element': 'host.cito.com',
                                 'message': 'host is down'}, self.incident_time2)

        self.assertEquals((self.incident.firstEventTime-t1).seconds, 0)

        self.assertEquals((incident.lastEventTime - incident.firstEventTime).seconds, 10,
                          msg='LastEventTime:%s-FirsEventTime%s is not 10' %
                              (self.incident.lastEventTime, self.incident.firstEventTime))

        self.assertEquals((incident.lastEventTime-t1).seconds,10)

    def test_incident_counts(self):
        incident = add_incident({'eventid': self.event.id, 'element': 'host.cito.com',
                                 'message': 'host is down'}, self.incident_time1)
        # Check counts
        self.assertEqual(Incident.objects.all().count(), 1)
        self.assertEquals(incident.total_incidents, 2)
        self.assertEqual(IncidentLog.objects.all().count(), 2)

    def test_acknowledged_incident(self):
        incident = add_incident({'eventid': self.event.id, 'element': 'host.cito.com',
                                 'message': 'host is down'}, self.incident_time1)
        incident.status = 'Acknowledged'
        incident.save()
        incident2 = add_incident({'eventid': self.event.id, 'element': 'host.cito.com',
                                 'message': 'host is down'}, self.incident_time1)
        self.assertEquals(incident.id, incident2.id,
                          msg='Acknowledged incident was not appended, new incident created instead.')

    def test_cleared_incident(self):
        incident = add_incident({'eventid': self.event.id, 'element': 'host.c.com',
                                 'message': 'host is down'}, self.incident_time1)
        incident.status = 'Cleared'
        incident.save()
        incident2 = add_incident({'eventid': self.event.id, 'element': 'host.c.com',
                                 'message': 'host is down'}, self.incident_time1)
        self.assertGreater(incident2.id, incident.id,
                          msg='New incident was not created upon closing a previous one.')

