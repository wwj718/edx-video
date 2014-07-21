"""
This is the default template for our main set of AWS servers.
"""

# We intentionally define lots of variables that aren't used, and
# want to import all variables from base settings files
# pylint: disable=W0401, W0614

import json

from .common import *
from logsettings import get_logger_config
import os

# specified as an environment variable.  Typically this is set
# in the service's upstart script and corresponds exactly to the service name.
# Service variants apply config differences via env and auth JSON files,
# the names of which correspond to the variant.
SERVICE_VARIANT = os.environ.get('SERVICE_VARIANT', None)

# when not variant is specified we attempt to load an unvaried
# config set.
CONFIG_PREFIX = ""

if SERVICE_VARIANT:
    CONFIG_PREFIX = SERVICE_VARIANT + "."

############### ALWAYS THE SAME ################################
DEBUG = False
TEMPLATE_DEBUG = False

EMAIL_BACKEND = 'django_ses.SESBackend'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

###################################### CELERY  ################################

# Don't use a connection pool, since connections are dropped by ELB.
BROKER_POOL_LIMIT = 0
BROKER_CONNECTION_TIMEOUT = 1

# For the Result Store, use the django cache named 'celery'
CELERY_RESULT_BACKEND = 'cache'
CELERY_CACHE_BACKEND = 'celery'

# When the broker is behind an ELB, use a heartbeat to refresh the
# connection and to detect if it has been dropped.
BROKER_HEARTBEAT = 10.0
BROKER_HEARTBEAT_CHECKRATE = 2

# Each worker should only fetch one message at a time
CELERYD_PREFETCH_MULTIPLIER = 1

# Skip djcelery migrations, since we don't use the database as the broker
SOUTH_MIGRATION_MODULES = {
    'djcelery': 'ignore',
}

# Rename the exchange and queues for each variant

QUEUE_VARIANT = CONFIG_PREFIX.lower()

CELERY_DEFAULT_EXCHANGE = 'edx.{0}core'.format(QUEUE_VARIANT)

HIGH_PRIORITY_QUEUE = 'edx.{0}core.high'.format(QUEUE_VARIANT)
DEFAULT_PRIORITY_QUEUE = 'edx.{0}core.default'.format(QUEUE_VARIANT)
LOW_PRIORITY_QUEUE = 'edx.{0}core.low'.format(QUEUE_VARIANT)

CELERY_DEFAULT_QUEUE = DEFAULT_PRIORITY_QUEUE
CELERY_DEFAULT_ROUTING_KEY = DEFAULT_PRIORITY_QUEUE

CELERY_QUEUES = {
    HIGH_PRIORITY_QUEUE: {},
    LOW_PRIORITY_QUEUE: {},
    DEFAULT_PRIORITY_QUEUE: {}
}

############# NON-SECURE ENV CONFIG ##############################
# Things like server locations, ports, etc.
with open(ENV_ROOT / CONFIG_PREFIX + "env.json") as env_file:
    ENV_TOKENS = json.load(env_file)

EMAIL_BACKEND = ENV_TOKENS.get('EMAIL_BACKEND', EMAIL_BACKEND)
EMAIL_FILE_PATH = ENV_TOKENS.get('EMAIL_FILE_PATH', None)
LMS_BASE = ENV_TOKENS.get('LMS_BASE')
# Note that MITX_FEATURES['PREVIEW_LMS_BASE'] gets read in from the environment file.

SITE_NAME = ENV_TOKENS['SITE_NAME']

LOG_DIR = ENV_TOKENS['LOG_DIR']

CACHES = ENV_TOKENS['CACHES']

SESSION_COOKIE_DOMAIN = ENV_TOKENS.get('SESSION_COOKIE_DOMAIN')
SESSION_ENGINE = ENV_TOKENS.get('SESSION_ENGINE', SESSION_ENGINE)

