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

    @property
    def is_event_suppressed(self):
        return EventSuppressor.objects.filter(event=self._incident.event).exists()

    @property
    def is_element_suppressed(self):
        return ElementSuppressor.objects.filter(element=self._incident.element).exists()

    @property
    def is_element_and_event_suppressed(self):
        return EventAndElementSuppressor.objects.filter(event=self._incident.event,
                                                        element=self._incident.element).exists()

    def is_suppressed(self, incident):
        if incident is None:
            raise ValueError('SuppressorPipeLine called with an empty incident')

        self._incident = incident

        if self.is_event_suppressed:
            incidentauditlog(message='Incident matches event suppression rule', incident=self._incident)
            return True
        elif self.is_element_suppressed:
            incidentauditlog(message='Incident matches element suppression rule', incident=self._incident)
            return True
        elif self.is_element_and_event_suppressed:
            incidentauditlog(message='Incident matches event and element suppression rule', incident=self._incident)
            return True
        else:
            return False