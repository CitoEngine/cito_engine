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

import logging
import re
import requests
import simplejson
from twisted.internet import task, reactor, threads
from django.core.cache import cache
from django.conf.settings import DISPATCHER_CONFIG
from cito_engine.models import Incident, EventAction, EventActionLog, EventActionCounter


class Dispatch:

    def __init__(self):
        self.LOCK_EXPIRE = DISPATCHER_CONFIG['lock_expire']
        self.POLLING_INTERVAL = DISPATCHER_CONFIG['interval']
        self.logger = logging.getLogger('main')


    def check_incident_threshold(self, incident, event_action):
        """
        Check if an incident has met its threshold so we can dispatch an action
        """
        event_action_counter, create = EventActionCounter.objects.get_or_create(incident=incident,
                                                                                event_action=event_action)
        return event_action_counter.check_threshold()


    def check_open_incidents(self):
        job_name = 'check_open_incidents'
        acquire_lock = lambda: cache.add(job_name, "true", self.LOCK_EXPIRE)
        release_lock = lambda: cache.delete(job_name)

        self.logger.info('#' * 10)
        self.logger.info('%s: Fetching incidents' % self.check_open_incidents)
        if acquire_lock():
            try:
                self.logger.info("Checking for open incidents")
                # We will not dispatch any actions for any incident status other than 'Active'
                for incident in Incident.objects.filter(status='Active'):
                    self.logger.debug('IncidentID:%s EventID:%s Element:%s' % (incident.id, incident.event.id, incident.element))
                    for event_action in EventAction.objects.filter(event=incident.event, isEnabled=True):
                        if self.check_incident_threshold(incident, event_action):
                            threads.deferToThread(self.dispatcher, incident, event_action)
                self.logger.info("Done checking")
            finally:
                self.logger.info("Releasing lock")
                release_lock()
        else:
            self.logger.error("Job is already running.")

    #TODO: Make sure this is non-blocking
    def dispatcher(self, incident, event_action):
        """
        Fires a relevant action based on cito_engine.models.EventAction settings
        """
        self.logger.info('Firing incident for [%s] [%s] [%s] [%s]' % (incident.id, incident.event.id,
                                                                      incident.element, event_action.plugin))
        # If the plugin is not enabled, lets move on.
        if not event_action.plugin.status:
            return

        incident_info = incident.incidentInfo
        plugin_parameters_json = event_action.pluginParameters
        plugin_parameters_json = re.sub('"__EVENTID__"', simplejson.dumps(unicode(incident.event.id)), plugin_parameters_json)
        plugin_parameters_json = re.sub('"__INCIDENTID__"', simplejson.dumps(unicode(incident.id)), plugin_parameters_json)
        plugin_parameters_json = re.sub('"__ELEMENT__"', simplejson.dumps(unicode(incident.element)), plugin_parameters_json)
        plugin_parameters_json = re.sub('"__MESSAGE__"', simplejson.dumps(unicode(incident.incidentInfo)), plugin_parameters_json)
        plugin_json = '{"plugin": %s, "parameters": %s}' % (simplejson.dumps(event_action.plugin.name), plugin_parameters_json)

        try:
            response = requests.post(event_action.plugin.server.url+'/runplugin', data=plugin_json,
                                     verify=event_action.plugin.server.ssl_verify)
            EventActionLog.objects.create(eventAction=event_action, text=response.text, incident=incident)
        except BaseException as e:
            event_action_error = "Error executing Plugin:%s: ErrMsg:%s %s" % (event_action.plugin.name, e.message, e.args)
            EventActionLog.objects.create(eventAction=event_action, text=event_action_error, incident=incident)
            self.logger.error(event_action_error)
        finally:
            return

    def start(self):
            self.logger.info("-=         Incident Dispatcher starting         =-")
            taskLoop = task.LoopingCall(self.check_open_incidents)
            taskLoop.start(self.POLLING_INTERVAL)
            reactor.suggestThreadPoolSize(30)
            reactor.run()


def dispatcher_dry_run(event, event_action):
    logger = logging.getLogger('main')
    dry_run_result = ''
    plugin_parameters_json = event_action.pluginParameters
    plugin_parameters_json = re.sub('"__EVENTID__"', simplejson.dumps(unicode(event.id)), plugin_parameters_json)
    plugin_parameters_json = re.sub('"__INCIDENTID__"', simplejson.dumps('test_incident_id'), plugin_parameters_json)
    plugin_parameters_json = re.sub('"__ELEMENT__"', simplejson.dumps('test_element_name'), plugin_parameters_json)
    plugin_parameters_json = re.sub('"__MESSAGE__"', simplejson.dumps('test_message'), plugin_parameters_json)
    plugin_json = '{"plugin": %s, "parameters": %s}' % (simplejson.dumps(event_action.plugin.name), plugin_parameters_json)
    logger.debug('Test sent to %s \n %s' % (event_action.plugin.server, plugin_json))
    try:
        response = requests.post(event_action.plugin.server.url+'/runplugin', data=plugin_json,
                                 verify=event_action.plugin.server.ssl_verify)
        dry_run_result = response.text
    except BaseException as e:
        dry_run_result = "Error executing Plugin:%s: %s" % (event_action.plugin.name, e.args)
    finally:
        return dry_run_result