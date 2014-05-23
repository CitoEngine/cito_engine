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
from django.conf import settings

logger = logging.getLogger('poller_logger')


class RabbitMQReader(object):
    def __init__(self):
        self.credentials = pika.PlainCredentials(settings.RABBITMQ_CONF['username'], settings.RABBITMQ_CONF['password'])
        self.channel = None
        self.connection = None

    def _connect_mq(self):
        logger.info('Connecting to rabbitmq server..')
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=settings.RABBITMQ_CONF['host'],
                port=settings.RABBITMQ_CONF['port'],
                credentials=self.credentials,
                virtual_host=settings.RABBITMQ_CONF['vhost'],
                ssl=settings.RABBITMQ_CONF['ssl']))
        except pika.exceptions.AMQPConnectionError:
            logger.error('Error connecting to RabbitMQ server: %s' % settings.RABBITMQ_CONF['host'])
            return False

        try:
            self.channel = self.connection.channel()
        except:
            logger.error('Error selecting channel')
            return False

        try:
            self.channel.queue_declare(queue=settings.RABBITMQ_CONF['queue'], durable=True)
        except:
            logger.error('Error declaring queue: %s' % settings.RABBITMQ_CONF['queue'])
            return False

        return True

    def get_message(self):
        if not self.connection:
            self._connect_mq()
        try:
            method_frame, header_frame, body = self.channel.basic_get(settings.RABBITMQ_CONF['queue'], no_ack=False)
        except:
            # Send an empty tuple if channel.basic_get failed for some reason.
            return None, None

        if method_frame:
            return method_frame, body
        else:
            # Send an empty tuple if channel.basic_get did not return a message
            return None, None

    def delete_message(self, method_frame):
        try:
            self.channel.basic_ack(method_frame.delivery_tag)
        except AttributeError:
            logger.error('RABBITMQ delete failure for method_frame: %s, type(method_frame): %s' % (method_frame, type(method_frame)))