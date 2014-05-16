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

import re
import simplejson


def create_json_parameters(event_action, incident, message=None):
    plugin_parameters = event_action.pluginParameters
    plugin_parameters = re.sub('"__EVENTID__"', simplejson.dumps(unicode(incident.event.id)), plugin_parameters)
    plugin_parameters = re.sub('"__INCIDENTID__"', simplejson.dumps(unicode(incident.id)), plugin_parameters)
    plugin_parameters = re.sub('"__ELEMENT__"', simplejson.dumps(unicode(incident.element)), plugin_parameters)
    plugin_parameters = re.sub('"__MESSAGE__"', simplejson.dumps(unicode(message)), plugin_parameters)
    return '{"plugin": %s, "parameters": %s}' % (simplejson.dumps(unicode(event_action.plugin.name)), plugin_parameters)