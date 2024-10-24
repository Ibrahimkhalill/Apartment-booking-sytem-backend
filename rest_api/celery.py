from __future__ import absolute_import, unicode_literals
import os
import billiard
import sys

from celery import Celery

# Set the start method for multiprocessing only if not already set
if not billiard.get_start_method():
    if sys.platform == 'win32':
        billiard.set_start_method('spawn')
    else:
        billiard.set_start_method('fork')

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest_api.settings')

# Create Celery application instance
app = Celery('rest_api')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Additional Celery configurations
app.conf.update(
    broker_url='redis://localhost:6379/0',  # Adjust according to your setup
    broker_connection_retry_on_startup=True,
    task_serializer='json',
    accept_content=['json'],
    result_backend='redis://localhost:6379/0',  # Adjust according to your setup
    timezone='UTC',  # Adjust to your preferred timezone
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
