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

from rules_engine.models import ElementSuppressor, EventAndElementSuppressor, EventSuppressor
from audit.auditlog import incidentauditlog


class SuppressorPipeLine(object):

    def __init__(self):
        self._incident = None
        self.msg = None

    @property
    def is_event_suppressed(self):
        try:
            event_sup = EventSuppressor.objects.get(event=self._incident.event)
        except EventSuppressor.DoesNotExist:
            return False
        if event_sup.start_time and event_sup.end_time:
            if event_sup.start_time < self._incident.lastEventTime < event_sup.end_time:
                self.msg = 'Event Suppressed %s < %s < %s ' % (event_sup.start_time, self._incident.lastEventTime, event_sup.end_time)
                return True
            return False
        self.msg = 'Incident matches event suppression rule'
        return True

    @property
    def is_element_suppressed(self):
        try:
            event_sup = ElementSuppressor.objects.get(element=self._incident.element)
        except ElementSuppressor.DoesNotExist:
            return False
        if event_sup.start_time and event_sup.end_time:
            if event_sup.start_time < self._incident.lastEventTime < event_sup.end_time:
                self.msg = 'Element Suppressed %s < %s < %s ' % (
                    event_sup.start_time, self._incident.lastEventTime, event_sup.end_time)
                return True
            return False
        self.msg = 'Incident matches element suppression rule'
        return True

    @property
    def is_element_and_event_suppressed(self):
        try:
            event_sup = EventAndElementSuppressor.objects.get(event=self._incident.event,
                                                              element=self._incident.element)
        except EventAndElementSuppressor.DoesNotExist:
            return False
        if event_sup.start_time and event_sup.end_time:
            if event_sup.start_time < self._incident.lastEventTime < event_sup.end_time:
                self.msg = 'Event and Element Suppressed %s < %s < %s ' % (
                    event_sup.start_time, self._incident.lastEventTime, event_sup.end_time)
                return True
            return False
        self.msg = 'Incident matches event and element suppression rule'
        return True

    def is_suppressed(self, incident):
        if incident is None:
            raise ValueError('SuppressorPipeLine called with an empty incident')

        self._incident = incident

        if self.is_event_suppressed or self.is_element_suppressed or self.is_element_and_event_suppressed:
            incidentauditlog(message=self.msg, incident=self._incident, level='DEBUG')
            return True
        else:
            return False
