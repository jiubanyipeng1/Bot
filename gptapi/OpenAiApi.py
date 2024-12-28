# -*- coding: utf-8 -*-
# 对接ChatGPT
import requests
import json

# 聊天对话
async def generate_text(prompt,api_config):
    """
    :param prompt: 历史对话内容，[{},{}]
    :param api_config: ChatGPT的API配置信息
    :return: 返回聊天系统的对话
    """
    url = api_config.get('url', 'https://api.openai.com/v1/chat/completions')
    model = api_config.get('model', 'gpt-4o-mini')
    parameters = api_config.get('parameters', {})
    parameters['model'] = model
    parameters['messages'] = prompt
    stream = parameters.get('stream', False)
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_config.get('api_key', '')}"
    }
    if api_config.get('proxy', '') != '':
        proxies = {
            'http': api_config.get('proxy', False),
            'https': api_config.get('proxy', False),
        }
    else:
        proxies = None
    try:
        if stream:
            response = requests.post(url, headers=header, json=parameters, stream=True,proxies=proxies)
            response.encoding = "utf-8"
            def stream_response():
                for line in response.iter_lines(decode_unicode="utf-8"):
                    if line.startswith('data: '):
                        if line == 'data: [DONE]':  # 验证是否结束
                            break
                        data = json.loads(line[6:])
                        if data['choices'][0]['delta'].get('content',False):
                            yield data['choices'][0]['delta']['content']
            if response.status_code != 200:  # 这里失败的一般是配置有问题
                return {'code': False, "data": response.text, 'info': 'openai的配置接口错误，请检查配置文件！'}

            return {'code': True, "data": stream_response(), 'info': 'openai聊天接口返回'}
        else:
            response = requests.post(url, headers=header, json=parameters,proxies=proxies)
            if response.status_code != 200:  # 这里失败的一般是配置有问题
                return {'code': False, "data": response.text, 'info': 'openai的配置接口错误，请检查配置文件！'}
            return {'code': True, "data": response.json()["choices"][0]['message']["content"],'info': 'openai聊天接口返回'}

    except requests.exceptions.RequestException as e:
        return {'code': False, "data": str(e), 'info': '可能是网络问题，或配置文件的url地址不对！'}

    except Exception as e:
        return {'code': False, "data": str(e), 'info': '程序报错！有可能openai口返回的数据格式不对！'}



# 图片生成