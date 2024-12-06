#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml


def load_config():
    """ 配置文件的初始化，注意没有验证配置文件的可行性！"""
    pwd = os.path.dirname(os.path.abspath(__file__))
    config = {}
    try:
        with open(f"{pwd}/config.yaml", "rb") as fp:
            config = yaml.safe_load(fp)
    except FileNotFoundError:
        print('创建文件，如果是权限不足给赋予读写文件权限。\n创建配置文件中...')
        try:
            with open('./config.yaml', 'w', encoding='utf-8') as f:
                f.write(config_template)
                print('文件创建完成，请填写配置文件信息！')
        except Exception as e:
            print('文件创建失败！', e)

    except Exception as e:
        print('yaml文件可能有问题，请检查！以下是报错信息：')
        print(e)
    return config


config_template = """qq_bot: false   # QQ机器人开关
weixin_bot: false   # 微信机器人开关
web_bot: true   # 网页开关
bot_instruct_hint: true   #
bot_host_name: ""
bot_file_path: ""
bot_file_del: false
bot_debug: false
bot_admin_user:   # 管理员账号，只有包含在内的账号才能启用管理员功能
  "qq": ["2956098898"]   # qq 对接平台
  "weixin": ["微信wid"]   # 微信对接平台
  "web": ["账号"]  # 网页对接平台

chat_api: "chat_tyqw"
ocr_api: ""
pdf_extracter_api: ""
text_to_image_api: "text_to_image_tqwx"
calculator_api: ""
code_interpreter_api: ""
background_to_image_api: "background_to_image_tywx"

role_play: false
system_content: "You are a helpful assistant."

qq_config:
  timeout_clear: 3600
  group_disabled: false
  private_disabled: false
  permit_group: ["2956098898","QQ账号二","QQ账号三"]
  log:
    chat: true
    chat_path: "./log/qq/chat/"

weixin_config:
  timeout_clear: 3600
  group_disabled: false
  private_disabled: false
  permit_group: ["微信wid","QQ账号二","QQ账号三"]
  log:
    chat: true
    chat_path: "./log/weixin/chat/"

web_config:
  port: 9999
  streaming: false
  login: true
  user_data:
    "账号": "密码"
  log:
    chat: true
    chat_path: "./log/web/chat/"


api:
  chat_xunfei:
    appid: "66456fafad"
    api_secret: "dfgsf5436fggs5445"
    api_key: "adfsadsfafadaf"
    model: "general"
    url: "ws://spark-api.xf-yun.com/v1.1/chat"
    max_tokens: 4096
    max_context: 4096
    temperature: 0.5

  chat_openai:
    api_key: "sk-dafdafa43524524dfag"
    model: "text-davinci-003"
    url: "https://api.chatgpt.com/v1/chat/completions"
    max_tokens: 4096
    max_context: 4096
    temperature: 0.5

  chat_tyqw:
    api_key: "sk-dsafdfadf67575647"
    model: "qwen-plus"
    url: "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    max_tokens: 1500
    max_context: 6000
    temperature: 1
    DashScope_Plugin:
      ocr: false
      calculator: false
      text_to_image: false
      pdf_extracter: false
      code_interpreter: false

  ocr_tyqw:
    api_key: "sk-dfafafad53654"
    url: "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    model: "qwen-vl-plus"

  text_to_image_tywx:
    api_key: "sk-fadfa356546354"
    await_number: 60
    request_time: 3
    url: "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    model: "wanx-v1"
    style: "<auto>"
    size: "1024*1024"
    n: 1
  calculator_tywx: {}
  pdf_extracter_tywx: {}
  code_interpreter_tywx: {}

  background_to_image_tywx:
    api_key: "sk-fadsfah567363gws"
    await_number: 60
    request_time: 3
    url: "https://dashscope.aliyuncs.com/api/v1/services/aigc/background-generation/generation/"
    model: "wanx-background-generation-v2"
    n: 1
    noise_level: 300
    ref_prompt_weight: 0.3
"""


