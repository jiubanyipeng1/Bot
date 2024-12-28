# -*- coding: utf-8 -*-
import types
from datetime import datetime, timedelta
import logging
from logging.handlers import TimedRotatingFileHandler
import secrets
from flask import Flask, session, request, redirect, url_for, flash, render_template, jsonify, Response, stream_with_context
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from concurrent.futures import ThreadPoolExecutor
import asyncio
import functools

import function

class User(UserMixin):
    """自定义User类，继承自UserMixin以获得默认实现的方法"""
    def __init__(self, username, auto_login=False):
        self.id = username
        self.can_auto_login = auto_login

def generate_secure_token(length=32):
    return secrets.token_hex(length)

class WEBBot:
    def __init__(self, config, cache_manager, session_manager) -> None:
        self.executor = ThreadPoolExecutor(max_workers=10)

        self.config = config
        self.cache_manager = cache_manager
        self.session_manager = session_manager

        # 配置文件的用户账号密码
        self.users_db = self.config.get('web', {"user_data": {}})['user_data']
        self.users_admin = self.config.get('admin_user', {'web': {}})['web']  # 管理员账号 列表

        self.app = Flask('web_bot')
        self.app.secret_key = self.config['web'].get('secret_key', "JiuBanYiPeng.20241222")
        self.app.permanent_session_lifetime = timedelta(days=1)  # 设置session过期时间

        # 初始化LoginManager并设置未登录时重定向到登录页面
        self.login_manager = LoginManager()
        self.login_manager.login_message = "请先登录以访问该页面。"
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = 'login'

        self.LOG = logging.getLogger("web_bot")
        log_file = function.filepath(f'{self.config["log"]}/web_bot.log')  # 日志文件名称
        handler = TimedRotatingFileHandler(log_file, when="D", interval=1, backupCount=7)
        self.LOG.addHandler(handler)

        # 设置加载用户的回调函数
        @self.login_manager.user_loader
        def load_user(user_id):
            user_data = self.users_db.get(user_id)
            if user_data:
                return User(user_id)
            return None

        self._add_routes()
        self.LOG.info(f'web_bot启动')
        self.app.run(debug=self.config.get('debug', False), port=self.config['web']['port'], host='127.0.0.1')

    def _add_routes(self):
        # 定义路由和视图函数
        @self.app.route('/', methods=['GET', 'POST'])
        @login_required
        def index():
            """处理主页请求"""
            if request.method == 'POST':
                data = request.get_json()
                if data is None:
                    return jsonify({'code': False, 'error': '没有数据'}), 400
                return self.process_message(data)
            return render_template('home.html')

        @self.app.errorhandler(404)
        def page_not_found(error):
            # 错误处理函数
            return render_template('404.html', error=error), 404

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """处理用户登录请求"""
            if current_user.is_authenticated:
                return redirect(url_for('index'))

            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                client_ip = next((ip for ip in request.headers.get('X-Forwarded-For', '').split(',') if ip.strip()),
                                 request.remote_addr)
                self.LOG.info(f"用户：{username} 尝试登录. IP:{client_ip}")
                # 这里应该要添加验证 在短时间内禁用该ip地址访问和锁定该用户

                if not username or not password:
                    flash('请输入用户名和密码！')
                    return render_template('login.html')

                user_data = self.users_db.get(username, False)

                if user_data and user_data == password:
                    user_obj = User(username)
                    login_user(user_obj)
                    self.LOG.info(f"用户：{username} 登录成功. IP:{client_ip}")
                    session['last_activity'] = datetime.now().timestamp()
                    return redirect(url_for('index'))
                else:
                    flash('账号或密码不存在！')
            else:
                # 根据配置文件决定是否自动登录 没有登录且不是中index视图函数过来的
                if not request.args.get('logout', False):
                    flash('您已成功注销！')
                    if self.config['web']['auto_login']:
                        username = f'group-{generate_secure_token(16)}'
                        self.users_db[username] = username
                        user = User(username, True)
                        self.users_db[username] = user  # 将新用户添加到模拟数据库
                        self.LOG.info(f"自动登录 用户：{username}")
                        login_user(user, remember=True)
                        session['last_activity'] = datetime.now().timestamp()
                        return redirect(url_for('index'))
            return render_template('login.html')

        @self.app.route('/logout', methods=['POST'])
        @login_required
        def logout():
            """处理用户登出请求"""
            logout_user()
            return redirect(url_for('login',logout=True))

        @self.app.before_request
        def before_request():
            session.permanent = True
            if current_user.is_authenticated:
                session.modified = True
                session['last_activity'] = datetime.now().timestamp()

            # 检查是否有超过24小时未活动的用户并登出
            last_activity = session.get('last_activity')
            if last_activity and datetime.now().timestamp() - last_activity > 86400:
                logout_user()

    def process_message(self, data):
        """ 处理消息 """
        # {'messages': [{'role': 'user', 'content': '你好'}, {'role': 'user', 'content': '我好'}],'instruct': '文本回答',session_id:'1234567890'}
        if not data:
            return jsonify({"code": False, "mes": "无效的 JSON 数据"}), 400
        async def process():
            session_id = data.get('session_id', False)
            if not session_id:
                session_id = generate_secure_token(16)
            if data.get('instruct') == '文本回答':
                if self.config['web']['api']['chat'] == 'default':
                    name_api = self.config['chat_api']
                else:
                    name_api = self.config['web']['api']['chat']
                config_api = self.config['api'].get(name_api, False)
                if config_api:
                    data_api = await function.start_chat(data['messages'], name_api, config_api)
                    data_api['session_id'] = session_id
                    return data_api
            else:
                return {"code": False, "mes": "未找到对应的API"}
        result = self._run_in_thread(process).result()
        if isinstance(result['data'], types.GeneratorType):
            return Response(stream_with_context(result["data"]), content_type='text/plain')
        else:
            return jsonify(result), 200

    def _run_in_thread(self, async_func):
        """ 辅助函数，用于在线程池中运行异步函数 """
        @functools.wraps(async_func)
        def wrapper():
            # 确保每个线程有自己的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(async_func())
            finally:
                loop.close()
            return result

        future = self.executor.submit(wrapper)
        return future
