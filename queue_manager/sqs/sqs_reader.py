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
import boto.sqs
from django.conf import settings

logger = logging.getLogger('poller_logger')


class SQSReader(object):
    def __init__(self):
        self.aws_key = settings.AWS_CONF['awskey']
        self.aws_secret = settings.AWS_CONF['awssecret']
        self.aws_region = settings.AWS_CONF['region']
        self.sqs_queue = settings.AWS_CONF['sqsqueue']
        self.sqs_message_visibility = settings.POLLER_CONFIG['visibility']
        self.batchsize = settings.POLLER_CONFIG['batchsize']

    def get_message_batch(self, batchsize=1):
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

            return message_batch

    def delete_message(self, message):
        return message.delete()