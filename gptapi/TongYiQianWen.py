# -*- coding: utf-8 -*-
# 阿里云模型服务灵积，通义千问对接，文档上看，聊天对话通用、插件通用，各模型不通用
from requests import post as requests_post, get as requests_get
import json
import time


# 状态码 通用参考说明
status_code = {
    "InvalidParameter": "接口调用参数不合法",
    "DataInspectionFailed": "数据检查错误，输入或者输出包含疑似敏感内容被绿网拦截",
    "BadRequest.EmptyInput": "请求的输入不能为空",
    "BadRequest.EmptyParameters": "请求的参数不能为空",
    "BadRequest.EmptyModel": "请求输入的模型不能为空",
    "InvalidURL": "请求的 URL 错误",
    "Arrearage": "客户账户因为欠费而被拒绝访问",
    "UnsupportedOperation": "关联的对象不支持该操作（可以根据实际情况修改）",
    "InvalidApiKey": "请求中的 ApiKey 错误",
    "AccessDenied": "无权访问此 API，比如不在邀测中",
    "InvalidPlugin.AccessDenied": "无权访问此 API，比如不在邀测中",
    "AccessDenied.Unpurchased": "客户没有开通此商品",
    "RequestTimeOut": "请求超时",
    "BadRequest.TooLarge": "接入层网关返回请求体过大错误，错误如果是由mse网关层直接拦截，则没有 code，并且 message 不能自定义。如果是restful网关拦截返回code。",
    "BadRequest.InputDownloadFailed": "下载输入文件失败，可能是下载超时，失败或者文件超过限额大小，错误信息可以指出更细节内容。",
    "BadRequest.UnsupportedFileFormat": "输入文件的格式不支持。",
    "Throttling": "接口调用触发限流",
    "Throttling.RateQuota": "调用频次触发限流，比如每秒钟请求数",
    "Throttling.AllocationQuota": "一段时间调用量触发限流，比如每分钟生成Token数 或 免费额度已经耗尽，并且模型未开通计费访问。",
    "InternalError": "内部错误",
    "InternalError.Algo": "内部算法错误",
    "SystemError": "系统错误",
    "InternalError.Timeout": "异步任务从网关提交给算法服务层之后等待时间 3 小时，如果 3 小时始终没有结果，则超时。",
    "SUCCESSED": "任务执行成功",
    "FAILED": "任务执行失败",
    "CANCELED": "任务被取消",
    "PENDING": "任务排队中",
    "SUSPENDED": "任务挂起",
    "RUNNING": "任务处理中"
}


# 聊天对话
async def generate_text(prompt, api_config):
    """
    2023.12.31
    :param prompt: 历史对话内容，[{},{}]
    :param api_config: 通义千问的API配置信息
    :return: 返回聊天系统的信息
    """
    from function import checklen
    messages = checklen(prompt, api_config['max_context'])
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {api_config['api_key']}"}  # 流式返回  ,"X-DashScope-SSE":"enable"}
    data = {
        "model": api_config['model'],
        "input": {
            "messages": messages,
        },
        "parameters": {
            "max_tokens": api_config['max_tokens'],
            "temperature": api_config['temperature']
        }
    }
    try:
        response = requests_post(api_config['url'], headers=headers, json=data)
        data = response.json()
        if response.status_code != 200:
            return {"code": False, "mes": data, "hint": f'api接口返回的信息错误！\n 错误提示：{status_code.get(data["code"], "无")}'}
        return {"code": True, "mes": data['output']['text']}
    except Exception as e:
        return {"code": False, "mes": f'错误:{e}', "hint": '程序运行错误，可能是无法连接网络或接口内容返回问题!'}


# 插件生成，账号还没有开通，支持有：图片生成、文字识别、Python代码解释器、计算器、PDF解析、绘制函数图像
def generate_plugin(prompt, api_config, plug_name):
    if api_config['model'] != "qwen-plus":
        return {"code": False, "mes": f'模型不是"qwen-plus"，请更换模型！', "hint": '目前2024.1.7，通义千问的插件仅qwen-plus模型支持！'}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_config['api_key']}",
        "X-DashScope-Plugin": json.dumps({plug_name: {}}),
    }
    data = {
        "model": api_config['model'],
        "input": {
            "messages": prompt,
        },
        "parameters": {
            "result_format": "message",  # 默认为text。建议使用插件时，使用message类型
        }
    }
    try:
        response = requests_post(api_config['url'], headers=headers, json=data)
        if response.status_code != 200:
            return {"code": False, "data": response.text, "hint": f'api接口返回的信息错误！\n 错误提示：{status_code.get(data["code"], "无")}'}
        return {"code": True, "data": response}
    except Exception as e:
        return {"code": False, "data": f'错误:{e}', "hint": '程序运行错误，可能是无法连接网络或接口内容返回问题!'}


# 图片识别（通义千问VL-plus），图像格式目前支持：bmp,jpg,jpeg,png和tiff
def generate_ocr(prompt, api_config):
    messages = [
        {
            "role": "system",
            "content": [
                {"text": "You are a helpful assistant."}
            ]
        },
        {
            "role": "user",
            "content": [
                {"image": "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"},
                {"text": "这个图片是哪里？"}
            ]
        }
    ]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_config['api_key']}",
    }
    data = {
        "model": api_config['ocr']['model'],
        "input": {
            "messages": prompt,
        }
    }
    try:
        response = requests_post(api_config['ocr']['url'], headers=headers, json=data)
        data = response.json()
        if response.status_code != 200:
            return {"code": False, "data": response.text, "hint": f'api接口返回的信息错误！\n 错误提示：{status_code.get(data["code"], "无")}'}
        return {"code": True, "data": data}
    except Exception as e:
        return {"code": False, "data": f'错误:{e}', "hint": '程序运行错误，可能是无法连接网络或接口内容返回问题!'}


