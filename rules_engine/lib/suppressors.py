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