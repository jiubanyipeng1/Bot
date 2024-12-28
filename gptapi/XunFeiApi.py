import requests
import json
import base64
from datetime import datetime
from time import mktime
import hashlib
import hmac
from wsgiref.handlers import format_date_time
from urllib.parse import urlparse, urlencode
import aiohttp


def create_url(api_secret, api_key, url, method="POST"):
    """ 讯飞通用鉴权 url
    :param api_secret:
    :param api_key:
    :param url:
    :param method:
    :return:
    """
    now = datetime.now()   # 生成RFC1123格式的时间戳
    date = format_date_time(mktime(now.timetuple()))
    host = urlparse(url).netloc
    path = urlparse(url).path
    # 拼接字符串
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    # 进行hmac-sha256进行加密
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

    # 将请求的鉴权参数组合为字典
    values = {
        "authorization": authorization,
        "date": date,
        "host": host
    }
    # 拼接鉴权参数，生成url
    return url + '?' + urlencode(values)


async def generate_text(text, config_api) -> dict:
    """ 生成文本
    :text: 文本列表 [{"role": "system","content": "你是知识渊博的助理"},{"role": "user","content": "你好，讯飞星火"}]
    :config_api : {
        model: "Lite" ,
        url: "https://spark-api-open.xf-yun.com/v1/chat/completions",
        APIPassword: "aAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        max_context: 4096,
        parameters: {
            max_tokens: 4096,
            temperature: 0.5
        }
    }
    :return: {'code': 接口返回状态，布尔类型, "data": 返回接口的信息，如果是异步就是方法，}
    """
    url = config_api.get('url', 'https://spark-api-open.xf-yun.com/v1/chat/completions')
    model = config_api.get('model', 'Lite')
    parameters = config_api.get('parameters', {})
    parameters['model'] = model
    parameters['messages'] = text
    stream = parameters.get('stream', False)
    header = {
        "Authorization": f"Bearer {config_api.get('APIPassword', '')}"  # 注意此处替换自己的APIPassword
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
                        if data.get('code', 99) == 0:
                            # 返回字典类型的数据
                            yield data['choices'][0]['delta']['content']
                        else:
                            yield data

            if response.status_code != 200:  # 这里失败的一般是配置有问题
                return {'code': False, "data": response.text, 'info': '讯飞的配置接口错误，请检查配置文件！'}

            return {'code': True, "data": stream_response(), 'info': '讯飞聊天接口返回'}
        else:
            response = requests.post(url, headers=header, json=parameters)
            if response.status_code != 200:  # 这里失败的一般是配置有问题
                return {'code': False, "data": response.text, 'info': '讯飞的配置接口错误，请检查配置文件！'}

            if response.json().get('code', 99) == 0:
                return {'code': True, "data": response.json()['choices'][0]['message']['content']}
            else:
                return {'code': False, "data": response.text, 'info': '讯飞接口错误返回错误，请求速度太快或额度不足等，请查看详情'}

    except requests.exceptions.RequestException as e:
        return {'code': False, "data": str(e), 'info': '可能是网络问题，或配置文件的url地址不对！'}

    except Exception as e:
        return {'code': False, "data": str(e), 'info': '程序报错！有可能讯飞接口返回的数据格式不对！'}


async def text_generate_img(text, config_api):
    try:
        appid = config_api.get('APPID', 'appid')
        uid = config_api.get('uid', "123456789")
        domain = config_api.get('domain', "general")
        parameters = config_api.get('parameters', {'width': 512, 'height': 512})
        width = parameters['width']
        height = parameters['height']

        body = {"header": {"app_id": appid, "uid": uid},
            "parameter": {"chat": {"domain": domain, "width": width, "height": height}},
            "payload": {"message": {"text": [{"role": "user", "content": text}]}}}
        url = create_url(config_api['APISecret'], config_api['APIKey'], config_api['url'])
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers={'Content-Type': 'application/json'}) as response:
                if response.status == 200:
                    # 检查响应的内容类型
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/json' in content_type:
                        data = await response.json()
                    else:
                        result = await response.text()
                        data = json.loads(result)

                    if data['header']['code'] != 0:
                        return {'code': False, "data": data, 'info': '讯飞接口错误返回错误，请求速度太快或额度不足等，请查看详情'}
                    return {'code': True, "data": data["payload"]["choices"]["text"][0]['content'], 'filename': data['header']['sid']+'.jpg', 'info': '讯飞 文本生成图片 返回成功'}
                else:
                    return {'code': False, "data": '讯飞响应失败，返回状态不是200！', 'info': '讯飞接口错误返回错误，原因未知！'}
    except aiohttp.ClientError as e:
        return {'code': False, "data": str(e), 'info': '讯飞 文本生成图片 可能是网络问题、配置文件的url地址不对、许可凭证等问题'}
    except Exception as e:
        return {'code': False, "data": str(e), 'info': '讯飞 文本生成图片  未知，请查看详情'}