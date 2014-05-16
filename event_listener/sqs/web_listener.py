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
import sys
from time import time
import simplejson

from django.conf import settings

from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet import reactor, threads
# from twisted.python import log

import boto.sqs
from boto.sqs.message import Message

logger = logging.getLogger('listener_logger')


class AddEventPage(Resource):
    OK_MSG = ''
    UNAUTHORIZED_MSG = ''
    isLeaf = True

    def __init__(self):
        global log
        self.OK_MSG = '{"event":"accepted"}'
        self.UNAUTHORIZED_MSG = '{"event": "not accepted", "reason" : "method not supported"}'

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        request.setHeader('Content-Type', 'application/json;charset=UTF-8')
        request.setHeader('Server', 'Cito')
        return self.UNAUTHORIZED_MSG

    def send_to_sqs(self, msg):
        global log
        conn = boto.sqs.connect_to_region(settings.AWS_CONF['region'],
                                          aws_access_key_id=settings.AWS_CONF['awskey'],
                                          aws_secret_access_key=settings.AWS_CONF['awssecret'],
                                          is_secure=False)
        try:
            parsed_json = simplejson.loads(msg)
        except Exception as e:
            logger.critical("Invalid message:%s Reason:%s" % (msg, e))

        # wrap with timestamp
        if 'timestamp' not in parsed_json:
            msg = '{"event":%s , "timestamp":"%d"}' % (msg, int(time()))

        logger.info('Message %s' % msg)

        # Send to SQS
        if conn is None:
            logger.critical("Could not connect to AWS: region=%s" % settings.AWS_CONF['region'])
        else:
            q = conn.get_queue(settings.AWS_CONF['sqsqueue'])
            if q is None:
                logger.critical("Error connecting to SQS queue: %s" %
                        settings.AWS_CONF['sqsqueue'])
                return
            m = Message()
            m.set_body(msg)
            q.write(m)
            if m.id is None:
                logger.critical("Could not send this msg to queue: %s" % m.get_body())
            else:
                logger.info('Wrote %s' % m.id)

    def render_POST(self, request):
        newdata = request.content.getvalue()
        d = threads.deferToThread(self.send_to_sqs, newdata)
        request.setHeader('Content-Type', 'application/json;charset=UTF-8')
        return self.OK_MSG


# Twisted!
def start_listener():
    logger.info("Starting Listener at %s" % settings.EVENT_LISTENER_CONFIG['port'])
    root = Resource()
    root.putChild("addevent", AddEventPage())
    reactor.listenTCP(int(settings.EVENT_LISTENER_CONFIG['port']), Site(root))
    reactor.run()
