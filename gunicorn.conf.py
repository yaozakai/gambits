"""gunicorn WSGI server configuration."""

from multiprocessing import cpu_count
from os import environ


def max_workers():
    return cpu_count()


bind = '192.168.1.107:' + environ.get('PORT', '5000')
max_requests = 1000
worker_class = 'gevent'
workers = max_workers()


