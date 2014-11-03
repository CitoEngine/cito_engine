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
from datetime import datetime
import simplejson
import boto.sqs
from boto.sqs.message import Message
from django.conf import settings

logger = logging.getLogger('listener_logger')


def send_to_sqs(msg):
    parsed_json = ''
    conn = boto.sqs.connect_to_region(settings.AWS_CONF['region'],
                                      aws_access_key_id=settings.AWS_CONF['awskey'],
                                      aws_secret_access_key=settings.AWS_CONF['awssecret'],
                                      is_secure=False)
    try:
        parsed_json = simplejson.loads(msg)
    except Exception as e:
        logger.critical('Invalid message:%s Reason:%s' % (msg, e))
        return False

    # wrap with timestamp
    if 'timestamp' not in parsed_json:
        msg = '{"event":%s , "timestamp":"%d"}' % (msg, int(datetime.utcnow().strftime('%s')))

    logger.debug('Message %s' % msg)

    # Send to SQS
    if conn is None:
        logger.critical("Could not connect to AWS: region=%s" % settings.AWS_CONF['region'])
        return False
    else:
        q = conn.get_queue(settings.AWS_CONF['sqsqueue'])
        if q is None:
            logger.critical("Error connecting to SQS queue: %s" % settings.AWS_CONF['sqsqueue'])
            return
        m = Message()
        m.set_body(msg)
        q.write(m)
        if m.id is None:
            logger.critical('Could not send this msg to queue: %s' % m.get_body())
            return False
        else:
            logger.info('Incident successfully written to SQS, msg_id:%s' % m.id)
            return True