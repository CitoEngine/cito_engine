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
from twisted.internet import task, reactor, threads
from django.conf import settings
from cito_engine.actions.incidents import add_incident, ProcessIncident
from queue_manager.sqs import sqs_reader
from queue_manager.rabbitmq import rabbitmq_reader

# TODO: Workaround to de-duplication caused by un-deleted message

logger = logging.getLogger('poller_logger')


class EventPoller(object):

    def __init__(self):
        self.message_format = ['event', 'timestamp']
        self.event_format = ['eventid', 'element', 'message']
        self.poll_interval = settings.POLLER_CONFIG['interval']
        self.queue_reader = None

    def parse_message(self, message):
        """
        Parses a message body and returns True if message should be deleted from queeu
        :param message:
        :return boolena: True if message can be deleted from queue, else False
        """
        e = []
        # decode JSON
        try:
            parsed_json = simplejson.loads(message)
        except Exception as exception:
            logger.error('Error parsing JSON %s' % exception)
            return True

        for k in self.message_format:
            if not k in parsed_json:
                logger.error('MessageTag %s not defined in  message:%s' %
                             (k, parsed_json))
                return True

        e = parsed_json['event']
        for k in self.event_format:
            if not k in e:
                logger.error('EventTag %s not defined in  message:%s' %
                             (k, parsed_json))
                return True

        # Make sure we received a valid timestamp
        try:
            timestamp = int(parsed_json['timestamp'])
        except Exception as exp:
            logger.error('Invalid timestamp in message:%s, reason:%s' % (message, exp))
            return True

        # Add incident to Database
        # This try/except block will catch
        # django.db.utils.OperationalError: (2006, 'MySQL server has gone away')
        # for a very low traffic server
        try:
            incident = add_incident(e, timestamp)
        except Exception as exp:
            logger.error('Could not add incident:%s, reason:%s' % (e, exp))
            return False

        # Check incident thresholds and fire events
        if incident and incident.status == 'Active':
            threads.deferToThread(ProcessIncident, incident, e['message'])
        logger.info('MsgOk: EventID:%s, Element:%s, Message:%s on Timestamp:%s' % (e['eventid'],
                                                                                   e['element'],
                                                                                   e['message'],
                                                                                   timestamp))
        return True

    def _get_sqs_messages(self):
        logger.info("-= SQS Poller run: BATCHSIZE=%s, POLLING_INTERVAL=%s =-" %
                    (settings.POLLER_CONFIG['batchsize'], settings.POLLER_CONFIG['interval']))
        for m in self.queue_reader.get_message_batch():
            logger.debug("Received: %s with ID:%s" % (m.get_body(), m.id))

            if not self.parse_message(m.get_body()):
                logger.error('MsgID:%s could not be written, will retry again.' % m.id)
            else:
                try:
                    d = threads.deferToThread(self.queue_reader.delete_message, m)
                    logger.debug('MsgID:%s deleted from queue' % m.id)
                except Exception as exp:
                    logger.error("Error deleting msg from SQS: %s" % exp)

    def _get_rabbitmq_messages(self):
        logger.info("-= RABBITMQ Poller run: BATCHSIZE=%s, POLLING_INTERVAL=%s =-" %
                    (settings.POLLER_CONFIG['batchsize'], settings.POLLER_CONFIG['interval']))

        # Emulate batch messages by polling rabbitmq server multiple times
        try:
            for i in range(settings.POLLER_CONFIG['batchsize']):
                message_frame, message_body = self.queue_reader.get_message()
                if not message_frame:
                    raise StopIteration()

                if not self.parse_message(message_body):
                    logger.error('MsgID:%s could not be written, will retry again.' % message_frame.delivery_tag)
                else:
                    try:
                        d = threads.deferToThread(self.queue_reader.delete_message, message_frame)
                        logger.debug('MsgID:%s deleted from queue' % message_frame.delivery_tag)
                    except Exception as exp:
                        logger.error("Error deleting msg from RabbitMQ: %s" % exp)
        except StopIteration:
            pass

    def _get_messages(self):
        if settings.QUEUE_TYPE in ['SQS', 'sqs']:
            self.queue_reader = sqs_reader.SQSReader()
            self._get_sqs_messages()
        elif settings.QUEUE_TYPE in ['RABBITMQ', 'rabbitmq']:
            self.queue_reader = rabbitmq_reader.RabbitMQReader()
            try:
                self._get_rabbitmq_messages()
            except Exception as e:
                logger.fatal('Could not fetch messages from RabbitMQ reason:%s' % e)
        else:
            raise ValueError('Incorrect value "%s" for QUEUE_TYPE in %s' %
                             (settings.QUEUE_TYPE, settings.SETTINGS_MODULE))

    def begin_event_poller(self):
        logger.info("-=         Event Poller starting         =-")
        task_loop = task.LoopingCall(self._get_messages)
        task_loop.start(self.poll_interval)
        reactor.run()
