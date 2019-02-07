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
from mock import patch, call
from django.test import TestCase
from cito_engine.models import Incident, IncidentLog, EventActionCounter
from cito_engine.poller.event_poller import EventPoller
from . import factories


class TestEventActions(TestCase):
    """
    X = 2, Y=100

     Case 1
     * One incident in T secs
     * 2nd at T+10, 3rd at T+11, 4th at T+51
     * Assert we have 1 single incident, 4 logs and event action executed once

     * 5th incident occurs at T+101
     * Assert counters are reset
     * 6th incident occurs at T+151
     * Assert event action is executed for the second time

    """
    def setUp(self):
        self.event = factories.EventFactory.create()

    @patch('cito_engine.actions.incidents.requests')
    def test__single_event_action_execution(self, mock_requests):
        self.eventaction = factories.EventActionFactory.create(event=self.event,threshold_count=2, threshold_timer=100)
        T = int(time())
        raw_incident = '{ "event": {"eventid":"%s", "element":"foo", "message":"omgwtfbbq"}, "timestamp": %d}' % (self.event.id, T)

        eventpoller = EventPoller()
        self.assertTrue(eventpoller.parse_message(raw_incident))
        incident = Incident.objects.filter()[0]
        eacounter = EventActionCounter.objects.get(incident=incident)
        self.assertFalse(eacounter.is_triggered)

        # 2nd incident
        raw_incident = '{ "event": {"eventid":"%s", "element":"foo", "message":"omgwtfbbq"}, "timestamp": %d}' % (
            self.event.id, T+10)
        self.assertTrue(eventpoller.parse_message(raw_incident))

        eacounter = EventActionCounter.objects.get(incident=incident)
        self.assertTrue(eacounter.is_triggered)

        #3rd incident
        raw_incident = '{ "event": {"eventid":"%s", "element":"foo", "message":"omgwtfbbq"}, "timestamp": %d}' % (
            self.event.id, T + 11)
        self.assertTrue(eventpoller.parse_message(raw_incident))
        eacounter = EventActionCounter.objects.get(incident=incident)
        self.assertTrue(eacounter.is_triggered)

        # 4th incident
        raw_incident = '{ "event": {"eventid":"%s", "element":"foo", "message":"omgwtfbbq"}, "timestamp": %d}' % (
            self.event.id, T + 51)
        self.assertTrue(eventpoller.parse_message(raw_incident))
        eacounter = EventActionCounter.objects.get(incident=incident)
        self.assertTrue(eacounter.is_triggered)

        #We should have one incident and 4 incident logs
        self.assertEqual(Incident.objects.count(), 1)
        self.assertEqual(IncidentLog.objects.count(), 4)

        # Assert we only execute plugin once
        self.assertEqual(mock_requests.post.call_count, 1)

        # 5th incident after time window
        raw_incident = '{ "event": {"eventid":"%s", "element":"foo", "message":"omgwtfbbq"}, "timestamp": %d}' % (
            self.event.id, T + 101)
        self.assertTrue(eventpoller.parse_message(raw_incident))
        eacounter = EventActionCounter.objects.get(incident=incident)
        self.assertFalse(eacounter.is_triggered)
        # Assert we did not execute plugin yet
        self.assertEqual(mock_requests.post.call_count, 1)

        # 6th incident after time window
        raw_incident = '{ "event": {"eventid":"%s", "element":"foo", "message":"omgwtfbbq"}, "timestamp": %d}' % (
            self.event.id, T + 121)
        self.assertTrue(eventpoller.parse_message(raw_incident))
        eacounter = EventActionCounter.objects.get(incident=incident)
        self.assertTrue(eacounter.is_triggered)
        # Assert event action occurred for the second time
        self.assertEqual(mock_requests.post.call_count, 2)


        #todo create tests to check use cases mentioned in the comments

    """
    X = 1, Y=100

     Case 2
     * Two incidents in T secs
     * 3rd at T+10, 4th in T+51
     * Assert we have 1 single incident, 4 logs and event action executed once

     * Two incidents in T+121 secs
     * Assert counters are reset
     * 5th incident occurs at T+121
     * Assert event action is executed for the second time
     * 6th incident occurs at T+121
     * Assert event action is not executed 

    """
    @patch('cito_engine.actions.incidents.requests')
    def test__single_threshold_event_action_execution(self, mock_requests):
        self.eventaction = factories.EventActionFactory.create(event=self.event,threshold_count=1, threshold_timer=100)
        T = int(time())
        raw_incident = '{ "event": {"eventid":"%s", "element":"foo", "message":"omgwtfbbq"}, "timestamp": %d}' % (self.event.id, T)

        eventpoller = EventPoller()
        self.assertTrue(eventpoller.parse_message(raw_incident))
        incident = Incident.objects.filter()[0]
        eacounter = EventActionCounter.objects.get(incident=incident)
        self.assertTrue(eacounter.is_triggered)
        # Assert we executed plugin 
        self.assertEqual(mock_requests.post.call_count, 1)

        # 2nd incident
        raw_incident = '{ "event": {"eventid":"%s", "element":"foo", "message":"omgwtfbbq"}, "timestamp": %d}' % (
            self.event.id, T)
        self.assertTrue(eventpoller.parse_message(raw_incident))

        eacounter = EventActionCounter.objects.get(incident=incident)
        self.assertTrue(eacounter.is_triggered)
        # Assert we did not executed plugin again
        self.assertEqual(mock_requests.post.call_count, 1)

        #3rd incident
        raw_incident = '{ "event": {"eventid":"%s", "element":"foo", "message":"omgwtfbbq"}, "timestamp": %d}' % (
            self.event.id, T + 10)
        self.assertTrue(eventpoller.parse_message(raw_incident))
        eacounter = EventActionCounter.objects.get(incident=incident)
        self.assertTrue(eacounter.is_triggered)

        # 4th incident
        raw_incident = '{ "event": {"eventid":"%s", "element":"foo", "message":"omgwtfbbq"}, "timestamp": %d}' % (
            self.event.id, T + 51)
        self.assertTrue(eventpoller.parse_message(raw_incident))
        eacounter = EventActionCounter.objects.get(incident=incident)
        self.assertTrue(eacounter.is_triggered)

        #We should have one incident and 4 incident logs
        self.assertEqual(Incident.objects.count(), 1)
        self.assertEqual(IncidentLog.objects.count(), 4)

        # Assert we only execute plugin once
        self.assertEqual(mock_requests.post.call_count, 1)

        # 5th incident after time window
        raw_incident = '{ "event": {"eventid":"%s", "element":"foo", "message":"omgwtfbbq"}, "timestamp": %d}' % (
            self.event.id, T + 121)
        self.assertTrue(eventpoller.parse_message(raw_incident))
        eacounter = EventActionCounter.objects.get(incident=incident)
        self.assertTrue(eacounter.is_triggered)
        # Assert event action occurred for the second time
        self.assertEqual(mock_requests.post.call_count, 2)

        # 6th incident after time window
        raw_incident = '{ "event": {"eventid":"%s", "element":"foo", "message":"omgwtfbbq"}, "timestamp": %d}' % (
            self.event.id, T + 121)
        self.assertTrue(eventpoller.parse_message(raw_incident))
        eacounter = EventActionCounter.objects.get(incident=incident)
        self.assertTrue(eacounter.is_triggered)
        # Assert event action occurred for the second time
        self.assertEqual(mock_requests.post.call_count, 2)
