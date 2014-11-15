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
from cito_engine.models import EventAction, EventActionCounter


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
    except Exception as e:
        dry_run_result = "Error executing Plugin:%s: reason:%s" % (event_action.plugin.name, e)
    finally:
        return dry_run_result


def update_eventaction_counters(incident, timer_value=0):
    try:
        event_actions = EventAction.objects.filter(event=incident.event, isEnabled=True)
    except EventAction.DoesNotExist:
        return

    for event_action in event_actions:
        event_action_counter, create = EventActionCounter.objects.get_or_create(incident=incident,
                                                                                event_action=event_action)
        if not create:
            event_action_counter.update_counters(timer_value=timer_value)
    return