"""gunicorn WSGI server configuration."""
import sys
from multiprocessing import cpu_count
from os import environ


def max_workers():
    return cpu_count()


bind = '127.0.0.1:' + environ.get('PORT', '6001')

max_requests = 1000
worker_class = 'gevent'
workers = max_workers()


