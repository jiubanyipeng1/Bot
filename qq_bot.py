# coding:utf-8
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import websocket
import time
from threading import Thread
import function

class QQBot:
    """ QQ机器人运行 """
    def __init__(self, config, cache_manager, session_manager) -> None:
        self.config = config
        self.cache_manager = cache_manager
        self.session_manager = session_manager

        self.LOG = logging.getLogger("qq_bot")
        log_file = function.filepath(f'{self.config["log"]}/qq_bot.log')  # 日志文件名称
        handler = TimedRotatingFileHandler(log_file, when="D", interval=1, backupCount=7)
        self.LOG.addHandler(handler)
        self.cache_manager.set_user('qqid', self.config['qq']['number'])
        websocket.enableTrace(self.config.get('debug', False))  # 启用或禁用WebSocket的调试信息，会引起web未启用，应该是被堵塞了，暂未解决
        self.ws = None
        self._start_ws()
        self.reconnect_interval = 5  # 设置重连间隔时间（秒）

    def start(self):
        try:
            self._start_ws()
        except KeyboardInterrupt:
            self.LOG.info("\n正在关闭WebSocket连接，请稍等...")
            self.close_ws()
            self.LOG.info("WebSocket连接已关闭。")

    def _start_ws(self):
        self.ws = websocket.WebSocketApp(
            f"ws://127.0.0.1:{self.config['qq']['port']}/?access_token={self.config['qq']['token']}",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            # on_ping = lambda ws, msg: self.LOG.info(f"Ping 收到: {msg}"),
            # on_pong = lambda ws, msg: self.LOG.info(f"Pong 收到: {msg}")
        )
        self.ws.on_open = self.on_open
        #self.ws.run_forever(ping_interval=30, ping_timeout=10)

        self.reconnect_interval = 5  # 设置重连间隔时间（秒）
        while True:
            try:
                self.ws.run_forever()
            except Exception as e:
                self.LOG.error(f"WebSocket 运行时出错: {e}")
            finally:
                self.LOG.warning("WebSocket 连接已断开，将在 {} 秒后尝试重新连接...".format(self.reconnect_interval))
                time.sleep(self.reconnect_interval)

    def on_open(self,*args):
        self.LOG.info('WebSocket 连接成功建立.')

    def close_ws(self,*args):
        if self.ws:
            self.ws.close()

    def on_message(self, ws, message):
        """napcat 信息接收并转发 """
        mes = json.loads(message)
        def inner_process_msg():
            self.session_manager.qq_receive_message(mes, ws)

        Thread(target=inner_process_msg, name="GetMessage", daemon=True).start()

    def on_error(self, ws, error):
        self.LOG.error(f"WebSocket 错误: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.LOG.warning(f"WebSocket 关闭: 状态码 {close_status_code}, 消息 {close_msg}")


    def stop(self) -> None:
        """ 关闭qq bot 相关"""
        try:
            self.LOG.info("正在关闭与 napcat 的WebSocket连接，请稍等...")
            self.close_ws()
            self.LOG.info("与 napcat 的WebSocket连接已关闭。")
        except Exception as e:
            self.LOG.error(f"关闭 napcat 的WebSocket连接 报错: {e}")


