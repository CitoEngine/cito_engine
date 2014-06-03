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
from django.conf import settings
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet import reactor, threads
from queue_manager.sqs import sqs_writer
from queue_manager.rabbitmq import rabbitmq_writer

logger = logging.getLogger('listener_logger')


class AddEventPage(Resource):
    OK_MSG = ''
    UNAUTHORIZED_MSG = ''
    isLeaf = True

    def __init__(self):
        global log
        self.OK_MSG = '{"event": "accepted"}'
        self.UNAUTHORIZED_MSG = '{"event": "not accepted", "reason": "method not supported"}'
        if settings.QUEUE_TYPE in ['SQS', 'sqs']:
            self.queue_writer = sqs_writer.send_to_sqs
        elif settings.QUEUE_TYPE in ['RABBITMQ', 'rabbitmq']:
            self.queue_writer = rabbitmq_writer.send_to_rabbitmq
        else:
            raise ValueError('Incorrect value "%s" for QUEUE_TYPE in %s' %
                             (settings.QUEUE_TYPE, settings.SETTINGS_MODULE))

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        request.setHeader('Content-Type', 'application/json;charset=UTF-8')
        request.setHeader('Server', 'CitoEngine')
        return self.UNAUTHORIZED_MSG

    def render_POST(self, request):
        newdata = request.content.getvalue()
        d = threads.deferToThread(self.queue_writer, newdata)
        request.setHeader('Content-Type', 'application/json;charset=UTF-8')
        return self.OK_MSG


def clean_up():
    logger.info('Shutting down CitoEngine Event Listener')


# Twisted!
def start_listener():
    logger.info("Starting Listener at %s" % settings.EVENT_LISTENER_CONFIG['port'])
    logger.info("Queue type: %s" % settings.QUEUE_TYPE)
    root = Resource()
    root.putChild("addevent", AddEventPage())
    reactor.listenTCP(int(settings.EVENT_LISTENER_CONFIG['port']), Site(root))
    reactor.addSystemEventTrigger('before', 'shutdown', clean_up)
    reactor.run()
