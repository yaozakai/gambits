# """gunicorn WSGI server configuration."""
# import sys
# from socket import socket
#
# from config import app as application
#
# from route_cq9_api import cq9_api
# from route_template import template
# from route_user import user
# from route_wallet import wallet
# from utils import reload_icon_placement, reload_translations, reload_game_titles
#
#
# if __name__ == '__main__':
#
#     reload_icon_placement()
#     reload_translations()
#     reload_game_titles()
#     application.register_blueprint(cq9_api)
#     application.register_blueprint(template)
#     application.register_blueprint(user)
#     application.register_blueprint(wallet)
#     # application.register_blueprint(stage)
#
#     print('Socket: ' + socket.gethostname())
#     # print('SQLALCHEMY_DATABASE_URI: ' + socket.gethostname())
#     if socket.gethostname() == 'srv.gambits.vip':
#         if 'stage' in sys.argv[1:]:
#             application.run(host='0.0.0.0', port=5001)
#             # serve(application, host="0.0.0.0", port=5001)
#         else:
#             application.run(host='0.0.0.0')
#             # serve(application, host="0.0.0.0")
#     elif socket.gethostname() == 'The-Only-Real-MacBook-Pro.local':
#         application.debug = True
#         application.run(host='192.168.1.107')
#         # serve(application, host="192.168.1.107")
