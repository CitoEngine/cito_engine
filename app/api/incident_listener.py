from __future__ import absolute_import
import json
import gevent
import logging
from django.conf import settings
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from queue_manager.sqs import sqs_writer
from queue_manager.rabbitmq import rabbitmq_writer
from api.json_responses import json_error, json_ok

logger = logging.getLogger('listener_logger')


class IncidentListenerAPI(View):
    """
    API for accepting incidents in JSON format
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(IncidentListenerAPI, self).dispatch(*args, **kwargs)

    def post(self, request):
        """
        Accepts JSON
            {
                "event":
                {
                    "eventid": <int>,
                    "element": <string>,
                    "message": <string>,
                },
                "timestamp": <int>
            }
        :return JSON response:
        """

        try:
            parsed_json = json.loads(request.body)
        except Exception as e:
            return json_error('Invalid JSON' % e)

        for k in settings.INCIDENT_PARAMS:
            if k not in parsed_json:
                return json_error('Missing JSON key:%s' % k)

        if settings.QUEUE_TYPE in ['SQS', 'sqs']:
            queue_writer = sqs_writer.send_to_sqs
        elif settings.QUEUE_TYPE in ['RABBITMQ', 'rabbitmq']:
            queue_writer = rabbitmq_writer.send_to_rabbitmq
        else:
            raise ValueError('Incorrect value "%s" for QUEUE_TYPE in %s' %
                             (settings.QUEUE_TYPE, settings.SETTINGS_MODULE))

        gevent.spawn(queue_writer, request.body)
        gevent.sleep(0)
        return json_ok('accepted')