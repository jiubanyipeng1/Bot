# -*- coding: utf-8 -*-
import logging
from logging.handlers import TimedRotatingFileHandler
import asyncio
from wcferry import Wcf, WxMsg
from cache_manager import CacheManager
import help
import function


class SessionHandler:
    """ 会话处理 """

    def __init__(self, cache_manager: CacheManager):
        self.LOG = logging.getLogger("session_handler")
        log_file = cache_manager.config['log'] + "/session_handler.log"  # 日志文件名称
        handler = TimedRotatingFileHandler(log_file, when="D", interval=1, backupCount=7)
        self.LOG.addHandler(handler)

        self.config = cache_manager.config
        self.cache_manager = cache_manager
        self.loop = asyncio.new_event_loop()  # 创建一个新的事件循环
        asyncio.set_event_loop(self.loop)  # 设置为当前事件循环

    async def chat_message(self, keys, content):
        """ 与chat接口 聊天信息处理
        :param content: 本次聊天文本
        :param keys:['平台','用户账号','私人或公共','公共id']
        :return: {'is_send': True, 'code': False, 'data': 'chat_api 接口未配置或接口配置不正确！'}
        """

        user_data = self.cache_manager.get_nested_value(keys)  # 获取数据的缓存
        api_config = self.cache_manager.config['api']  # 获取api配置缓存
        # 验证chat_api 接口名称
        if self.cache_manager.config[keys[0]]['api'].get('chat', 'default') == 'default':
            chat_api_name = self.config['chat_api']
        else:
            chat_api_name = self.config[keys[0]]['api'].get('chat', 'default')

        if api_config.get(chat_api_name, False):
            text_list_data = user_data['text_list']  # 获取直接的聊天缓存
            text_list_data.append({'role': 'user', 'content': content})  # 将本次的聊天缓存添加
            # 执行聊天对话的接口
            result = await function.start_chat(text_list_data, chat_api_name, api_config[chat_api_name])
            if result['code']:
                result['is_system'] = False
            else:
                result['is_system'] = True
                self.LOG.error(result)
            return result
        self.LOG.error(f'chat_api 接口未配置或接口配置不正确！chat aip名称：" {chat_api_name} " 不存在')
        return {'is_system': True, 'code': False, 'data': f'chat_api 接口未配置或接口配置不正确！chat aip名称：" {chat_api_name} " 不存在'}

    async def instruct_message(self, keys, content):
        """指令处理
        :param keys: ['平台','用户账号','私人或公共','公共id']
        :param content: /功能#图像风格类型#图像大小#几张图像 文本描述 \n 参考示列：/文本生成图像#3D卡通#1024#1 一直猫，黑色的，有点胖
        :return: {'is_send': True, 'code': True, 'mes': '已处理完成！'}
        """
        help_operations = {
            '帮助': help.bot_help(),
            'help': help.bot_help(),
            '菜单': help.bot_menu(),
            'text_to_image_xufei': help.text_to_image_xufei()
        }

        # /文本生成图像#3D卡通#1024#1 一直猫，黑色的，有点胖
        message_parameter = content.split(' ')[0].replace('/', '').split('#')
        message_content = content.split(' ', 1)[1] if ' ' in content else content

        operation = help_operations.get(message_parameter[0], '不存在帮助说明指令')
        if operation != '不存在帮助说明指令':
            return {'code': True, 'is_system': False, 'data': operation}

        if message_parameter[0] == '文本生成图像':
            if self.config[keys[0]]['api']['text_to_image_api'] == 'default':
                api_name = self.config['text_to_image_api']
            else:
                api_name = self.config[keys[0]]['api']['text_to_image_api']
            # 进行文本生成图片的操作
            result = await function.text_generate_img(api_name, message_content, self.config['api'][api_name],
                                                      message_parameter[1:])
            if result['code']:
                # 图片保存路径
                save_path = self.config['filepath'] + '/' + keys[0] + '/' + keys[1] + '/' + keys[2] + '/image/'
                # 保存图片
                save = await function.write_img(save_path, result['sid'], result['data'])
                if save['code']:
                    save['is_system'] = False
                    save['file_type'] = 'img'
                    return save
                result = save
            # 当参数不对时，顺便返回 参数的使用帮助
            help_mes = help_operations.get('text_to_image_' + api_name, '无该参数的参考说明！')
            result['help'] = help_mes
            return result
        else:
            return {'code': False, 'data': f'指令：{message_parameter} 不存在！'}

    def wx_process_message(self, msg: WxMsg, wcf: Wcf, is_continue=False):
        """ 微信 处理会话逻辑 """
        keys = ['wx', msg.sender]  # 获取值列表的初始化
        if msg.from_group():
            keys.append('group')
            keys.append(msg.roomid)
        else:
            keys.append('private')
        #  是否继续进行
        if is_continue:
            # 这里需要验证信息类型，一般是指文件，进行文件的保存！

            return {'is_system': True, 'code': True, 'data': '该功能暂未开发，请勿使用'}

        # 异步处理
        async def process_message():
            if msg.content[:1] == '/':  # 是否存在指令
                task = self.loop.create_task(self.instruct_message(keys, msg.content))
                result = await task
            else:
                # 仅聊天
                task = self.loop.create_task(self.chat_message(keys, msg.content))
                result = await task

            # 是否发送文件，如果这里存在必然是要发送信息
            if result.get('file_type', False):
                # 清空用户的继续缓存
                keys.append('continue')
                self.cache_manager.update_nested_value(keys, False)
                # 发送文件的类型
                if result.get('file_type', 'file') == 'img':
                    if msg.from_group():
                        wcf.send_image(result['path'], msg.roomid)
                    else:
                        wcf.send_image(result['path'], msg.sender)
                elif result.get('file_type', 'file') == 'file':
                    if msg.from_group():
                        wcf.send_file(result['path'], msg.roomid)
                    else:
                        wcf.send_file(result['path'], msg.sender)
                else:
                    self.LOG.error(f'发送文件类型,没有该类型文件:{result.get("file_type", "")}')
                return

            # 发送 文本信息
            if result.get('is_system', True):  # 默认情况下系统信息
                # 系统的提示信息都添加到日志中
                self.LOG.info(result)

                # 系统的提示信息，这里一般是指令信息，需要回复给对方
                if result['code']:
                    wcf.send_text(result['data'], msg.roomid, msg.sender)
                else:
                    # 系统的报错信息，根据是否开启开关调试进行
                    if self.cache_manager.config.get('debug', False):
                        wcf.send_text(result['data'], msg.roomid, msg.sender)
                return
            else:  # 发送信息
                mes = ''
                if isinstance(result["data"], dict):  # 处理非流式响应
                    mes += result["data"]
                    wcf.send_text(mes, msg.roomid, msg.sender)
                elif hasattr(result["data"], '__iter__'):
                    # 处理流式响应
                    for item in result["data"]:
                        wcf.send_text(item, msg.roomid, msg.sender)
                        mes += item

                data = self.cache_manager.get_nested_value(keys)
                data['continue'] = False
                text_list_data = data['text_list']
                text_list_data.append({"role": 'assistant', "content": mes})
                data['text_list'] = text_list_data
                # 更新缓存
                self.cache_manager.update_nested_value(keys, data)
                # 是否将聊天记录写入
                if self.config['wx'].get('log_chat', False):
                    chat_path = self.config['wx'].get('log_chat_path'+'/', './')
                    if len(keys) == 3:
                        path_name = keys[0] + '_' + keys[1] + '_' + keys[2] + '.log'  # wx_账号_private
                    else:
                        path_name = keys[0] + '_' + keys[1] + '_' + keys[2] + '_' + keys[3] + '.log'  # wx_账号_group_群号
                    log_text = 'user' + '\n' + msg.content + '\n' + 'assistant' + '\n' + mes + '\n'
                    write_log = await function.write_log(chat_path, path_name, log_text)
                    self.LOG.info(write_log['mes'])

        # 运行异步处理函数
        self.loop.run_until_complete(process_message())
