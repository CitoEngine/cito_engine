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
import pika
import sys
from django.conf import settings

logger = logging.getLogger('poller_logger')


class RabbitMQReader(object):
    def __init__(self):
        self.credentials = pika.PlainCredentials(settings.RABBITMQ_CONF['username'], settings.RABBITMQ_CONF['password'])
        self.channel = None
        self.connection = None

    def _connect_mq(self):
        """
        Connects to rabbitmq and selects the channel
        :return:
        """
        logger.info('Connecting to rabbitmq server..')
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=settings.RABBITMQ_CONF['host'],
                port=settings.RABBITMQ_CONF['port'],
                credentials=self.credentials,
                virtual_host=settings.RABBITMQ_CONF['vhost'],
                ssl=settings.RABBITMQ_CONF['ssl']))
        except pika.exceptions.AMQPConnectionError as e:
            logger.error('Error connecting to RabbitMQ server: %s, reason: %s' % (settings.RABBITMQ_CONF['host'], e))
            return False

        try:
            self.channel = self.connection.channel()
        except Exception as e:
            logger.error('Error selecting channel, reason: %e')
            return False

        try:
            self.channel.queue_declare(queue=settings.RABBITMQ_CONF['queue'], durable=True)
        except Exception as e:
            logger.error('Error declaring queue: %s, reason: %s' % (settings.RABBITMQ_CONF['queue'], e))
            return False

        return True

    def _close_mq(self):
        """
        Closes connection to rabbitmq
        :return:
        """
        logger.info('Closing connection to rabbitmq')
        # if self.channel.is_open:
        #     try:
        #         self.channel.close()
        #     except Exception as e:
        #         logger.error('Error closing channel, reason: %s' % e)

        if self.connection.is_open:
            try:
                self.connection.close()
            except Exception as e:
                logger.error('Error closing connection, reason: %s' % e)

    def get_message(self):
        """
        Fetches a single message from rabbitmq
        :return:
        """
        connected = False

        if self.connection is None:
            connected = self._connect_mq()

        if not connected:
            return None, None

        if not self.connection.is_open:
            self._connect_mq()
        else:
            logger.debug('Already connected..')

        try:
            method_frame, header_frame, body = self.channel.basic_get(settings.RABBITMQ_CONF['queue'], no_ack=False)
        except Exception as e:
            logger.error('Error fetching message from rabbitmq, reason: %s' % e)
            # Send an empty tuple if channel.basic_get failed for some reason.
            return None, None

        # self._close_mq()

        if method_frame:
            return method_frame, body
        else:
            # Send an empty tuple if channel.basic_get did not return a message
            return None, None


    def delete_message(self, method_frame):
        """
        Deletes the message from queue
        :param method_frame:
        :return:
        """
        if self.connection is None or self.channel is None:
            self._connect_mq()

        if not self.connection.is_open or self.channel.is_closed:
            self._connect_mq()

        try:
            self.channel.basic_ack(method_frame.delivery_tag)
        except AttributeError:
            logger.error('RABBITMQ delete failure for method_frame: %s, type(method_frame): %s' % (method_frame, type(method_frame)))