from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gotcha.settings')

# app = Celery('gotcha')
app = Celery('', 
    backend="redis://rediscloud:HwvYf4EUPwSi6WmGEiC49K28ZCymmUSp@redis-18821.c90.us-east-1-3.ec2.cloud.redislabs.com:18821", 
    broker="redis://rediscloud:HwvYf4EUPwSi6WmGEiC49K28ZCymmUSp@redis-18821.c90.us-east-1-3.ec2.cloud.redislabs.com:18821")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

# app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

if __name__ == '__main__':
    app.start()

# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))