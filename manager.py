# -*- coding: utf-8 -*-
import logging

from weixin_bot import WeiXinBot
from qq_bot import QQBot
from web_bot import WBEBot
from cache_manager import CacheManager
from session_manager import SessionManager
from logging.handlers import TimedRotatingFileHandler


class Manager:
    """ 运行管理实例
    微信、QQ、web的启动管理
    后面需要检查配置文件
    """
    def __init__(self, config: dict) -> None:
        self.config = config
        self.cache_manager = CacheManager(config)  # 全局的缓存管理 初始化
        self.session_manager = SessionManager(self.cache_manager)  # 全局的会话管理 初始化

        self.LOG = logging.getLogger("manager")
        log_file = self.config['log'] + "/manager.log"  # 日志文件名称
        handler = TimedRotatingFileHandler(log_file, when="D", interval=1, backupCount=7)
        self.LOG.addHandler(handler)

        if self.config.get('weixin_bot', False):
            if self.cache_manager.is_wx_config():
                self.WeiXinBot = WeiXinBot(self.config, self.cache_manager, self.session_manager)
                self.WeiXinBot.enable_receiving_msg()  # 启动微信消息接收
            else:
                self.LOG.error('微信模块配置错误，请检查！')

        # if config.get('qq_bot', False):
        #     self.QQBot = QQBot(self.cache_manager, self.session_manager)
        #
        # if config.get('web_bot', False):
        #     self.WBEBot = WBEBot(self.cache_manager, self.session_manager)
