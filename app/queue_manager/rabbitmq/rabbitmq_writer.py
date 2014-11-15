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

sudo rabbitmqctl add_user cito_user cito_pass
sudo rabbitmqctl add_vhost /cito_event_listener
sudo rabbitmqctl set_permissions -p /cito_event_listener cito_user ".*" ".*" ".*"
"""
import pika
from django.conf import settings
import logging

logger = logging.getLogger('listener_logger')


def send_to_rabbitmq(message):
    """
    Connects to rabbitmq and sends the json message to the queue
    :param message:
    :return:
    """
    credentials = pika.PlainCredentials(settings.RABBITMQ_CONF['username'], settings.RABBITMQ_CONF['password'])
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=settings.RABBITMQ_CONF['host'],
            port=settings.RABBITMQ_CONF['port'],
            credentials=credentials,
            virtual_host=settings.RABBITMQ_CONF['vhost'],
            ssl=settings.RABBITMQ_CONF['ssl']))
    except pika.exceptions.AMQPConnectionError:
        logger.error('Error connecting to RabbitMQ server: %s' % settings.RABBITMQ_CONF['host'])
        return

    try:
        channel = connection.channel()
    except Exception as e:
        logger.error('Error selecting channel, reason: %e')
        return False

    try:
        channel.queue_declare(queue=settings.RABBITMQ_CONF['queue'], durable=True)
    except Exception as e:
        logger.error('Error declaring queue: %s, reason: %s' % (settings.RABBITMQ_CONF['queue'], e))
        return False

    try:
        channel.basic_publish(exchange=settings.RABBITMQ_CONF['exchange'],
                              routing_key=settings.RABBITMQ_CONF['queue'],
                              body=message,
                              properties=pika.BasicProperties(
                                  delivery_mode=2, # make message persistent
                              ),)
    except Exception as e:
        logger.error('Error publishing message to EXCHANGE: %s, QUEUE:%s, reason: %s' %
                     (settings.RABBITMQ_CONF['exchange'], settings.RABBITMQ_CONF['queue'], e))
        logger.error('Message received by RabbitMQ: %s' % message)
        return False

    logger.debug('Message: %s' % message)
    logger.info('Incident successfully written to RabbitMQ')

    #close the connection
    try:
        if connection.is_open:
            connection.close()
    except Exception as e:
        logger.error('Cannot close connection, reason: %s' % e)

    return True