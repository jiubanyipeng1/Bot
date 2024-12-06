# coding:utf-8

from flask import Flask, render_template, request, redirect, url_for, make_response

from random import randint, choice

from asyncio import run as asyncio_run

from json import loads as json_loads

from os import makedirs as os_makedirs

from time import sleep

import function

from gptapi import TongYiQianWen, XunFeiApi, OpenAiApi

app = Flask(__name__)

class WBEBot:

""" Web机器人运行 """

def __init__(self, config) -> None:

self.config = config

def char_processor(apiname, api, message,username):

mes = function.chat_run_api(message,apiname,api)

if mes['code']:

# 这里是写入日志

if bot_config['bot_chat_log']:

mes_log = f"[user:{message[-1]}]

[assistant:{mes['mes']}]

"

print(asyncio_run(function.write_log('/web/'+username, mes_log)))

return {"code": True, "mes": mes['mes']}

else:

return {"code": False, "mes": mes['mes']}

def random_number():

""" 生成凭证

:return: MXY0zjgU-K8C0AO72-W5RGEJeq-9387k9cx, xlVOq68r5w1s56uXWN759b8N0kx0l5gy

"""

number,token = '', ''

for i in range(4):

for ii in range(8):

number += choice([chr(randint(48,57)), chr(randint(65,90)), chr(randint(97,122))])

token += choice([chr(randint(48,57)), chr(randint(65,90)), chr(randint(97,122))])

if i < 3:

number += '-'

return number, token

class WebProcess:

def __init__(self, config):

""" web处理 """

self.config = config

self.user_data = config['web_config']['user_data']

self.key_data = {} # 存储用户登录成功的凭证

self.enable_login = config['web_config']['login'] # 用户账号登录验证

def home(self):

""" 用户首页视图 """

user_cookie = request.cookies

if user_cookie.get('username', False) and user_cookie['username'] in self.key_data:

# cookie 检查

# if user_cookie['token'] != self.key_data[user_cookie['username']]['token']:

# return render_template('login.html', error='当前的cookie不匹配')

if request.method == 'POST':

data = json_loads(request.data.decode('utf-8'))

if data['instruct'] == '文本回答':

return self.generate_text(data['messages'])

if data['instruct'] == '文本生成图像':

# 还需要 prompt

return self.generate_image(data)

return {'code': False, 'mes': '其他功能，暂时为开发', 'instruct': '文本回答'}

return render_template('home.html')

else:

return redirect(url_for('login'))

def login(self):

""" 用户登录视图和登录处理 """

if self.enable_login:

if request.method == 'POST':

# 获取用户名和密码

username = request.form['username']

password = request.form['password']

if username in self.user_data and password == self.user_data[username]:

session_id, token = random_number()

new_key_data = {'token': token, 'session_id': session_id}

self.key_data[username] = new_key_data

response = make_response(redirect(url_for('home')))

response.set_cookie('username', str(username))

response.set_cookie('token', token)

response.set_cookie('session_id', session_id)

return response

else:

return render_template('login.html', error='账号或密码有误！')

else:

session_id, token = random_number()

new_key_data = {'token': token, 'session_id': session_id}

self.key_data[session_id] = new_key_data

response = make_response(redirect(url_for('home')))

response.set_cookie('username', str(session_id))

response.set_cookie('token', token)

response.set_cookie('session_id', session_id)

return response

return render_template('login.html')

def generate_text(self, prompt):

""" GPT 文本回答 """

if self.config['chat_api'] == 'chat_tyqw':

return TongYiQianWen.generate_text(prompt, self.config['chat_tyqw'])

if self.config['chat_api'] == 'chat_xunfei':

return XunFeiApi.generate_text(prompt, self.config['chat_xunfei'])

if self.config['chat_api'] == 'chat_openai':

return OpenAiApi.generate_text(prompt, self.config['chat_openai'])

return {'code': False, 'mes': '错误，文本回答功能配置有误！可能是 chat_api 配置的 名称 与主配置键不匹配'}

def generate_image(self, data):

""" GPT 文本生成图像 """

config = self.config['text_to_image_tywx']

config.update(data)

if self.config['chat_api'] == 'chat_tyqw':

return TongYiQianWen.generate_image(config, 'text_to_image')

def generate_plugin(self, data):

""" GPT 插件功能 """

def generate_ocr(self, data):

""" GPT 图片识别 """

if __name__ == '__main__':

try:

os_makedirs('BotLog/web', exist_ok=True)

with open('setting_config.json', 'r', encoding='utf-8') as f:

bot_config = json_loads(f.read())

app.secret_key = random_number()[0] # 随机生成 加密session数据密钥，为了方便不进行固定

web_process_instance = WebProcess(bot_config)

app.add_url_rule('/', view_func=web_process_instance.home, methods=['GET', 'POST'])

app.add_url_rule('/home', view_func=web_process_instance.home, methods=['GET', 'POST'])

app.add_url_rule('/login', view_func=web_process_instance.login, methods=['GET', 'POST'])

app.run(host='0.0.0.0', debug=True, port=bot_config['web_config']['port'])

except FileNotFoundError:

function.get_setting_config() # 创建配置文件

except Exception as e:

print('错误，请检查，以下是报错信息：

', e, '

退出...')

sleep(5)