# allow for environments to specify what cookie name our login subsystem should use
# this is to fix a bug regarding simultaneous logins between edx.org and edge.edx.org which can
# happen with some browsers (e.g. Firefox)
if ENV_TOKENS.get('SESSION_COOKIE_NAME', None):
    # NOTE, there's a bug in Django (http://bugs.python.org/issue18012) which necessitates this being a str()
    SESSION_COOKIE_NAME = str(ENV_TOKENS.get('SESSION_COOKIE_NAME'))

#Email overrides
DEFAULT_FROM_EMAIL = ENV_TOKENS.get('DEFAULT_FROM_EMAIL', DEFAULT_FROM_EMAIL)
DEFAULT_FEEDBACK_EMAIL = ENV_TOKENS.get('DEFAULT_FEEDBACK_EMAIL', DEFAULT_FEEDBACK_EMAIL)
ADMINS = ENV_TOKENS.get('ADMINS', ADMINS)
SERVER_EMAIL = ENV_TOKENS.get('SERVER_EMAIL', SERVER_EMAIL)
MKTG_URLS = ENV_TOKENS.get('MKTG_URLS', MKTG_URLS)
TECH_SUPPORT_EMAIL = ENV_TOKENS.get('TECH_SUPPORT_EMAIL', TECH_SUPPORT_EMAIL)

COURSES_WITH_UNSAFE_CODE = ENV_TOKENS.get("COURSES_WITH_UNSAFE_CODE", [])

#Timezone overrides
TIME_ZONE = ENV_TOKENS.get('TIME_ZONE', TIME_ZONE)


for feature, value in ENV_TOKENS.get('MITX_FEATURES', {}).items():
    MITX_FEATURES[feature] = value

LOGGING = get_logger_config(LOG_DIR,
                            logging_env=ENV_TOKENS['LOGGING_ENV'],
                            syslog_addr=(ENV_TOKENS['SYSLOG_SERVER'], 514),
                            debug=False,
                            service_variant=SERVICE_VARIANT)

#theming start:
PLATFORM_NAME = ENV_TOKENS.get('PLATFORM_NAME', 'edX')


################ SECURE AUTH ITEMS ###############################
# Secret things: passwords, access keys, etc.
with open(ENV_ROOT / CONFIG_PREFIX + "auth.json") as auth_file:
    AUTH_TOKENS = json.load(auth_file)

# If Segment.io key specified, load it and turn on Segment.io if the feature flag is set
# Note that this is the Studio key. There is a separate key for the LMS.
SEGMENT_IO_KEY = AUTH_TOKENS.get('SEGMENT_IO_KEY')
if SEGMENT_IO_KEY:
    MITX_FEATURES['SEGMENT_IO'] = ENV_TOKENS.get('SEGMENT_IO', False)


AWS_ACCESS_KEY_ID = AUTH_TOKENS["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = AUTH_TOKENS["AWS_SECRET_ACCESS_KEY"]
DATABASES = AUTH_TOKENS['DATABASES']
MODULESTORE = AUTH_TOKENS['MODULESTORE']
CONTENTSTORE = AUTH_TOKENS['CONTENTSTORE']

# Datadog for events!
DATADOG_API = AUTH_TOKENS.get("DATADOG_API")

# Celery Broker
CELERY_BROKER_TRANSPORT = ENV_TOKENS.get("CELERY_BROKER_TRANSPORT", "")
CELERY_BROKER_HOSTNAME = ENV_TOKENS.get("CELERY_BROKER_HOSTNAME", "")
CELERY_BROKER_VHOST = ENV_TOKENS.get("CELERY_BROKER_VHOST", "")
CELERY_BROKER_USER = AUTH_TOKENS.get("CELERY_BROKER_USER", "")
CELERY_BROKER_PASSWORD = AUTH_TOKENS.get("CELERY_BROKER_PASSWORD", "")

BROKER_URL = "{0}://{1}:{2}@{3}/{4}".format(CELERY_BROKER_TRANSPORT,
                                            CELERY_BROKER_USER,
                                            CELERY_BROKER_PASSWORD,
                                            CELERY_BROKER_HOSTNAME,
                                            CELERY_BROKER_VHOST)
