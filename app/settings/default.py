import ConfigParser
from django.core.exceptions import ImproperlyConfigured
from .base import *

CITOENGINE_CONFIG_FILE = None
config_file_locations = ['/opt/citoengine/conf/citoengine.conf', 'settings/citoengine.conf', 'citoengine.conf']

if os.getenv('CITOENGINE_CONFIG_FILE') is not None:
    config_file_locations.insert(0, os.getenv('CITOENGINE_CONFIG_FILE'))

for c in config_file_locations:
    if os.path.exists(c):
        CITOENGINE_CONFIG_FILE = c
        break

if CITOENGINE_CONFIG_FILE is None:
    raise ImproperlyConfigured('No configuration file found at %s' % ':'.join(config_file_locations))

conf = ConfigParser.ConfigParser()
conf.readfp(open(CITOENGINE_CONFIG_FILE, 'r'))

DEBUG = conf.getboolean('GENERAL', 'DEBUG')
TEMPLATE_DEBUG = conf.getboolean('GENERAL', 'TEMPLATE_DEBUG')
LOG_PATH = conf.get('GENERAL', 'LOG_PATH')
QUEUE_TYPE = conf.get('GENERAL', 'QUEUE_TYPE')
TIME_ZONE = conf.get('GENERAL', 'TIME_ZONE')
LOGIN_URL = conf.get('GENERAL', 'LOGIN_URL')
ALLOWED_HOSTS = conf.get('GENERAL', 'ALLOWED_HOSTS').split(',')

# Setup Logging
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
            'filename': LOG_PATH + "/poller.log",
            'maxBytes': 100000000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'listener_log_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_PATH + "/listener.log",
            'maxBytes': 100000000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'auth_log_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_PATH + "/auth.log",
            'maxBytes': 100000000,
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
        'auth_logger': {
            'handlers': ['auth_log_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
## End logging


DATABASES = dict(default=dict())
DATABASES['default']['ENGINE'] = 'django.db.backends.%s' % conf.get('DATABASE', 'ENGINE')
DATABASES['default']['NAME'] = conf.get('DATABASE', 'DBNAME')
DATABASES['default']['USER'] = conf.get('DATABASE', 'DBUSER')
DATABASES['default']['PASSWORD'] = conf.get('DATABASE', 'DBPASSWORD')
DATABASES['default']['HOST'] = conf.get('DATABASE', 'DBHOST')
DATABASES['default']['PORT'] = conf.get('DATABASE', 'DBPORT')
DATABASES['default']['TEST_NAME'] = 'cito_tests_db'
DATABASES['default']['OPTIONS'] = {
    'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'
}


if QUEUE_TYPE == 'RABBITMQ':
    # ################################
    # RabbitMQ Configuration settings
    #################################
    RABBITMQ_CONF['host'] = conf.get('RABBITMQ', 'HOST')
    RABBITMQ_CONF['port'] = int(conf.get('RABBITMQ', 'PORT'))
    RABBITMQ_CONF['username'] = conf.get('RABBITMQ', 'USERNAME')
    RABBITMQ_CONF['password'] = conf.get('RABBITMQ', 'PASSWORD')
    RABBITMQ_CONF['ssl'] = conf.getboolean('RABBITMQ', 'SSL')
    RABBITMQ_CONF['exchange'] = conf.get('RABBITMQ', 'EXCHANGE')
    RABBITMQ_CONF['vhost'] = conf.get('RABBITMQ', 'VHOST')
    RABBITMQ_CONF['queue'] = conf.get('RABBITMQ', 'QUEUE')

elif QUEUE_TYPE == 'SQS':
    #################################
    # AWS::SQS Configuration settings
    #################################
    AWS_CONF['region'] = conf.get('AWS', 'REGION')
    AWS_CONF['awskey'] = conf.get('AWS', 'AWSKEY')
    AWS_CONF['awssecret'] = conf.get('AWS', 'AWSSECRET')
    AWS_CONF['sqsqueue'] = conf.get('AWS', 'SQSQUEUE')

else:
    raise ImproperlyConfigured('No valid queue type defined')

POLLER_CONFIG['interval'] = int(conf.get('POLLER', 'INTERVAL'))
POLLER_CONFIG['batchsize'] = int(conf.get('POLLER', 'BATCHSIZE'))
POLLER_CONFIG['visibility'] = int(conf.get('POLLER', 'VISIBILITY'))

JIRA_OPTS = dict()
JIRA_ENABLED = False
try:
    if conf.get('JIRA_OPTS', 'JIRA_ENABLED').lower() == 'true':
        JIRA_ENABLED = True
        JIRA_OPTS['URL'] = conf.get('JIRA_OPTS', 'JIRA_URL')
        JIRA_OPTS['USER'] = conf.get('JIRA_OPTS', 'JIRA_USER')
        JIRA_OPTS['PASSWORD'] = conf.get('JIRA_OPTS', 'JIRA_PASSWORD')
        JIRA_OPTS['DEFAULT_PROJECT'] = conf.get('JIRA_OPTS', 'JIRA_DEFAULT_PROJECT')
        JIRA_OPTS['DEFAULT_ISSUE_TYPE'] = conf.get('JIRA_OPTS', 'JIRA_DEFAULT_ISSUE_TYPE')
        # Double check if all JIRA parameters came through
        for k in ['URL', 'USER', 'PASSWORD', 'DEFAULT_PROJECT', 'DEFAULT_ISSUE_TYPE']:
            if not JIRA_OPTS.get(k):
                raise ImproperlyConfigured('JIRA integeration is enabled but JIRA_%s value is missing' % k)
except ConfigParser.NoSectionError:
    pass

# if conf.has_section('DEVELOPMENT'):
#     try:
#         if conf.getboolean('DEVELOPMENT', 'DEVMODE'):
#             INSTALLED_APPS += tuple(conf.items('DEVELOPMENT', 'INSTALLED_APPS'))
#             TEST_RUNNER = conf.get('DEVELOPMENT', 'TEST_RUNNER')
#             SOUTH_TESTS_MIGRATE = conf.getboolean('DEVELOPMENT', 'SOUTH_TESTS_MIGRATE')
#     except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
#         pass
