# -*- coding: utf-8 -*-
# 对接智谱
import requests
import json


async def generate_text(text, config_api) -> dict:
    """ 生成文本
    :text: 文本列表 [{"role": "system","content": "你是知识渊博的助理"},{"role": "user","content": "你好，讯飞星火"}]
    :config_api : {
        model: "Lite" ,
        url: "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        APIPassword: "aAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        max_context: 4096,
        parameters: {
            max_tokens: 4096,
            temperature: 0.5
        }
    }
    :return: {'code': 接口返回状态，布尔类型, "data": 返回接口的信息，如果是异步就是方法，}
    """
    url = config_api.get('url', 'https://open.bigmodel.cn/api/paas/v4/chat/completions')
    model = config_api.get('model', 'glm-4-flash')
    parameters = config_api.get('parameters', {})
    parameters['model'] = model
    parameters['messages'] = text
    stream = parameters.get('stream', False)
    header = {
        "Authorization": f"Bearer {config_api.get('APIkeys', '')}"  # 注意此处替换自己的APIPassword
    }

    try:
        if stream:
            response = requests.post(url, headers=header, json=parameters, stream=True)
            response.encoding = "utf-8"

            def stream_response():
                for line in response.iter_lines(decode_unicode="utf-8"):
                    if line.startswith('data: '):
                        if line == 'data: [DONE]':  # 验证是否结束
                            break
                        data = json.loads(line[6:])
                        if data['choices'][0]['delta']['content'] == '':
                            continue
                        yield data

            if response.status_code != 200:  # 这里失败的一般是配置有问题
                return {'code': False, "data": response.json(), 'info': '智谱的配置接口错误，请检查配置文件！'}

            return {'code': True, "data": stream_response(), 'info': '智谱聊天接口返回'}
        else:
            response = requests.post(url, headers=header, json=parameters)
            if response.status_code != 200:  # 这里失败的一般是配置有问题
                return {'code': False, "data": response.json(), 'info': '智谱的配置接口错误，请检查配置文件！'}

            if response.json().get('code', 99) == 0:
                return {'code': True, "data": response.json()['choices'][0]['message']['content']}
            else:
                return {'code': False, "data": response.json(),
                        'info': '智谱接口错误返回错误，请求速度太快或额度不足等，请查看详情'}

    except requests.exceptions.RequestException as e:
        return {'code': False, "data": str(e), 'info': '可能是网络问题，或配置文件的url地址不对！'}

    except Exception as e:
        return {'code': False, "data": str(e), 'info': '程序报错！有可能智谱接口返回的数据格式不对！'}

