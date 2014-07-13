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
from cito_engine.actions import json_formatter
from . import factories


class TetJSONFormatter(TestCase):

    def test_json_formatter(self):
        """
        Tests proper substitution of __VARS__ in plugin parameters
        """
        event = factories.EventFactory.create()
        message = 'The bird is the word!'
        plugin_params = '["__EVENTID__", "__INCIDENTID__", "__ELEMENT__", "__MESSAGE__", "SPHONGLE"]'
        event_action = factories.EventActionFactory(pluginParameters=plugin_params,
                                                    event=event)
        incident = factories.IncidentFactory.create(event=event)
        response = json_formatter.create_json_parameters(event_action=event_action,
                                                         incident=incident,
                                                         message=message)
        expected_response = '{"plugin": "%s", "parameters": ["%s", "%s", "%s", "%s", "SPHONGLE"]}' % (event_action.plugin.name, event.id, incident.id, incident.element, message)
        self.assertEqual(response, expected_response)

