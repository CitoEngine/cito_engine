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

from django.test import TestCase
from reports.models import HourlyData, DailyData
from reports import actions
from . import factories


class TestTeamViews(TestCase):
    def setUp(self):
        pass

    def test_get_report_all_incidents(self):
        """
        Reports on all incidents based on Hourly and Daily data
        """
        event1 = factories.EventFactory.create()
        days = 1
        for i in range(3):
            test_incident = factories.IncidentFactory.create(event=event1)
            test_incident.lastEventTime = test_incident.firstEventTime
            test_incident.save()
            actions.update_reports(test_incident)
        response = actions.get_report_all_incidents(days=days)[0]
        self.assertIsInstance(response, HourlyData)
        self.assertEqual(response.event_id, event1.id)
        self.assertEqual(response.team_id, event1.team_id)
        self.assertEqual(response.severity, event1.severity)
        self.assertEqual(response.category, event1.category.categoryType)
        self.assertEqual(response.total_incidents, 3)

        #note test with additional params
        days = 2
        response = actions.get_report_all_incidents(days=days,
                                                    event_id=event1.id,
                                                    team_id=event1.team.id,
                                                    severity=event1.severity)[0]
        self.assertIsInstance(response, DailyData)
        self.assertEqual(response.event_id, event1.id)
        self.assertEqual(response.team_id, event1.team_id)
        self.assertEqual(response.severity, event1.severity)
        self.assertEqual(response.category, event1.category.categoryType)
        self.assertEqual(response.total_incidents, 3)

    def test_get_events_in_system(self):
        """
        Get all events from the system
        """
        foo = factories.TeamFactory.create(name='foo')
        bar = factories.TeamFactory.create(name='bar')
        baz = factories.TeamFactory.create(name='baz')
        [factories.EventFactory.create(team=team) for e in range(5)
                                                  for team in [foo, bar, baz]]
        result = actions.get_events_in_system()
        self.assertEqual(len(result), 3)
        for i in range(3):
            rec = result[i]
            self.assertEqual(rec['count'], 5)
            self.assertIn(rec['team_name'], ['foo', 'bar', 'baz'])

    def test_get_incidents_per_event(self):
        """
        Test incidents per event and team
        """
        event1 = factories.EventFactory.create()
        total_incidents = 15
        for i in range(total_incidents):
            test_incident = factories.IncidentFactory.create(event=event1)
            test_incident.lastEventTime = test_incident.firstEventTime
            test_incident.save()
            actions.update_reports(test_incident)
        response = actions.get_incidents_per_event(days=1,
                                                   event_id=event1.id,
                                                   team_id=event1.team.id)
        self.assertEqual(response[0]['event_id'], event1.id)
        self.assertEqual(response[0]['team_id'], event1.team.id)
        self.assertEqual(response[0]['total_count'], total_incidents)

    def test_get_most_alerted_elements(self):
        """
        Test report for most alerted elements
        """
        event1 = factories.EventFactory.create()
        [factories.IncidentFactory.create(event=event1, element='host.foo.com') for x in range(5)]
        [factories.IncidentFactory.create(event=event1, element='host.baz.com') for x in range(6)]
        [factories.IncidentFactory.create(event=event1, element='host.bar.com') for x in range(7)]
        response = actions.get_most_alerted_elements(days=1,result_limit=1)
        # print response
        self.assertEqual(response[0]['element'], 'host.bar.com')
        self.assertEqual(response[0]['total_count'], 0)
        self.assertEqual(response[0]['uniq_count'], 7)