# 文本生成图像（通义万相）/图像背景生成（通义万相-图像背景生成）
async def generate_image(api_config, function_name):
    """
    :param api_config: 封装完成后的信息
    :param function_name: # 指令名称
    :return: 调用API的结果，个人使用应该是不需要修改返回方式
    """
    # 获取任务的结果，图片生成需要等待，成功获取到结果就直接发送，因此需要分离出来,返回任务ID等方式
    async def run_get_result(task_id):
        task_url = f'https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}'
        count = 0
        while count < await_number:
            time.sleep(request_time)  # 先进行延时
            response_img = requests_get(task_url, headers=headers)
            data_img = response_img.json()
            if response_img.status_code != 200:
                return {"code": False, "data": data_img, "hint": '可能是请求太频繁了'}
            task_status = data_img['output']['task_status']  # 任务作业状态
            if task_status == 'FAILED' or task_status == 'UNKNOWN':
                return {"code": False, "data": data_img, "hint": '作业失败或不存在！'}
            if task_status == 'SUCCEEDED':
                return {"code": True, "data": data_img, "hint": '图片生成完成！'}
            #  排队和处理中不做处理
            count += 1
            # print(data_img)
        else:
            # 时间到了，取消任务，后期再配合阿里的EventBridge事件转发进行更多的操作
            cancel_task_url = task_url + '/cancel'
            cancel_task = requests_get(cancel_task_url, headers=headers)
            if cancel_task.status_code != 200:
                print(f'任务:{task_id}，取消任务失败！接口返回信息：\n {cancel_task.text}')
            else:
                print(f'任务:{task_id}，取消成功！')
            return {"code": False, "data": f'等待图片生成时间超时', "hint": '等待图片生成时间超时'}

    # 运行任务请求
    async def run_request(url, data):
        try:
            response = requests_post(url, headers=headers, json=data)
            data = response.json()
            # print(data)
            if response.status_code != 200:
                return {"code": False, "data": data,
                        "hint": f'api接口返回的信息错误！\n 错误提示：{status_code.get(data["code"], "无")}'}
            get_result = await run_get_result(data['output']['task_id'])
            return get_result
        except Exception as e:
            return {"code": False, "data": f'错误:{e}', "hint": '程序运行错误，可能是连接网络问题！'}

    url = api_config['url']
    request_time = api_config['request_time']
    await_number = api_config['await_number']
    data = '数据初始化，数据会被下面重新覆盖'

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_config['api_key']}",
        "X-DashScope-Async": "enable"  # 表明使用异步方式提交作业
    }

    # 文本生成图像（通义万相）
    if function_name == 'text_to_image':
        data = {
            "model": api_config['model'],
            "input": {
                "prompt": api_config['prompt'],
            },
            "parameters": {
                "style": api_config['style'],  # 图片生成的风格
                "size": api_config['size'],  # 图片生成的大小
                "n": api_config['n'],    # 图片生成的数量，支持1~4 张，默认值1
                # "seed":42  # 随机值暂不用固定的，用系统自动生成的
            }
        }

    # 图像背景生成（通义万相-图像背景生成）
    if function_name == 'background_to_image':
        data = {
            "model": api_config['model'],
            "input": {
                "base_image_url": api_config.get('base_image_url', None),  # 透明背景的主体图像URL。需要为带透明背景的RGBA 四通道图像，支持png格式，分辨率长边不超过2048像素。输出图像的分辨率与该输入图相同
                "ref_image_url": api_config.get('ref_image_url', None),  # 引导图URL, 支持 jpg, png，webp等常见格式图像；
                "ref_prompt": api_config.get('ref_prompt', None),  # 引导文本提示词，支持中英双语，不超过70个单词。
                "neg_ref_prompt": api_config.get('neg_ref_prompt', None),  # 负向提示词，不希望出现的内容
                "title": api_config.get('title', None),  # 图像上添加文字主标题。算法自动确定文字的大小和位置，限制1-8个字符
                "sub_title": api_config.get('sub_title', None)   # 图像上添加文字副标题。算法自动确定文字的大小和位置，限制1-10个字符。仅当title不为空时生效
            },
            "parameters": {
                "noise_level": api_config.get('noise_level', 300),  # 当ref_image_url不为空时生效。在图像引导的过程中添加随机变化，数值越大与参考图相似度越低，默认值300，取值范围[0,999]
                "ref_prompt_weight": api_config.get('ref_prompt_weight', 0.5),  # 仅当ref_image_url和ref_prompt同时输入时生效，该参数设定文本和图像引导的权重。ref_prompt_weight表示文本的权重，图像引导的权重为1-ref_prompt_weight。默认值0.5，取值范围 [0,1]
                "n": api_config.get('n', 1)   # 图片生成的数量，支持1~4 张，默认值1
            }
        }
    run_result = await run_request(url, data)
    return run_result
