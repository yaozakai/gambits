from gevent import monkey

monkey.patch_all()

from application import create_app
from os import environ

create_app = create_app()
if __name__ == '__main__':
    environ['env'] = 'prod'
    # create_app.run(port=5000, host='10.138.0.2')  # for local testing (like with iPhone)
    create_app.run()  # for full integration with CQ9 (keep as localhost)
