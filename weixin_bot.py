# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import re
import logging
from queue import Empty
from threading import Thread
from logging.handlers import TimedRotatingFileHandler

from wcferry.client import Wcf
from wcferry.wxmsg import WxMsg


class WeiXinBot:
    """微信机器人"""
    def __init__(self, config, cache_manager, session_manager) -> None:
        self.config = config
        self.wcf = Wcf(port=config['wx']['port'])
        self.wxid = self.wcf.get_self_wxid()   # 获取机器人的微信id
        self.allContacts = self.get_all_contacts()  # 获取机器人的微信联系人（包括好友、公众号、服务号、群成员……）
        self.cache_manager = cache_manager
        self.cache_manager.set_user('wxid', self.wxid)
        self.session_manager = session_manager

        self.LOG = logging.getLogger("weixin_bot")
        log_file = self.config['log'] + "/weixin_bot.log"  # 日志文件名称
        handler = TimedRotatingFileHandler(log_file, when="D", interval=1, backupCount=7)
        self.LOG.addHandler(handler)
        self.LOG.info(f'微信登录成功，你的微信wid：{self.wxid}')

    def enable_receiving_msg(self) -> None:
        """wcferry 信息接收并转发"""
        def inner_process_msg():
            while self.wcf.is_receiving_msg():
                try:
                    msg = self.wcf.get_msg()
                    self.session_manager.wx_receive_message(msg, self.wcf)
                except Empty:
                    continue  # Empty message
                except Exception as e:
                    print(f"Receiving message error: {e}")

        self.wcf.enable_receiving_msg()  # 持续接收回调信息
        Thread(target=inner_process_msg, name="GetMessage", daemon=True).start()

    def enable_recv_msg(self, callback) -> None:
        self.wcf.enable_recv_msg(callback)

    def send_text_msg(self, msg: str, receiver: str, at_list: str = "") -> None:
        """ 发送消息
        :param msg: 消息字符串
        :param receiver: 接收人wxid或者群id
        :param at_list: 要@的wxid, @所有人的wxid为：notify@all
        """
        # msg 中需要有 @ 名单中一样数量的 @
        ats = ""
        if at_list:
            if at_list == "notify@all":  # @所有人
                ats = " @所有人"
            else:
                wxids = at_list.split(",")
                for wxid in wxids:
                    # 根据 wxid 查找群昵称
                    ats += f" @{self.wcf.get_alias_in_chatroom(wxid, receiver)}"

        # {msg}{ats} 表示要发送的消息内容后面紧跟@，例如 北京天气情况为：xxx @张三
        if ats == "":
            self.LOG.info(f"To {receiver}: {msg}")
            self.wcf.send_text(f"{msg}", receiver, at_list)
        else:
            self.LOG.info(f"To {receiver}: {ats}\r{msg}")
            self.wcf.send_text(f"{ats}\n\n{msg}", receiver, at_list)

    def get_all_contacts(self) -> dict:
        """
        获取联系人（包括好友、公众号、服务号、群成员……）
        格式: {"wxid": "NickName"}
        """
        contacts = self.wcf.query_sql("MicroMsg.db", "SELECT UserName, NickName FROM Contact;")
        return {contact["UserName"]: contact["NickName"] for contact in contacts}

    def auto_accept_friend_request(self, msg: WxMsg) -> None:
        """ 自动接受添加 好友 """
        try:
            xml = ET.fromstring(msg.content)
            v3 = xml.attrib["encryptusername"]
            v4 = xml.attrib["ticket"]
            scene = int(xml.attrib["scene"])
            self.wcf.accept_new_friend(v3, v4, scene)

        except Exception as e:
            self.LOG.error(f"同意好友出错：{e}")

    def say_hi_to_new_friend(self, msg: WxMsg) -> None:
        """ 自动添加好友后 主动打招呼！ """
        nickName = re.findall(r"你已添加了(.*)，现在可以开始聊天了。", msg.content)
        if nickName:
            # 添加了好友，更新好友列表
            self.allContacts[msg.sender] = nickName[0]
            self.send_text_msg(f"Hi {nickName[0]}，我自动通过了你的好友请求。", msg.sender)