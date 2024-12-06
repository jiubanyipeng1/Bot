# coding:utf-8
# 功能集合函数模块
from time import localtime, time, strftime
import os
import aiofiles
import base64

from gptapi import XunFeiApi, OpenAiApi, TongYiQianWen, ZhiPuApi


# 异步写入聊天日志
async def write_log(file_path, file_name, data) -> dict:
    """ 异步写入文本数据
    :param file_path: 文件地址
    :param file_name: 文件名
    :param data: 数据内容，会在数据内容前面自动添加时间
    :return: 是否写入成功和信息
    """
    try:
        file_path = os.path.join(file_path, file_name)
        absolute_file_path = os.path.abspath(file_path)
        directory = os.path.dirname(absolute_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        log_time = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
        async with aiofiles.open(file_path, 'a', encoding='utf-8') as file:
            await file.write(f"{log_time}  \n {data}")
            return {'code': True, 'mes': f'{file_path},写入完成'}
    except PermissionError:
        return {'code': False, 'mes': f'文件:{file_path},无写入权限'}
    except Exception as e:
        return {'code': False, 'mes': f"写入日志文件错误：{e}"}


# 异步写入图片数据
async def write_img(file_path, file_name, data) -> dict:
    """ 异步写入文本数据
        :param file_path: 文件地址
        :param file_name: 文件名
        :param data: 数据内容，会在数据内容前面自动添加时间
        :return: 是否写入成功和信息
        """
    try:
        file_path = os.path.join(file_path, file_name)
        absolute_file_path = os.path.abspath(file_path)
        directory = os.path.dirname(absolute_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        image_data = base64.b64decode(data)

        async with aiofiles.open(file_path, mode='wb') as f:
            await f.write(image_data)
            # 检查文件是否存在
        if os.path.exists(absolute_file_path):
            return {'code': True, "path": absolute_file_path, 'info': '图片保存成功'}
        else:
            return {'code': False, "data": '图片路径不存在！', "path": absolute_file_path, 'info': '图片保存失败'}
    except Exception as e:
        return {'code': False, "data": str(e), "save_path": file_path + file_name, 'info': '图片保存运行过程报错'}


# 聊天的字符串计算和字符串列表删除
def checklen(text, max_context=4096):
    """ 聊天的字符串计算和字符串列表删除
    :param text: 文本列表
    :param max_context:最长的长度
    :return: 更新后的文本列表
    """

    def getlength(text):  #
        length = 0
        for content in text:
            temp = content["content"]
            leng = len(temp)
            length += leng
        return length

    checklen_len = len(text)
    text_len = 0
    checklen_text = text
    while getlength(checklen_text) > max_context:
        text_len += 1
        # 最后一条信息超过限制就获取部分信息
        if text_len == checklen_len:
            txt = checklen_text[-1]['content'][:max_context]
            checklen_text[-1]['content'] = txt
        else:
            del checklen_text[0]
    # 不允许assistant在第一个会话中
    if checklen_text[0]['role'] == 'assistant':
        del checklen_text[0]
    return checklen_text


# 聊天  GPT的API对接
async def start_chat(chat_data, name_api, config_api):
    """ 聊天对接模块
    :param chat_data:本次会话的聊天列表
    :param name_api: api名称
    :param config_api: api的配置
    :return:数据都是以字典返回，{'code': 布尔类型，本次对接状态, 'data': 接口返回的内容信息内容}
    """
    mes = {'code': False, 'mes': f'API对接函数（function）错误,没有该api名称的配置文件：{name_api}'}
    # 检查聊天信息的长度 如果长度过长会截最前面的会话信息，默认计算的大小为 4096
    max_context = config_api.get('max_context', 4096)
    text = checklen(chat_data, max_context)
    # 执行，后期使用函数将其包含执行
    if name_api == "chat_xunfei":
        mes = await XunFeiApi.generate_text(text, config_api)
    elif name_api == "chat_openai":
        return OpenAiApi.generate_text(text, config_api)  # 发送数据并返回答案,返回的是字典
    elif name_api == "chat_tyqw":
        return TongYiQianWen.generate_text(text, config_api)
    elif name_api == "bigmodel":
        return ZhiPuApi.generate_text(text, config_api)
    return mes


async def text_generate_img(api_name, text, config_api, keys):
    """ 文本生成图像 对接模块 """
    mes = {'code': False, 'mes': f'API对接函数（function）错误,没有该api名称的配置文件：{api_name}'}
    # 检查聊天信息的长度 如果长度过长会截最前面的会话信息，默认计算的大小为 4096
    # 执行，后期使用函数将其包含执行
    if api_name == "text_to_image_xufei":
        if len(keys) > 2:
            return {'code': False, 'data': '参数长度不对！','info':'文本生成图像 讯飞 参数过长！最多仅有两个参数！'}
        dict_keys = [i for i in config_api['parameters'].keys()]
        for i in range(len(keys)):
            if keys[i] is None or keys[i] == '':
                continue
            config_api['parameters'][dict_keys[i]] = keys[i]
        mes = await XunFeiApi.text_generate_img(text, config_api)
        return mes
    # elif api_name == "chat_openai":
    #     return OpenAiApi.text_generate_img(text, config_api)  # 发送数据并返回答案,返回的是字典
    # elif api_name == "chat_tyqw":
    #     return TongYiQianWen.text_generate_img(text, config_api)
    return mes

