# -*- coding: utf-8 -*-
import logging
from logging.handlers import TimedRotatingFileHandler
import function


class CacheManager:
    """数据缓存管理"""

    def __init__(self, config):
        self.user_data = {'wx': {}, 'qq': {}, 'web': {}}  # 用户缓存数据初始化
        self.config = config  # 全局的 配置文件
        self.session = {}   # 会话 缓存数据初始化，暂时没有使用
        self.LOG = logging.getLogger("cache_manager")

        log_file = function.filepath(f'{self.config["log"]}/cache_manager.log')  # 日志文件名称
        handler = TimedRotatingFileHandler(log_file, when="D", interval=1, backupCount=7)
        self.LOG.addHandler(handler)

    def get_config(self):
        """ 获取 全部配置文件"""
        return self.config

    def get_session(self):
        """ 获取会话缓存 """
        return self.session

    def get_user_all(self):
        """ 获取全部用户缓存数据
        {
        '平台':{'用户账号':{'private':{}}}
        'wx'：{'用户账号':{'group':{'公共id':{}}}}
        }
        """

        return self.user_data

    def get_user(self, key):
        """用户数据 获取缓存 用户缓存"""
        return self.user_data.get(key, None)

    def get_nested_value(self, keys):
        """用户数据 获取嵌套字典中的值 """
        current = self.user_data
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        return current

    def delete_user(self, key):
        """用户数据 删除缓存 用户缓存 """
        if key in self.user_data:
            del self.user_data[key]

    def set_user(self, key, value):
        """用户数据 设置缓存 用户缓存 一般用于初始化"""
        self.user_data[key] = value

    def update_nested_value(self, keys, new_value):
        """用户数据 更新嵌套字典中的值，如果路径中不存在的键则创建它们"""
        current = self.user_data
        for k in keys[:-1]:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                current[k] = {}
                current = current[k]
        if isinstance(current, dict):
            current[keys[-1]] = new_value
            self.LOG.info(f"更新缓存: {' -> '.join(keys)} ")  # Debug output
        else:
            self.LOG.error(f"更新缓存失败！ {' -> '.join(keys[:-1])} ")

    def is_wx_config(self):
        """ 验证微信配置文件是否存在异常 """
        try:
            wx_config = self.config["wx"]
            mes = 'port 不是int类型'
            if isinstance(wx_config['port'],int) :
                mes = 'max_timeout 不是int类型'
                if isinstance(wx_config['max_timeout'],int):
                    mes = 'private_disabled 不是 bool 类型'
                    if isinstance(wx_config['private_disabled'],bool):
                        mes = 'permit_group 不是 list 类型'
                        if isinstance(wx_config['permit_group'],list):
                            mes = 'groups_disabled 不是 bool 类型'
                            if isinstance(wx_config['groups_disabled'],bool):
                                mes = 'groups_enable 不是 list 类型'
                                if isinstance(wx_config['groups_enable'],list):
                                    mes = 'log_chat 不是 bool 类型'
                                    if isinstance(wx_config['log_chat'],bool):
                                        mes = 'log_chat_path 不是 str 类型'
                                        if isinstance(wx_config['log_chat_path'], str):
                                            mes = 'api 不是 dict 类型'
                                            if isinstance(wx_config['api'],dict):
                                                return True
            self.LOG.error(f'微信配置错误：{mes}')
            return None
        except Exception as e:
            self.LOG.error(f'微信配置错误：{e}')
            return None

    def is_qq_config(self):
        """ 验证QQ配置文件是否存在异常 """
        mes = ''
        try:
            qq_config = self.config["qq"]
            mes = 'number 不是 str 类型'
            if isinstance(qq_config['number'], str):
                mes = 'number  QQ账号可能为假。仅允许为整数，为了防止bug暂时不允许除整数以外的类型'
                if isinstance(int(qq_config['number']), int):
                    mes = 'port 不是int类型'
                    if isinstance(qq_config['port'], int):
                        mes = 'token 不是str类型'
                        if isinstance(qq_config['token'], str):
                            mes = 'timeout_clear 不是 int 类型'
                            if isinstance(qq_config['timeout_clear'], int):
                                mes = 'group_disabled 不是 bool 类型'
                                if isinstance(qq_config['group_disabled'], bool):
                                    mes = 'groups_enable 不是 list 类型'
                                    if isinstance(qq_config['groups_enable'], list):
                                        mes = 'private_disabled 不是 bool 类型'
                                        if isinstance(qq_config['private_disabled'], bool):
                                            mes = 'permit_group 不是 list 类型'
                                            if isinstance(qq_config['permit_group'], list):
                                                mes = 'log_chat 不是 bool 类型'
                                                if isinstance(qq_config['log_chat'], bool):
                                                    mes = 'log_chat_path 不是 str 类型'
                                                    if isinstance(qq_config['log_chat_path'], str):
                                                        mes = 'api 不是 dict 类型'
                                                        if isinstance(qq_config['api'], dict):
                                                            return True
            self.LOG.error(f'QQ配置错误：{mes}')
            return None
        except Exception as e:
            self.LOG.error(f'QQ配置错误：{e} \n {mes}')
            return None