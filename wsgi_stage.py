"""gunicorn WSGI server configuration."""
from multiprocessing import cpu_count
from os import environ


def max_workers():
    return cpu_count()


bind = '127.0.0.1:' + environ.get('PORT', '5001')

max_requests = 1000
worker_class = 'gevent'
workers = 1
environ['env'] = 'stage'


