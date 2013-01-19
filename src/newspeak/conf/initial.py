"""
Initial settings for newspeak. This file gets copied and updated by
newspeak.runner.generate_settings.
"""

import os.path

CONF_ROOT = os.path.dirname(__file__)

DATABASES = {
    'default': {
        # You can swap out the engine for MySQL easily by changing this value
        # to ``django.db.backends.mysql`` or to PostgreSQL with
        # ``django.db.backends.postgresql_psycopg2``

        # If you change this, you'll also need to install the appropriate
        # python package: psycopg2 (Postgres) or mysql-python
        'ENGINE': 'django.db.backends.sqlite3',

        'NAME': os.path.join(CONF_ROOT, 'newspeak.db'),
        # 'USER': 'postgres',
        # 'PASSWORD': '',
        # 'HOST': '',
        # 'PORT': '',
    }
}

# Override the time zone and the language code

# TIME_ZONE = 'UTC'
# LANGUAGE_CODE = 'nl-nl'

# If you're expecting any kind of real traffic on newspeak, we highly
# recommend configuring memcached.

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': ['127.0.0.1:11211'],
#     }
# }

# Number of threads
# NEWSPEAK_THREADS = 64
