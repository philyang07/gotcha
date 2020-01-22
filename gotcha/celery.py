from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gotcha.settings')

app = Celery('gotcha')
# app = Celery('gotcha', backend='amqp://dyfobtkj:YsAQDCL9MtX8dNjL7a91-fdlhJzaR9H2@vulture.rmq.cloudamqp.com/dyfobtkj', broker="pyamqp://dyfobtkj:YsAQDCL9MtX8dNjL7a91-fdlhJzaR9H2@vulture.rmq.cloudamqp.com/dyfobtkj")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))