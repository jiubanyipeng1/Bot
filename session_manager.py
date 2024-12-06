# -*- coding: utf-8 -*-
import logging
from logging.handlers import TimedRotatingFileHandler
from wcferry import Wcf, WxMsg
from cache_manager import CacheManager
from session_handler import SessionHandler


class SessionManager:
    """ 会话管理 """

    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.config = cache_manager.config
        self.session_handler = SessionHandler(cache_manager)

        self.LOG = logging.getLogger("cache_manager")
        log_file = self.config['log'] + "/cache_manager.log"  # 日志文件名称
        handler = TimedRotatingFileHandler(log_file, when="D", interval=1, backupCount=7)
        self.LOG.addHandler(handler)

    def wx_receive_message(self, msg: WxMsg, wcf: Wcf):
        """ 微信会话管理 """

        if msg.from_self():
            return '自己发的！不进行处理！'
        if msg.type != 1 or msg.type != 3:
            return '不是文本或图片消息！不进行处理！'
        # 0  朋友圈消息 1 文本信息 3 图片信息 34 语音消息 37 好友请求 40 PossibleFriend 42 共享名片 43 视频消息
        # 47 动画表情 48 定位 位置 49 共享实时位置、文件、转账、链接、群邀请 50 VOIP MSG 51 微信初始化消息
        # 52 语音/视频通话通知 53 语音/视频通话邀请 62 小视频 999 SYS NOTICE 10000 红包、系统消息 10002 撤回消息
        # 1048625 搜狗表情 16777265 链接 436207665 微信红包 536936497 红包封面 754974769 视频号视频
        # 771751985 视频号名片 822083633 引用消息 922746929 拍一拍 973078577 视频号直播 974127153 商品链接
        # 975175729 视频号直播 1040187441 音乐链接 1090519089 文件case

        # 是否启用私有
        if self.config['wx'].get('private_disabled', False):
            if msg.sender not in self.config['wx'].get('groups_disabled', []) or msg.sender not in \
                    self.config['wx'].get('bot_admin_user', {'wx': []}).get('wx', []):
                self.LOG.info(f"{msg.sender}：账号不在私有名单内")
                return  '验证失败，不在允许名单或者不是管理员'

        keys = ['wx', msg.sender]  # 获取值列表的初始化
        # 处理添加信息键
        if msg.from_group():
            # 是否启用群名单验证
            if self.config['wx'].get('groups_disabled', False):
                if msg.roomid not in self.config['wx'].get('groups_enable', []):
                    self.LOG.info(f"{msg.roomid}：群不在名单内")
                    return  # 不在群名单内
            # 是否被 @，如果是 @直接转发，能被@的一般只有文本信息
            if msg.is_at(self.cache_manager.user_data('wxid')):
                # 验证是否第一次进行请求并初始化
                self.is_session('wx', msg.sender, True, msg.roomid)
                self.session_handler.wx_process_message(msg, wcf)  # 信息转发
                return '群@信息，处理中...'
            keys.append('group')
            keys.append(msg.roomid)
        else:  # 私人
            # 验证是否第一次进行请求
            self.is_session('wx', msg.sender)
            keys.append('private')

        # 验证是否继续信息
        keys.append('continue')
        # 普通群信息 or 私人信息
        if self.cache_manager.get_nested_value(keys):  # 验证是否存在继续对话
            self.session_handler.wx_process_message(msg, wcf, is_continue=True)  # 信息转发
            return '继续对话,处理中...'
        else:
            # 是否私人信息，私人则转发
            if not msg.from_group():
                self.session_handler.wx_process_message(msg, wcf)
                return '私人信息，处理中...'
        return '流程结束！'


    def qq_receive_message(self, msg):
        """ QQ会话管理 """
        pass

    def web_receive_message(self, msg):
        """ web会话管理 """
        pass

    def is_session(self, platform, user, is_group=False, group_id='', is_init=True) -> bool:
        """ 是否存在会话缓存，默认不存在会话缓存，自动会生成缓存，返回 False
        :param platform: 平台
        :param user: 账号
        :param is_group: 是否公共
        :param group_id: 公共id
        :param is_init: 是否初始化缓存
        :return: 该账号的缓存数据
        """
        keys = [platform, user]
        data = {
            'current': 0,  # 当前运行第几次
            'continue': False,  # 是否继续
            'plugin': '',  # 指令插件
            'function': '',  # 指令功能
            'text_content': '',  # 本次文本内容
            'config': {},  # 对接AIP的参数和配置
            'text_list': []  # 文本对话历史信息
        }
        if is_group:
            keys.append('group')
            keys.append(group_id)
        else:
            keys.append('private')

        if self.cache_manager.get_nested_value(keys):
            return True

        if is_init:
            self.cache_manager.update_nested_value(keys, data)
        return False
