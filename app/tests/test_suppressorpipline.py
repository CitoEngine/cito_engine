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

from rules_engine.lib.suppressors import SuppressorPipeLine
from . import factories


class TestSuppressionPipeline(TestCase):

    def setUp(self):
        self.event = factories.EventFactory.create()
        self.incident = factories.IncidentFactory.create(event=self.event, element='foo')

    def test_eventsuppressor(self):
        """
        Test event suppression
        :return:
        """
        event_suppressor = factories.EventSuppressorFactory.create(event=self.event)
        S = SuppressorPipeLine()
        self.assertTrue(S.is_suppressed(incident=self.incident))
        self.assertTrue(S.is_event_suppressed)

    def test_element_suppressor(self):
        """
        Test element suppression
        :return:
        """
        element_suppressor = factories.ElementSuppressorFactory.create(element='foo')
        S = SuppressorPipeLine()
        self.assertTrue(S.is_suppressed(incident=self.incident))
        self.assertTrue(S.is_element_suppressed)

    def test_element_and_event_suppressor(self):
        """
        Test ElementAndEvent suppression
        :return:
        """
        e_and_e_suppressor = factories.EventAndElementSuppressorFactory(event=self.event, element='foo')
        S = SuppressorPipeLine()
        self.assertTrue(S.is_suppressed(incident=self.incident))
        self.assertTrue(S.is_element_and_event_suppressed)

    def test_is_suppressed(self):
        """
        Expect false if incident is not suppressed
        :return:
        """
        self.assertFalse(SuppressorPipeLine().is_suppressed(incident=self.incident))