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
from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import timezone
from rules_engine.lib.suppressors import SuppressorPipeLine
from . import factories


class TestSuppressionPipeline(TestCase):

    def setUp(self):
        self.event = factories.EventFactory.create()
        self.incident = factories.IncidentFactory.create(event=self.event, element='foo')

    def test_event_suppressor(self):
        """
        Test event suppression
        :return:
        """
        event_suppressor = factories.EventSuppressorFactory.create(event=self.event)
        S = SuppressorPipeLine()
        self.assertTrue(S.is_suppressed(incident=self.incident))
        self.assertTrue(S.is_event_suppressed)

    def test_event_suppressor_with_time_limits(self):
        """
        Test event suppression with time constraints
        :return:
        """

        now = timezone.now()
        hour_ago = now + timedelta(hours=-1)
        two_hours_ago = now+timedelta(hours=-1)
        hour_ahead = now + timedelta(hours=1)
        two_hours_ahead = now + timedelta(hours=2)

        # with proper time constraints
        e1 = factories.EventFactory.create()
        i1 = factories.IncidentFactory.create(event=e1, element='e1foo')
        factories.EventSuppressorFactory.create(event=e1, start_time=hour_ago, end_time=hour_ahead)
        S = SuppressorPipeLine()
        self.assertTrue(S.is_suppressed(incident=i1))
        self.assertTrue(S.is_event_suppressed)
        # expired time constraints
        e2 = factories.EventFactory.create()
        i2 = factories.IncidentFactory.create(event=e2, element='e2foo')
        factories.EventSuppressorFactory.create(event=e2, start_time=two_hours_ago, end_time=hour_ago)
        S = SuppressorPipeLine()
        self.assertFalse(S.is_suppressed(incident=i2))
        self.assertFalse(S.is_event_suppressed)
        # with time constraints in future
        e3 = factories.EventFactory.create()
        i3 = factories.IncidentFactory.create(event=e3, element='e3foo')
        factories.EventSuppressorFactory.create(event=e3, start_time=hour_ahead, end_time=two_hours_ahead)
        S = SuppressorPipeLine()
        self.assertFalse(S.is_suppressed(incident=i3))
        self.assertFalse(S.is_event_suppressed)


    def test_element_suppressor(self):
        """
        Test element suppression
        :return:
        """
        element_suppressor = factories.ElementSuppressorFactory.create(element='foo')
        S = SuppressorPipeLine()
        self.assertTrue(S.is_suppressed(incident=self.incident))
        self.assertTrue(S.is_element_suppressed)

    def test_element_suppressor_with_time_limits(self):
        """
        Test element suppression with time constraints
        :return:
        """

        now = timezone.now()
        hour_ago = now + timedelta(hours=-1)
        two_hours_ago = now + timedelta(hours=-1)
        hour_ahead = now + timedelta(hours=1)
        two_hours_ahead = now + timedelta(hours=2)

        # with proper time constraints
        e1 = factories.EventFactory.create()
        i1 = factories.IncidentFactory.create(event=e1, element='e1foo')
        factories.ElementSuppressorFactory.create(element='e1foo', start_time=hour_ago, end_time=hour_ahead)
        S = SuppressorPipeLine()
        self.assertTrue(S.is_suppressed(incident=i1))
        self.assertTrue(S.is_element_suppressed)
        # expired time constraints
        e2 = factories.EventFactory.create()
        i2 = factories.IncidentFactory.create(event=e2, element='e2foo')
        factories.ElementSuppressorFactory.create(element='e2foo', start_time=two_hours_ago, end_time=hour_ago)
        S = SuppressorPipeLine()
        self.assertFalse(S.is_suppressed(incident=i2))
        self.assertFalse(S.is_element_suppressed)
        # with time constraints in future
        e3 = factories.EventFactory.create()
        i3 = factories.IncidentFactory.create(event=e3, element='e3foo')
        factories.ElementSuppressorFactory.create(element='e3foo', start_time=hour_ahead, end_time=two_hours_ahead)
        S = SuppressorPipeLine()
        self.assertFalse(S.is_suppressed(incident=i3))
        self.assertFalse(S.is_element_suppressed)

    def test_element_and_event_suppressor(self):
        """
        Test ElementAndEvent suppression
        :return:
        """
        e_and_e_suppressor = factories.EventAndElementSuppressorFactory(event=self.event, element='foo')
        S = SuppressorPipeLine()
        self.assertTrue(S.is_suppressed(incident=self.incident))
        self.assertTrue(S.is_element_and_event_suppressed)

    def test_element_and_event_suppressor_with_time_limits(self):
        """
        Test event and element suppression with time constraints
        :return:
        """

        now = timezone.now()
        hour_ago = now + timedelta(hours=-1)
        two_hours_ago = now + timedelta(hours=-1)
        hour_ahead = now + timedelta(hours=1)
        two_hours_ahead = now + timedelta(hours=2)

        # with proper time constraints
        e1 = factories.EventFactory.create()
        i1 = factories.IncidentFactory.create(event=e1, element='e1foo')
        factories.EventAndElementSuppressorFactory.create(event=e1, element='e1foo', start_time=hour_ago, end_time=hour_ahead)
        S = SuppressorPipeLine()
        self.assertTrue(S.is_suppressed(incident=i1))
        self.assertTrue(S.is_element_and_event_suppressed)
        # expired time constraints
        e2 = factories.EventFactory.create()
        i2 = factories.IncidentFactory.create(event=e2, element='e2foo')
        factories.EventAndElementSuppressorFactory.create(event=e2, element='e2foo', start_time=two_hours_ago, end_time=hour_ago)
        S = SuppressorPipeLine()
        self.assertFalse(S.is_suppressed(incident=i2))
        self.assertFalse(S.is_element_and_event_suppressed)
        # with time constraints in future
        e3 = factories.EventFactory.create()
        i3 = factories.IncidentFactory.create(event=e3, element='e3foo')
        factories.EventAndElementSuppressorFactory.create(event=e3, element='e3foo', start_time=hour_ahead, end_time=two_hours_ahead)
        S = SuppressorPipeLine()
        self.assertFalse(S.is_suppressed(incident=i3))
        self.assertFalse(S.is_element_and_event_suppressed)

    def test_is_suppressed(self):
        """
        Expect false if incident is not suppressed
        :return:
        """
        self.assertFalse(SuppressorPipeLine().is_suppressed(incident=self.incident))