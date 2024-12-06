# coding:utf-8
from asyncio import run as asyncio_run
from json import dumps as json_dumps, loads as json_loads
from os import makedirs as os_makedirs
from time import sleep
import websocket
import function


class QQBot:
    """ QQ机器人运行 """
    def __init__(self, config) -> None:
        self.config = config

# 聊天对话数据处理，将对话数据进行切割
def chat_manage(user_id, role, chat_content, message_type, group_id='0'):
    group_pass = False
    # 会话初始化处理
    if message_type == 'group':
        if user_id not in chat_json:
            chat_json[user_id] = {'group': {group_id: {'chat_data': []}}}
        elif 'group' not in chat_json[user_id]:
            chat_json[user_id]['group'] = {group_id: {'chat_data': []}}
        elif group_id not in chat_json[user_id]['group']:
            chat_json[user_id]['group'][group_id] = {'chat_data': []}

        text = chat_json[user_id]['group'][group_id]['chat_data']
        group_pass = True
    else:
        if user_id not in chat_json:
            chat_json[user_id] = {'private': {'chat_data': []}}
        elif 'private' not in chat_json[user_id]:
            chat_json[user_id]['private'] = {'chat_data': []}

        text = chat_json[user_id]['private']['chat_data']
    if group_pass:
        if role == 'assistant':
            chat_json[user_id]['group'][group_id]['chat_data'] = {"role": 'assistant', "content":chat_content}
        else:
            chat_json[user_id]['group'][group_id]['chat_data'] = {"role": 'user', "content":chat_content}
            return text
    else:
        if role == 'assistant':
            chat_json[user_id]['private']['chat_data'] = {"role": 'assistant', "content":chat_content}
        else:
            chat_json[user_id]['private']['chat_data'] = {"role": 'user', "content":chat_content}
            return text


# QQ聊天信息处理
def qq_char_processor(user_mes_list,user_id,user_mes,type='private', group_id='0'):
    mes = function.chat_run_api(user_mes_list,bot_config['name_api'], api_config)
    # 将api对话添加到缓存会话中
    chat_manage(user_id, 'assistant', mes['mes'], type,group_id)

    # 这里是写入日志
    if bot_config['bot_chat_log'] and mes['code']:
        mes_log = f"[{type}:{group_id}:{user_id}] \n[user:{user_mes}]\n[assistant:{mes['mes']}]\n"
        print(asyncio_run(function.write_log('/qq/'+user_id, mes_log)))
    data_mes = send_msg(mes, user_id, type, group_id)
    # sleep(0.5)  # 限制发送消息的速度
    ws.send(data_mes)


# 消息发送通用封装
def send_msg(mes_data, user_id, type='group', group_id='0'):  # 消息是否为真、回复给谁、回复类型
    user_id = int(user_id)
    if type == 'private':
        data_mes = {"action": "send_msg",
                    "params": {"message_type": 'private', "user_id": user_id, 'message': mes_data['mes']}}
    else:
        data_mes = {"action": "send_group_msg",
                    "params": {"group_id": group_id, "message": f"[CQ:at,qq={user_id}] {mes_data['mes']}"}}

    return json_dumps(data_mes)  # 返回字符串形式的数据


# 客户端接收服务端数据时触发
def on_message(ws, message):
    data = json_loads(message)
    user_id = str(data.get('user_id', '0'))  # 将数字账号转为字符串账号

    # 减少cqhttp之间的通信，返回非信息不进行通信
    if data.get('post_type', '') != "message":
        return False
    # 机器人指令
    if '/bot ' == data["message"][0:5]:
        if user_id in qq_config.get('admin_group', []):
            pass
        else:
            mes = {'code': False, 'mes': f'账号：{user_id} 不属于管理员'}
            ws.send(send_msg(mes, user_id, data.get('message_type'), data.get('group_id', '0')))
            return False
    # 信息和账号验证
    if data['message_type'] == 'private':
        if qq_config['private_disabled']:  # 是否启用私发仅允许部分账号
            if user_id not in qq_config['permit_group']:
                return False
        qq_char_processor(chat_manage(user_id, 'user', data["message"], data['message_type']),user_id,data["message"])
    elif data['message_type'] == 'group':
        # 判断是否是 @ 机器人的消息
        if f"[CQ:at,qq={data.get('self_id')}]" in data.get("message"):
            # 是否启用群发仅允许部分账号
            if qq_config['group_disabled']:
                if user_id not in qq_config['permit_group']:
                    return False
            sickle_mes = data["message"].replace(f'[CQ:at,qq={data["self_id"]}]', '').strip()  # 将群信息@替换处理，仅保留信息内容
            data.update({'message': sickle_mes})
            qq_char_processor(chat_manage(user_id, 'user', sickle_mes, data['message_type'], data['group_id']),user_id,sickle_mes)
        else:
            # 不是@机器人，所以不进行回复
            return


# 通信发生错误时触发
def on_error(ws, error):
    print("{}\n在和go-cqhttp进行通信发生错误:{}".format(ws, error))
    if '[WinError 10061]' in str(error):
        print('请检查配置文件与go-cqhttp的地址和端口是否正确，或go-cqhttp是否运行成功')


# 连接关闭时触发
def on_close(ws, close_status_code, close_msg):
    print("### 关闭对接程序 ###")


# 连接建立时触发
def on_open(ws):
    ws.send('{"action":get_msg, "params":{"message_id":1}')  # 获取消息


chat_json = {}  # 对话缓存变量
qq_config = {}  # qq配置文件
api_config = {}  # 对接API平台的配置文件
bot_config = {}  # 全部的配置文件信息

if __name__ == "__main__":
    try:
        os_makedirs('BotLog/qq', exist_ok=True)
        with open('setting_config.json', 'r', encoding='utf-8') as f:
            bot_config = json_loads(f.read())
        api_config = bot_config[bot_config['name_api']]
        access_token = bot_config['cqhttp']['access_token']
        url = bot_config['cqhttp']['cqhttp_url']
        qq_config = bot_config['qq_config']
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(f"ws://{url}/?access_token={access_token}", on_message=on_message,
                                    on_error=on_error, on_close=on_close)
        ws.on_open = on_open
        ws.run_forever()
    except FileNotFoundError:
        function.get_setting_config()  # 创建配置文件
    except Exception as e:
        print('错误，请检查，以下是报错信息：\n', e, '退出...')
        sleep(5)

