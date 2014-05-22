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

from .base import *

DEBUG = True
TEMPLATE_DEBUG = True
INSTALLED_APPS += ('django_nose',)
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
SOUTH_TESTS_MIGRATE = False
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(module)s %(process)d %(thread)d %(levelname)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(module)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'log_to_stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose',
        },
        'poller_log_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_PATH.child('logs') + "/poller.log",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'listener_log_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_PATH.child('logs') + "/listener.log",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'main': {
            'handlers': ['log_to_stdout'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'poller_logger': {
            'handlers': ['poller_log_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'listener_logger': {
            'handlers': ['listener_log_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },

    }
}

#Database config
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'cito',                         # Or path to database file if using sqlite3.
        'USER': '',                             # Not used with sqlite3.
        'PASSWORD': '',                         # Not used with sqlite3.
        'HOST': '',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
        'TEST_NAME': 'cito_tests_db',
        'OPTIONS': {
            'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'
        }
    }
}


##################################
# AWS::SQS Configuration settings
##################################
AWS_CONF = dict()
AWS_CONF['region'] = 'us-east-1'
AWS_CONF['awskey'] = ''
AWS_CONF['awssecret'] = ''
AWS_CONF['sqsqueue'] = 'citoq'


##################################
# RabbitMQ Configuration settings
##################################
RABBITMQ_CONF = dict()
RABBITMQ_CONF['host'] = 'localhost'
RABBITMQ_CONF['port'] = 5672
RABBITMQ_CONF['username'] = 'cito_user'
RABBITMQ_CONF['password'] = 'CHANGEME!'
RABBITMQ_CONF['ssl'] = False
RABBITMQ_CONF['exchange'] = ''
RABBITMQ_CONF['vhost'] = '/cito_event_listener'
RABBITMQ_CONF['queue'] = 'cito_commonq'


##############################
# Queue type: SQS or RABBITMQ
##############################
QUEUE_TYPE = 'RABBITMQ'


##############################
# Event Poller config
##############################
POLLER_CONFIG = dict()

# Polling interval in seconds
POLLER_CONFIG['interval'] = 5

# Number of messages to poll from queue
POLLER_CONFIG['batchsize'] = 10

# How long should the poller hold on the the message before someone else picks it up on
# Leave this to 60 seconds if you don't know what you are doing.
POLLER_CONFIG['visibility'] = 60


########################################
# Dispatcher config
# (will be deprecated in future release
########################################
DISPATCHER_CONFIG = dict()

# Polling interval
DISPATCHER_CONFIG['interval'] = 10

# Job lock expire time
DISPATCHER_CONFIG['lock_expire'] = 30


##############################
# Event Listener config
##############################
EVENT_LISTENER_CONFIG = dict()
EVENT_LISTENER_CONFIG['port'] = 8080