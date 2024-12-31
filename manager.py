# -*- coding: utf-8 -*-
import json
import logging
import os
from logging.handlers import TimedRotatingFileHandler
import websocket
import subprocess
import platform
import time
import threading
import function
from weixin_bot import WeiXinBot
from qq_bot import QQBot
from web_bot import WEBBot
from cache_manager import CacheManager
from session_manager import SessionManager


class Manager:
    """ 运行管理实例 微信、QQ、web的启动管理 """
    def __init__(self, config: dict) -> None:
        self.config = config
        self.cache_manager = CacheManager(config)  # 全局的缓存管理 初始化
        self.session_manager = SessionManager(self.cache_manager)  # 全局的会话管理 初始化

        self.LOG = logging.getLogger("manager")
        log_file = function.filepath(f'{self.config["log"]}/manager.log')  # 日志文件名称
        handler = TimedRotatingFileHandler(log_file, when="D", interval=1, backupCount=7)
        self.LOG.addHandler(handler)

        self.QQBot = None  # qqbot实例
        self.napcat_proc = None  # napcat进程
        self.WeiXinBot = None  # weixin bot实例
        self.WEBBot = None # web bot实例

    def run_bots(self):
        # 创建线程
        web_bot_thread = threading.Thread(target=self.start_web_bot)
        qq_bot_thread = threading.Thread(target=self.start_qq_bot)
        wx_bot_thread = threading.Thread(target=self.start_wx_bot)

        # 启动线程
        web_bot_thread.start()
        qq_bot_thread.start()
        wx_bot_thread.start()

        # 等待两个线程都执行完毕
        web_bot_thread.join()
        qq_bot_thread.join()
        wx_bot_thread.join()
    def start_wx_bot(self):
        """启动微信 bot """
        if self.config.get('weixin_bot', False):
            if self.cache_manager.is_wx_config():
                self.WeiXinBot = WeiXinBot(self.config, self.cache_manager, self.session_manager)
            else:
                self.LOG.error('微信模块配置错误，请检查！')
        else:
            self.LOG.info('微信 未设置启动！')
        return

    def start_qq_bot(self):
        """ 启动qq bot """
        if self.config.get('qq_bot', False):
            if self.cache_manager.is_qq_config():
                qq_bot = self.config['qq']
                if qq_bot['number'] == '2956098898':
                    self.LOG.error('QQ模块配置错误，请填写你自己的QQ账号！')
                    return 'QQ模块配置错误，请填写你自己的QQ账号！'

                # 配置文件的相对地址
                napcat_config_path = function.filepath(f'./napcat.29927.onekey/versions/9.9.16-29927/resources/app/napcat/config/onebot11_{qq_bot["number"].strip()}.json')

                if not os.path.exists(os.path.dirname(napcat_config_path)):
                    self.LOG.error(f'napcat 文件路径不存在！请核查！\n {napcat_config_path}')
                    return 'napcat 文件路径不存在！'
                # 每次运行都重新写入更新
                with open(napcat_config_path,'w',encoding='utf-8') as f:
                    data  = {"network": {"httpServers": [],"httpClients": [],
                            "websocketServers": [{
                                    "name": "bot","enable": True,"host": "127.0.0.1", "port": qq_bot['port'],
                                    "messagePostFormat": "array","reportSelfMessage": False,
                                    "token": qq_bot['token'], "enableForcePushEvent": False,"debug": False,
                                    "heartInterval": 3000,"type": "WebSocket 服务器"
                            }],"websocketClients": []},
                        "musicSignUrl": "","enableLocalFile2Url": False,"parseMultMsg": True
                    }
                    f.write(json.dumps(data, ensure_ascii=False, indent=4))
                try:
                    status = self.is_napcat()
                    if status['status'] == 'ok':
                        self.LOG.info('qq bot 检查完成！开始启动')
                        self.QQBot = QQBot(self.config, self.cache_manager, self.session_manager)
                    elif status['status'] == 'retry':
                        self.LOG.info('napcat 插件 状态异常，10 秒后 重试！')
                        time.sleep(10)  # 等待 10 秒
                        self.start_qq_bot()  # 重试
                    elif status['status'] == 'error':
                        self.LOG.error('napcat 插件 错误，请检查！')
                        return 'napcat 插件 错误，请检查！'
                except KeyboardInterrupt:
                    # self.shutdown()
                    self.LOG.info('用户已手动关闭 QQ bot 程序！')
                    return '关闭机器人'
                except Exception as e:
                    self.LOG.error(f'qq bot 启动失败！{str(e)}')
                    return str(e)
            else:
                self.LOG.error('qq模块配置错误，请检查！')
                return 'qq模块配置错误，请检查！'
        else:
            self.LOG.info('qq bot 未启用！')
        return

    def start_web_bot(self):
        """ 启动 web_bot 插件程序。"""
        if self.config.get('web_bot', False):
            if self.cache_manager.is_web_config():
                self.WEBBot = WEBBot(self.config, self.cache_manager, self.session_manager)
            else:
                self.LOG.error('web模块配置错误，请检查！')
        else:
            self.LOG.info('web 未设置启动！')
        return

    def start_napcat(self):
        """ 启动 napcat 插件程序。启动成功返回 True，否则返回 False"""
        plugin_path = function.filepath("./napcat.29927.onekey/NapCatWinBootMain.exe")
        if not os.path.isfile(plugin_path):
            self.LOG.error(f"可执行文件未找到: {plugin_path}")
            return False

        try:
            if platform.system() == "Windows":
                cmd = f'cmd.exe /c "chcp 65001 >nul & cd {function.filepath("./")} &"{plugin_path}" --qq {self.config["qq"]["number"]}"'
                proc = subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,  # 创建新的控制台窗口
                )
                self.LOG.info(f"对接QQ插件程序NapCat已启动，PID: {proc.pid}")
                self.napcat_proc = proc  # 设置进程对象
                return True

            else:
                self.LOG.error("当前操作系统不支持")
                return False

        except Exception as e:
            self.LOG.error(f"启动 napcat 插件时出错: {e}")
            return False

    def is_napcat_running(self):
        """ 检查 napcat 进程是否正在运行 """
        if self.napcat_proc is None:
            self.LOG.info("napcat 进程尚未启动")
            return False

        return_code = self.napcat_proc.poll()
        if return_code is None:
            self.LOG.info("napcat 进程正在运行")
            return True
        else:
            self.LOG.warning(f"napcat 进程已结束，退出码为: {return_code}")
            return False

    def is_napcat(self):
        """ 检查 napcat 插件状态 """
        try:
            ws = websocket.create_connection(
                f"ws://127.0.0.1:{self.config['qq']['port']}/?access_token={self.config['qq']['token']}")
            self.LOG.info("成功连接到WebSocket服务器，验证QQ登录信息中...")

            message = json.dumps({"action": "get_login_info", "params": {}})
            ws.send(message)
            self.LOG.info(ws.recv())  # napcat问题，第一次交互会返回信息，下面这个信息才是我们需要的！
            response = ws.recv()
            response_data = json.loads(response)

            if response_data.get('status') == 'ok':
                # 注意，这里仅验证是否登录，没有验证是否在线
                self.LOG.info("QQ登录信息验证成功！")
                ws.close()
                return {'status': 'ok'}
            else:
                self.LOG.info("QQ登录信息验证失败！可能是未进行登录！")
                ws.close()
                return {'status': 'retry'}

        except (websocket._exceptions.WebSocketBadStatusException, ConnectionRefusedError) as e:
            self.LOG.error(f"无法连接到WebSocket服务器：{str(e)}")
            if not self.is_napcat_running():
                self.LOG.error("尝试启动 napcat 进程...")
                if self.start_napcat():
                    return {'status': 'retry'}
                else:
                    return {'status': 'error'}
            else:
                return {'status': 'retry'}

        except Exception as e:
            self.LOG.error(f"发生错误: {str(e)}")
            return {'status': 'error'}

    def shutdown(self):
        """ 关闭机器人 """
        try:
            self.LOG.info("正在关闭机器人...")
            self.WeiXinBot.stop()
            self.QQBot.stop()
            self.napcat_proc.terminate()
            try:  # 等待最多5秒让进程结束
                self.napcat_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.LOG.warning("napcat 进程没有及时终止，被迫杀死。")
                self.napcat_proc.kill()
                self.napcat_proc.wait()
            # self.web_bot.stop()
            self.LOG.info("机器人已关闭。")
        except Exception as e:
            self.LOG.error(f"关闭机器人时发生错误: {str(e)}")
