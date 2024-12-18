# -*- coding: utf-8 -*-
import logging
from logging.handlers import TimedRotatingFileHandler
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools

from wcferry import Wcf, WxMsg
from cache_manager import CacheManager
import help
import function


class SessionHandler:
    """ 会话处理 """

    def __init__(self, cache_manager: CacheManager):
        # 初始化线程池，可以指定最大工作线程数，这里设为10
        self.executor = ThreadPoolExecutor(max_workers=10)

        self.config = cache_manager.config
        self.cache_manager = cache_manager

        self.LOG = logging.getLogger("session_handler")
        log_file = function.filepath(f'{self.config["log"]}/session_handler.log')  # 日志文件名称
        handler = TimedRotatingFileHandler(log_file, when="D", interval=1, backupCount=7)
        self.LOG.addHandler(handler)

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

    async def chat_message(self, keys, content):
        """ 与chat接口 聊天信息处理
        :param content: 本次聊天文本
        :param keys:['平台','用户账号','私人或公共','公共id']
        :return: {'is_send': True, 'code': False, 'data': 'chat_api 接口未配置或接口配置不正确！'}
        """
        user_data = self.cache_manager.get_nested_value(keys)  # 获取数据的缓存
        api_config = self.cache_manager.config['api']  # 获取api配置缓存
        # 验证chat_api 接口名称
        chat_api_name = self.cache_manager.config[keys[0]]['api'].get('chat', 'default')
        if chat_api_name == 'default':
            chat_api_name = self.config['chat_api']
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
        if ' ' in content:
            message_parameter = content.split(' ')[0].replace('/', '').split('#')
            message_content = content.split(' ', 1)[1]
        else:
            # 这里一般是管理员指令，非管理员指令对接的GPT应该使用默认生成，这样后面的才不会出现问题
            message_parameter = content.replace('/', '').split('#')
            message_content = ''

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
                save_path = function.filepath(f"{self.config['filepath']}/{keys[0]}/{keys[1]}/{keys[2]}/image/{result.get('filename','unknown.jpg')}")
                # 保存图片
                save = await function.write_img(save_path, result['data'])
                if save['code']:
                    save['is_system'] = False
                    save['file_type'] = 'img'
                    return save
                result = save
            # 这里一般是执行GPT错误或当参数不对时，顺便返回参数的使用帮助
            help_mes = help_operations.get('text_to_image_' + api_name, '无该参数的参考说明！')
            result['help'] = help_mes
            return result
        else:
            return {'code': False, 'data': f'指令：{message_parameter[0]} 不存在！'}

    def qq_send_process_message(self, mes, data) -> str:
        """ QQ 发送信息 封装处理 """
        message = []
        if data.get('file_type', False):
            if data['file_type'] ==  'img':
                message.append({'type': 'image', 'data':{'file': f"file://{data['path']}"}})
            elif data['file_type'] ==  'file':
                message.append({'type': 'file', 'data': {'file': f"file://{data['path']}"}})
        else:
            message.append({'type': 'text', 'data': {'text': data['data']}})

        params  = {"message_type": f"{mes['message_type']}"}

        if mes['message_type'] == 'group':
            params['group_id'] = mes['group_id']
            message.append({'type': 'at', 'data': {'qq': f'{mes["user_id"]}'}})
        else:
            params['user_id'] = mes['user_id']
        params['message_type'] = mes['message_type']
        params['message'] = message

        payload_str = json.dumps({"action": "send_msg", "params": params})
        return payload_str

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
                task = self.instruct_message(keys, msg.content)
                result = await task
            else:
                # 仅聊天
                task = self.chat_message(keys, msg.content)
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
                    filepath = function.filepath(f"{chat_path}/{path_name}")
                    log_text = 'user' + '\n' + msg.content + '\n' + 'assistant' + '\n' + mes + '\n'
                    write_log = await function.write_log(filepath, log_text)
                    self.LOG.info(write_log['mes'])

        self._run_in_thread(process_message)
        # future = self.executor.submit(lambda: asyncio.run(process_message()))
        # return future

    def qq_process_message(self, mes:dict, ws, is_continue=False):
        """qq 会话信息处理"""
        keys = ['qq', mes['user_id']]
        if mes['message_type'] == 'group':
            keys.append('group')
            keys.append(mes['group_id'])
            text = mes['text']
        else:
            keys.append('private')
            text = mes['raw_message']
        if is_continue:
            return {'is_system': True, 'code': True, 'data': '该功能暂未开发，请勿使用'}

        # 异步处理函数
        async def process_message():
            if text[:1] == '/':  # 是否存在指令
                task = self.instruct_message(keys, text)
                result = await task
            else:
                # 仅聊天
                task = self.chat_message(keys, text)
                result = await task

            # 是否发送文件，如果这里存在必然是要发送信息
            if result.get('file_type', False):
                # 清空用户的继续缓存
                keys.append('continue')
                self.cache_manager.update_nested_value(keys, False)
                mes_str = self.qq_send_process_message(mes, result)
                ws.send(mes_str)
                return
            # 发送 信息
            if result.get('is_system', True):  # 默认情况下系统信息
                # 系统的提示信息都添加到日志中
                self.LOG.info(result)

                # 系统的提示信息，这里一般是指令信息，需要回复给对方
                if result['code']:
                    mes_str = self.qq_send_process_message(mes,result)
                    ws.send(mes_str)
                else:
                    # 系统的报错信息，根据是否开启开关调试进行
                    if self.cache_manager.config.get('debug', False):
                        mes_str = self.qq_send_process_message(mes, result)
                        ws.send(mes_str)
                return
            else:  # 发送信息
                mes_text = ''
                if isinstance(result["data"], dict):  # 处理非流式响应
                    mes_text += result["data"]
                    mes_str = self.qq_send_process_message(mes, result)
                    ws.send(mes_str)
                elif hasattr(result["data"], '__iter__'):
                    # 处理流式响应
                    for item in result["data"]:
                        mes_str = self.qq_send_process_message(mes, {'data':item})
                        ws.send(mes_str)
                        mes_text += item

                data = self.cache_manager.get_nested_value(keys)
                data['continue'] = False
                text_list_data = data['text_list']
                text_list_data.append ({"role": 'assistant', "content": mes_text})
                data['text_list'] = text_list_data
                # 更新缓存
                self.cache_manager.update_nested_value(keys, data)
                # 是否将聊天记录写入
                if self.config['qq'].get('log_chat', False):
                    chat_path = self.config['qq'].get('log_chat_path' + '/', './')
                    if len(keys) == 3:
                        path_name = keys[0] + '_' + keys[1] + '_' + keys[2] + '.log'  # wx_账号_private
                    else:
                        path_name = keys[0] + '_' + keys[1] + '_' + keys[2] + '_' + keys[3] + '.log'
                    log_text = 'user' + '\n' + text + '\n' + 'assistant' + '\n' + mes_text + '\n'
                    filepath = function.filepath(f"{chat_path}/{path_name}")
                    write_log = await function.write_log(filepath, log_text)
                    self.LOG.info(write_log['mes'])

        self._run_in_thread(process_message)
        # future = self.executor.submit(lambda: asyncio.run(process_message()))
        # return future

    def web_process_message(self, ):
        """web 信息处理"""
        pass

    def shutdown(self):
        """关闭线程池"""
        self.executor.shutdown()
