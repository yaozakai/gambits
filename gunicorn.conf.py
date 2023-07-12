"""gunicorn WSGI server configuration."""
import sys
from multiprocessing import cpu_count
from os import environ


def max_workers():
    return cpu_count()


if 'stage' in sys.argv[1:]:
    bind = '0.0.0.0:' + environ.get('PORT', '5001')
else:
    bind = '0.0.0.0:' + environ.get('PORT', '5000')


max_requests = 1000
worker_class = 'gevent'
workers = max_workers()


