from application import create_app
from os import environ

create_app = create_app()
if __name__ == '__main__':
    environ['env'] = 'prod'
    create_app.run(host='192.168.1.107')


