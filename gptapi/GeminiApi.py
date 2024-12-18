import requests
import json

async def generate_text(text, config_api) -> dict:
    """ 生成文本
    :text: 文本列表 [{"role": "user","content": "你好，gemini"}]
    :config_api : {
        model: "Lite" ,
        url: "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        api_key: "aAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        max_context: 4096,
        parameters: {
            max_tokens: 4096,
            temperature: 0.5
        }
    }
    :return: {'code': 接口返回状态，布尔类型, "data": 返回接口的信息，如果是异步就是方法，}
    """
    url = config_api.get('url', 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions')
    model = config_api.get('model', 'gemini-1.5-flash')
    parameters = config_api.get('parameters', {})
    parameters['model'] = model
    parameters['messages'] = text
    stream = parameters.get('stream', False)
    header = {
        "Authorization": f"Bearer {config_api.get('api_key', '')}"
    }
    if config_api.get('proxy','') != '':
        proxies = {
            'http': config_api.get('proxy',False),
            'https': config_api.get('proxy',False),
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
                        if data.get('code', 99) == 0:
                            # 返回字典类型的数据
                            yield data['choices'][0]['delta']['content']
                        else:
                            yield data

            if response.status_code != 200:  # 这里失败的一般是配置有问题
                return {'code': False, "data": response.text, 'info': 'gemini的配置接口错误，请检查配置文件！'}

            return {'code': True, "data": stream_response(), 'info': 'gemini聊天接口返回'}
        else:
            response = requests.post(url, headers=header, json=parameters,proxies=proxies)
            if response.status_code != 200:  # 这里失败的一般是配置有问题
                return {'code': False, "data": response.json(), 'info': 'gemini的配置接口错误，请检查配置文件！'}

            return {'code': True, "data": response.json()['choices'][0]['message']['content'],'info': 'gemini聊天接口返回'}

    except requests.exceptions.RequestException as e:
        return {'code': False, "data": str(e), 'info': '可能是网络问题，或配置文件的url地址不对！'}

    except Exception as e:
        return {'code': False, "data": str(e), 'info': '程序报错！有可能gemini口返回的数据格式不对！'}