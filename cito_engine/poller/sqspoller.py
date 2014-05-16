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
import simplejson
import sys
from twisted.internet import task, reactor, threads
import boto.sqs
from django.conf import settings
from cito_engine.actions.incidents import add_incident, ProcessIncident

# TODO: Workaround to de-duplication caused by un-deleted message

logger = logging.getLogger('poller_logger')


class SQSPoller:

    def __init__(self):
        self.aws_key = settings.AWS_CONF['awskey']
        self.aws_secret = settings.AWS_CONF['awssecret']
        self.aws_region = settings.AWS_CONF['region']
        self.sqs_queue = settings.AWS_CONF['sqsqueue']

        self.poll_interval = settings.SQSPOLLER_CONFIG['interval']
        self.sqs_message_visibility = settings.SQSPOLLER_CONFIG['visibility']
        self.batchsize = settings.SQSPOLLER_CONFIG['batchsize']

        self.message_format = ['event', 'timestamp']
        self.event_format = ['eventid', 'element', 'message']

    def parse_message(self, sqs_message):
        e = []
        # decode JSON
        try:
            parsed_json = simplejson.loads(sqs_message.get_body())
        except Exception as exception:
            logger.error('Error parsing JSON %s' % exception)
            return False
        for k in self.message_format:
            if not k in parsed_json:
                logger.error('MessageTag %s not defined in sqs_message.id:%s, sqs_message_body:%s' %
                             (k, sqs_message.id, parsed_json))
                return False
        e = parsed_json['event']
        for k in self.event_format:
            if not k in e:
                logger.error('EventTag %s not defined in sqs_message.id:%s, sqsMessageBody:%s' %
                             (k, sqs_message.id, parsed_json))
                return False

        # Add incident to Database
        incident = add_incident(e, parsed_json['timestamp'])

        # Check incident thresholds and fire events
        if incident and incident.status == 'Active':
            threads.deferToThread(ProcessIncident, incident, e['message'])
        logger.info('MsgOk: EventID:%s, Element:%s, Message%s on Timestamp:%s' % (e['eventid'],
                                                                                  e['element'],
                                                                                  e['message'],
                                                                                  parsed_json['timestamp']))
        return True

    def get_sqs_messages(self, batchsize=1):
        logger.debug("Poller run: BATCHSIZE=%s, POLLING_INTERVAL=%s" % (batchsize, self.poll_interval))
        conn = boto.sqs.connect_to_region(self.aws_region,
                                          aws_access_key_id=self.aws_key,
                                          aws_secret_access_key=self.aws_secret,
                                          is_secure=False)
        if conn is None:
            logger.error("Could not connect to AWS: region=%s" % self.aws_region)
        else:
            q = conn.get_queue(self.sqs_queue)
            if q is None:
                logger.error("Error connecting to SQS queue: %s" % self.sqs_queue)
                sys.exit(1)

            message_batch = q.get_messages(batchsize, visibility_timeout=self.sqs_message_visibility)

            if len(message_batch) > 0:
                logger.info("Parsing %s messages" % len(message_batch))
            else:
                logger.debug("No messages in queue")

            for m in message_batch:
                logger.debug("Received: %s with ID:%s" % (m.get_body(), m.id))
                if not self.parse_message(m):
                    logger.error('MsgID:%s will not be written' % m.id)

                try:
                    d = threads.deferToThread(q.delete_message, m)
                except Exception as e:
                    logger.error("Error deleting msg from SQS: %s" % e)

    def begin_sqs_poller(self):
        logger.info("-=         SQS Poller starting         =-")
        logger.info("-= [BATCHSIZE=%s] [POLLING_INTERVAL=%s]=-" % (self.batchsize, self.poll_interval))
        task_loop = task.LoopingCall(self.get_sqs_messages, self.batchsize)
        task_loop.start(self.poll_interval)
        reactor.run()
