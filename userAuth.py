# import xml.etree.ElementTree as xmlTree
#
# import random
# import requests
# import string
# import json
# import webbrowser
# # from database import proxies
#
#
# class UAT:
#     UA_payload = {
#         'game_url': '',
#         'uuid': 'x',  # assigned, should be uid
#         'transaction': {
#             'etransid': 'x',
#             'transid': 'x',
#             'datetime': 'x',
#         },
#         'player': {
#             'balance': '0.0',
#             'id': 'x',  # assigned by licensee, should be euid
#             'update': False,
#             'firstName': 'x',  # assigned
#             'lastName': 'x',  # assigned
#             'nickname': 'x',  # assigned
#             'country': 'x',  # assigned
#             'language': 'EN',  # assigned
#             'currency': 'CNY',  # assigned
#             'session': {
#                 'id': '111ssss3333rrrrr45555',  # assigned by licensee
#                 'ip': '192.168.0.1'  # assigned
#             }
#         },
#         'config': {
#             'brand': {
#                 'skin': '1'
#             },
#             'game': {
#                 # 'category': 'roulette',
#                 'interface': 'view1',
#                 'table': {
#                     'id': ''
#                 }
#             },
#             'channel': {
#                 'wrapped': False,
#                 'mobile': False,
#             },
#             'urls': {
#                 'cashier': 'http://www.RGam.ee',  # assigned by licensee
#                 'responsibleGaming': 'http://www.RGam.ee',  # assigned by licensee
#                 'lobby': 'http://www.lobb.ee',  # assigned by licensee
#                 'sessionTimeout': 'http://www.sesstm.ee'  # assigned by licensee
#             },
#             'freeGames': False
#         }
#     }
#     userdata = {
#         'emailaddress': 'x',
#         'screenname': 'x',
#         'countrycode': 'x',
#         'firstName': 'x',
#         'lastName': 'x',
#         'balance': '0.0',
#         'etransid': '###',
#         'transid': '###',
#         'datetime': '###',
#         'euid': 'x',
#         'uid': 'x',
#     }
#     url = 'https://diyft4.uat1.evo-test.com'
#     casino_id = 'diyft40000000001'
#     auth_key = 'test123'
#     cashier_payload = {
#         'cCode': 'xxx',
#         'euID': 'yaoza',
#         'ecID': 'diyft40000000001test123',
#         'eTransID': 'fake_eTransID',
#         'output': '1'
#     }
#
#     def __init__(self):
#         # self.UA_payload['config']['urls']['cashier'] = hostname
#         self.get_user_info()
#
#     def launch_game(self, game_id):
#         self.UA_payload['config']['game']['table']['id'] = game_id
#         ua_url = self.url + '/ua/v1/' + self.casino_id + '/' + self.auth_key
#         x = requests.post(ua_url, json=self.UA_payload)
#         x_json = json.loads(x.text)
#         if 'entry' in x_json:
#             webbrowser.open(self.url + x_json['entry'])
#         # elif x_json
#
#     def daily_report(self):
#         auth_payload = {'Authorization': 'Basic ZGl5ZnQ0MDAwMDAwMDAwMTp0ZXN0MTIz'}
#         x = requests.get(self.url + '/api/gamehistory/v1/casino/daily-report', headers=auth_payload, proxies=proxies)
#         return json.loads(x.text)['data']
#
#     def direct_game_launch(self):
#         auth_payload = {'Authorization': 'Basic ZGl5ZnQ0MDAwMDAwMDAwMTp0ZXN0MTIz'}
#         x = requests.get(self.url + '/api/lobby/v1/' + self.casino_id + '/state', headers=auth_payload, proxies=proxies)
#         return json.loads(x.text)
#
#     def mini_roulette(self):
#         self.UA_payload['config']['game']['table'] = {'id': 'pegck3qfanmqbgbh'}
#         ua_url = self.url + '/ua/v1/' + self.casino_id + '/' + self.auth_key
#         x = requests.post(ua_url, json=self.UA_payload, proxies=proxies)
#         # print("*******My URL", self.url + '/ua/v1/diyft40000000001/test123', sep="---->")
#         # print("*******My payload", self.UA_payload, sep="---->")
#         # print("*******My proxy", proxies, sep="---->")
#         # print("*******My x", x, sep="---->")
#         self.UA_payload['game_url'] = self.url + x.json()['entry']
#
#         self.UA_payload['config']['game']['table'] = ''
#         return
#
#     def game_stream(self):
#         auth_payload = {'Authorization': 'Basic ZGl5ZnQ0MDAwMDAwMDAwMTp0ZXN0MTIz'}
#         x = requests.get(self.url + '/api/streaming/game/v1/', stream=True, headers=auth_payload, proxies=proxies)
#         with open('game_stream.txt', 'wb') as f:
#             for chunk in x.iter_content(chunk_size=1024):
#                 if b'message' in chunk:
#                     f.write(chunk)
#                     break
#
#         return json.loads(chunk.decode('ascii'))['data']
#
#     def casino_cmd(self, cmd, amount=0):
#         if cmd == 'GUI':
#             self.cashier_payload.update({'cCode': cmd})
#         else:
#             self.cashier_payload.update({'cCode': cmd, 'amount': amount})
#
#         x = requests.get(self.url + '/api/ecashier', params=self.cashier_payload, proxies=proxies)
#         return xmlTree.fromstring(x.text)
#
#     def set_lang_game(self, form):
#         self.UA_payload['player']['language'] = form.language.data
#         self.UA_payload['config']['game']['category'] = form.game.data
#
#     def get_user_info(self):
#         gui = self.casino_cmd('GUI')
#         self.UA_payload['player']['firstName'] = gui[1].text
#         self.UA_payload['player']['lastName'] = gui[2].text
#         self.UA_payload['player']['nickname'] = gui[3].text
#         self.UA_payload['player']['country'] = gui[4].text
#         self.UA_payload['player']['update'] = False
#         self.UA_payload['uuid'] = gui[5].text
#         self.UA_payload['player']['id'] = gui[6].text
#
#     def get_user_balance(self):
#         rwa = self.casino_cmd('RWA')
#         self.UA_payload['player']['balance'] = rwa[3].text
#
#     def update_user_info(self, form):
#         self.UA_payload['player']['firstName'] = form.firstName.data
#         self.UA_payload['player']['lastName'] = form.lastName.data
#         self.UA_payload['player']['nickname'] = form.nickname.data
#         self.UA_payload['player']['country'] = form.country.data
#         self.UA_payload['player']['language'] = form.language.data
#         self.UA_payload['player']['update'] = True
#         self.UA_payload['player']['session']['id'] = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
#         self.UA_payload['config']['game']['category'] = form.game.data
#         self.process_UA2()
#
#     def ft_add(self, amount):
#         ecr = self.casino_cmd('ECR', amount)
#         self.UA_payload['player']['balance'] = ecr[0].text
#         self.UA_payload['transaction']['etransid'] = ecr[1].text
#         self.UA_payload['transaction']['transid'] = ecr[2].text
#         self.UA_payload['transaction']['datetime'] = ecr[3].text
#         self.userdata.update({
#             'balance': ecr[0].text,
#             'etransid': ecr[1].text,
#             'transid': ecr[2].text,
#             'datetime': ecr[3].text
#         })
#
#     def ft_subtract(self, amount):
#         ecr = self.casino_cmd('EDB', amount)
#         self.UA_payload['player']['balance'] = ecr[0].text
#         self.UA_payload['transaction']['etransid'] = ecr[1].text
#         self.UA_payload['transaction']['transid'] = ecr[2].text
#         self.UA_payload['transaction']['datetime'] = ecr[3].text
#         self.userdata.update({
#             'balance': ecr[0].text,
#             'etransid': ecr[1].text,
#             'transid': ecr[2].text,
#             'datetime': ecr[3].text
#         })
#
#     def process_UA2(self):
#         ua_url = self.url + '/ua/v1/' + self.casino_id + '/' + self.auth_key
#         x = requests.post(ua_url, json=self.UA_payload, proxies=proxies)
#
#         self.UA_payload['game_url'] = self.url + x.json()['entry']
#         return self.UA_payload['game_url']
#
#     def process_ow_check(self):
#         ua_url = self.url + '/ua/v1/' + self.casino_id + '/' + self.auth_key
#         x = requests.post(ua_url, json=self.UA_payload, proxies=proxies)
#         link = self.url + x.json()['entry']
#         print(link)
#         return link
