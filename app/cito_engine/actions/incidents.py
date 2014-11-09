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

from datetime import datetime
import logging

from django.utils import timezone
from django.db.models import Q
import requests

from cito_engine.models import Event, EventAction, EventActionCounter, EventActionLog, Incident, IncidentLog
from reports.actions import update_reports
from rules_engine.lib.suppressors import SuppressorPipeLine
from audit.auditlog import incidentauditlog
from . import json_formatter
from .event_actions import update_eventaction_counters


class ProcessIncident(object):
    def __init__(self, incident, message):
        self.incident = incident
        self.incident_message = message
        self.logger = logging.getLogger('poller_logger')
        self.begin()

    def begin(self):
        """
        If incident is suppressed, do nothing.
        Else execute EventActions
        """

        # Log if incident is already suppressed
        if self.incident.is_suppressed:
            incidentauditlog(incident=self.incident, message='IncidentID:%s is suppressed' % self.incident.id)

        # Check suppression pipeline
        elif SuppressorPipeLine().is_suppressed(incident=self.incident):
            self.incident.suppressed()
            incidentauditlog(incident=self.incident, message='IncidentID:%s found in suppression pipline, it is now suppressed.' % self.incident.id)

        # Process incident normally
        else:
            for event_action in EventAction.objects.filter(event=self.incident.event, isEnabled=True):
                if self.check_incident_threshold(event_action):
                    self.execute_plugin(event_action)

    def check_incident_threshold(self, event_action):
        """
        Check if an incident has met its threshold so we can dispatch an action
        """
        event_action_counter, create = EventActionCounter.objects.get_or_create(incident=self.incident,
                                                                                event_action=event_action)
        return event_action_counter.is_action_required

    def execute_plugin(self, event_action):
        """
        Fires a relevant action based on cito_engine.models.EventAction settings
        """
        self.logger.info('Firing incident for [%s] [%s] [%s] [%s]' % (self.incident.id, self.incident.event.id,
                                                                      self.incident.element, event_action.plugin))
        # If the plugin is not enabled, lets move on.
        if not event_action.plugin.status:
            return

        incident_info = self.incident.incidentInfo
        plugin_json = json_formatter.create_json_parameters(event_action, self.incident, self.incident_message)

        try:
            response = requests.post(event_action.plugin.server.url+'/runplugin', data=plugin_json,
                                     verify=event_action.plugin.server.ssl_verify)
            EventActionLog.objects.create(eventAction=event_action, text=response.text, incident=self.incident)
        except Exception as e:
            event_action_error = "Error executing Plugin:%s: ErrMsg:%s" % (event_action.plugin.name, e)
            EventActionLog.objects.create(eventAction=event_action, text=event_action_error, incident=self.incident)
            self.logger.error(event_action_error)
        finally:
            return


def add_incident(e, timestamp):
    """
    Adds an incident sent by cito_engine.poller
    """
    incident_time_diff = 0
    create = False
    logger = logging.getLogger('poller_logger')
    try:
        event_id = int(e['eventid'])
        element = e['element']
        msg = e['message']
    except Exception as excep:
        logger.error('Bad Incident:[%s], reason:[%s] message will be ignored.' % (excep, e))
        return

    # Ignore incident if any field is empty
    if not event_id or not element or not msg:
        logger.error('Bad Incident:[%s], reason:one or more fields are empty' % e)
        return

    # Ignore incident if event does not exist
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return
    #TODO: SQL sanity checks
    #TODO: Msg len check??

    incident_time = timezone.make_aware(datetime.fromtimestamp(float(timestamp)), timezone.get_default_timezone())
    logger.debug('Incident Time: %s' % incident_time)
    try:
        i = Incident.objects.get(~Q(status__iexact='Cleared'), event=event, element=element)
    except Incident.MultipleObjectsReturned:
        # If there are multiple open incidents for same eventID and element
        # we close them.
        logger.error('Multiple open objects found for %s ' % element)
        close_duplicate_incidents(event, element)
        return
    except Incident.DoesNotExist:
        create = True
        i = Incident.objects.create(event=event, element=element)

    # Update threshold timer and count
    last_incident_time = incident_time

    # Update timer only if record exists
    if create:
        i.firstEventTime = incident_time
        i.lastEventTime = incident_time
    else:
        logger.debug('Incident exists, updating IncidentLastEventTime time: %s' % i.lastEventTime)

        # If SQS sent message on time, we make timediff and
        # update the eventaction timer else ignore
        if i.lastEventTime < last_incident_time:
            incident_time_diff = (last_incident_time - i.lastEventTime).seconds
            i.lastEventTime = last_incident_time
        else:
            logger.warn("Got an incident late")

    # Update counters
    i.increment_count()
    update_eventaction_counters(i, incident_time_diff)

    # Add incident to log
    add_incident_log(i, msg, incident_time)

    # Update reports
    try:
        update_reports(i)
    except Exception as e:
        logger.error("Unable to save reports: %s" % unicode(e))
        logger.error("Incident details: %s" % unicode(i.event.id))

    # Return the newly added incident
    return i


def add_incident_log(incident, msg, incident_time):
    logger = logging.getLogger('poller_logger')
    try:
        IncidentLog.objects.create(incident=incident, msg=msg, timestamp=incident_time).save()
    except Exception as e:
        logger.error('Could not add incident log: %s' % e)


def close_duplicate_incidents(event, element):
    """
    Closes all duplicate 'Active' incidents.
    """
    logger = logging.getLogger('poller_logger')
    try:
        incidents = Incident.objects.filter(event=event, element__iexact=element, status='Active')
        #TODO: Keep the last active incident open and close others
        for i in incidents:
            logger.warning('closing duplicate incident:%s ' % i.id)
            i.status = 'Cleared'
            i.save()
    except Exception:
        logger.error('Could not close multiple incidents on event:%s, element:%s' % (event.id, element))

    return
