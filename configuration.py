#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import function


def load_config():
    """ 配置文件的初始化，注意没有验证配置文件的可行性！"""
    pwd = function.filepath('./config.yaml')
    print(f"配置文件路径地址： {pwd}")
    config = {}
    try:
        with open(pwd, "rb") as fp:
            config = yaml.safe_load(fp)
    except FileNotFoundError:
        print('创建文件，如果是权限不足给赋予读写文件权限。\n创建配置文件中...')
        try:
            with open(pwd, 'w', encoding='utf-8') as f:
                f.write(config_template)
                print('文件创建完成，请填写配置文件信息！')
        except Exception as e:
            print('文件创建失败！', e)

    except Exception as e:
        print('yaml文件可能有问题，请检查！以下是报错信息：')
        print(e)
    return config


config_template = """######## 配置默认规则 #############
# 如果是填写的文件路径是相对路径，会根据当前的function.py文件位置来计算，相对路径必须是 ./  开头
# 账号和群号 默认应该都是字符类型的（账号和群号虽然是整型）
# 如果对接的模块配置了另外的api名称，则该配置会覆盖全局的api配置
# api功能名称代表的含义： chat（聊天对话）、text_to_image_api（文本生成图像）
# 默认所有的api功能都是启用的，如果不想启用，设置为空或修改为api名称没有的，如修改为 "不启用"

######## 配置默认规则结束 #############

######## 机器人配置 #############
qq_bot: false   # QQ机器人开关 必填
weixin_bot: false   # 微信机器人开关 必填
web_bot: false   # 网页开关 必填
log: "./log/"   # 程序运行日志保存地址 必填
filepath: "./BotFile/"  # 程序运行过程中所产生的文件的保存地址，如文本生成图片，接收图片，其他文件等 必填
debug: false  # 程序的调试开关，主要会显示一些更多的提示信息，比如 配置错误 会在对应的平台发出响应信息 必填
admin_user:   # 平台管理员账号，只有包含在内的账号才能使用管理员功能，后期扩展管理使用  必填
  "qq": ["2956098898"]   # qq 对接平台 QQ账号 选填
  "wx": ["微信wid"]   # 微信对接平台 微信wid
  "web": [""]  # 网页对接平台  web账号
######## 机器人配置结束 ########

######## 默认 api 配置功能名称  ########
chat_api: "chat_xunfei"  # 聊天对话功能 默认的 api名称
text_to_image_api: "text_to_image_xufei"  # 文本生成图像  默认的 api名称
background_to_image_api: "background_to_image_tywx"  # 背景生成图像  默认的 api名称 ，暂未开发
understand_img_api: ""   # 图片理解，暂未开发
ppt_api: ""  # ppt 生成，暂未开发
######## 默认 api配置 结束 ########

######## QQ对接接口的配置 ########
qq:
  number: "2956098898"  # QQ账号,这里填写你的QQ机器人账号  必填
  port: 3001   # napcat  的监听端口  必填
  token: "jiubanyipeng"  # napcat 的鉴权密钥  必填

  timeout_clear: 3600   # 最长等待响应秒数,在指令等待中如果超过这个时间没有收到消息，则自动清理账号的继续对话
  group_disabled: false  # 是否仅允许特定的群成员发送聊天信息响应，群名单`enable`配置，默认是全部允许，如果开启，必须配置群名单，否则在群聊中将不回应
  groups_enable: ["939531887 "]  # 允许响应的群 roomId，大概长这样：939531887
  private_disabled: false  # 是否开启私有，当开启私有时，不管私人发送信息还是在群聊中被@，只有在`permit_group`名单中才会被响应，管理员名单不会被该限制
  permit_group: ["2956098898","QQ账号二","QQ账号三"]  # 被允许的个人账号名单
  log_chat: false   # 聊天对话是否保存
  log_chat_path: "./log/qq/chat/"  # 聊天对话 日志保存路径
  # api对接功能是否使用默认，如果不是请修改对应功能的名称
  api:
    chat: 'default'   # 聊天对话功能，是否默认使用全局，单独使用请填写最下面的api名称，如：chat_openai
    text_to_image_api: 'default'  # 文本生成图像，是否默认使用全局，单独使用请填写最下面的api名称
    background_to_image_api: 'default' # 背景生成图像，是否默认使用全局，单独使用请填写最下面的api名称
######## QQ对接接口的配置 结束 ########

######## 微信对接接口的配置 ########
wx:
  port: 9998   # `wcferry` RPC 服务器端口，默认为 10086，接收消息会占用 `port+1` 端口
  max_timeout: 3600  # 最长等待响应秒数
  private_disabled: false   # 是否开启私有，当开启私有时，不管私人发送信息还是在群聊中被@，只有在`permit_group`名单中才会被响应，管理员名单不会被该限制
  permit_group: ["微信wid","账号二","账号三"]  # 被允许的名单
  groups_disabled: false  # 是否仅允许特定的群成员发送聊天信息响应，群名单`enable`配置，默认是全部允许，如果开启，必须配置群名单，否则在群聊中将不回应
  groups_enable: []  # 允许响应的群 roomId，大概长这样：2xxxxxxxxx3@chatroom
  log_chat: true   # 是否将聊天对话写入到日志中，可删除，默认是不保存
  log_chat_path: "./log/weixin/chat/"   # 聊天对话 日志文件的路径
  # api对接功能是否使用默认，如果不是请修改对应功能的名称
  api:
    chat: 'default'   # 聊天对话功能，是否默认使用全局，单独使用请填写最下面的api名称，如：chat_openai
    text_to_image_api: 'default'  # 文本生成图像，是否默认使用全局，单独使用请填写最下面的api名称
    background_to_image_api: 'default' # 背景生成图像，是否默认使用全局，单独使用请填写最下面的api名称
######## 微信对接接口的配置  结束 ########

######## web对接接口的配置  ########
web:
  port: 9999   # web服务端口
  auto_login: true  # 是自动登录，如果开启则直接是匿名登录
  user_data:
    "账号": "密码"  # 登录账号密码，账号和密码都是字符串类型，管理员请以最上方为主。目前暂不开发web更多的功能
  log_chat: true   # 是否将聊天对话写入到日志中，可删除，默认是不保存
  log_chat_path: "./log/web/chat/"   # 聊天对话 日志文件的路径
  # api对接功能是否使用默认，如果不是请修改对应功能的名称
  api:
    chat: 'chat_xunfei_web'   # 聊天对话功能，是否默认使用全局，单独使用请填写最下面的api名称，如：chat_xunfei_web
    text_to_image_api: 'default'  # 文本生成图像，是否默认使用全局，单独使用请填写最下面的api名称
    background_to_image_api: 'default' # 背景生成图像，是否默认使用全局，单独使用请填写最下面的api名称
######## web对接接口的配置  结束 ########

######## api接口名称配置文件的详细配置  ########
api:
  # 以下的配置信息，需要与上面的填写的配置名称对应
  chat_xunfei:    # 聊天对话 讯飞配置
    model: "Lite"   # Lite、Pro、Pro-128K、Max、Max-32K和4.0 Ultra六个版本
    url: "https://spark-api-open.xf-yun.com/v1/chat/completions"
    APIPassword: "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    max_context: 4096   # 对话文本数据的最大长度（用户对话 + api接口回复 的文字)，当该键不存在默认值为4096
    parameters:   # 参数，以下是填写官方给出的参数，具体请查看官方api的参数介绍：https://www.xfyun.cn/doc/spark/HTTP调用文档.html#_3-请求说明
      max_tokens: 4096   # 参考官方给出的参数
      temperature: 0.5  # 参考官方给出的参数
      stream: false      #  是否启用流式返回，建议QQ和微信平台不要启用该功能，回复信息太快容易导致账号异常

  chat_openai:
    api_key: "sk-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    model: "text-davinci-003"
    url: "https://api.chatgpt.com/v1/chat/completions"
    max_context: 4096  # 对话文本数据的最大长度（用户对话 + api接口回复 的文字)，当该键不存在默认值为4096
    proxy: ""  # 代理地址，如果不需要代理，请删除该键或设置为空，参考：http://127.0.0.1:1081
    parameters:  # 参数，以下是填写官方给出的参数，具体请查看官方api的参数介绍：
      max_tokens: 4096
      temperature: 0.5
      stream: false      #  是否启用流式返回，建议QQ和微信平台不要启用该功能，回复信息太快容易导致账号异常
      
  chat_tyqw:  # 聊天对话 通义千问配置，注意，没有免费额度，新版没有进行测试！
    api_key: "sk-eAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    model: "qwen-plus"
    url: "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    max_context: 6000  # 对话文本数据的最大长度（用户对话 + api接口回复 的文字)，当该键不存在默认值为4096
    parameters:  # 参数，以下是填写官方给出的参数，具体请查看官方api的参数介绍：
      max_tokens: 4096
      temperature: 1
    DashScope_Plugin:  # 该功能未适配，
      ocr: false
      calculator: false
      text_to_image: false
      pdf_extracter: false
      code_interpreter: false

  chat_bigmodel: # 聊天对话 智谱配置
    model: "lm-4-Flash"   # lm-4-plus、glm-4-0520、glm-4 、glm-4-air、glm-4-airx、glm-4-long 、 glm-4-flashx 、 glm-4-flash
    url: "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    APIPassword: "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    max_context: 4096   # 对话文本数据的最大长度（用户对话 + api接口回复 的文字)，当该键不存在默认值为4096
    parameters: # 参数，以下是填写官方给出的参数，具体请查看官方api的参数介绍：
      max_tokens: 4096   # 参考官方给出的参数
      temperature: 0.5  # 参考官方给出的参数
      stream: false      #  是否启用流式返回，建议QQ和微信平台不要启用该功能，回复信息太快容易导致账号异常

  chat_gemini: # 聊天对话 Gemini配置,注意：由于兼容问题，暂仅使用openai的模型的兼容接口
    model: "gemini-1.5-flash"
    url: "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"   # 由于国内问题网络，可以使用代理好的地址或使用下面的配置进行代理
    api_key: "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"  # api秘钥
    api_versions: 'v1beta'   # 暂未启用。官方api的版本接口，版本的区别官方介绍：https://ai.google.dev/gemini-api/docs/api-versions?hl=zh-cn#rest
    proxy: ""  # 代理地址，如果不需要代理，请删除该键或设置为空，参考：http://127.0.0.1:1081

    max_context: 4096   # 对话文本数据的最大长度（用户对话 + api接口回复 的文字)，当该键不存在默认值为4096
    parameters: # 参数，以下是填写官方给出的参数，具体请查看官方api的参数介绍：
      max_tokens: 4096   # 参考官方给出的参数
      temperature: 0.5  # 参考官方给出的参数
      stream: false      #  是否启用流式返回，建议QQ和微信平台不要启用该功能，回复信息太快容易导致账号异常
  
  chat_grok: # 聊天对话 grok配置
    model: "grok-2-1212"
    url: "https://api.x.ai/v1/chat/completions"  # 由于国内问题网络，可以使用代理好的地址或使用下面的配置进行代理
    api_key: "xai-vEVPALAejlvU0SfeG9Djn5NL3E3a1nNNtGUcaHAkAoYwOiHSSOqaXWfVtzA7bJ54ZTAe6LYy9cXoSGGp"  # api秘钥
    proxy: ""  # 代理地址，如果不需要代理，请删除该键或设置为空，参考：http://127.0.0.1:1081
    max_context: 4096   # 对话文本数据的最大长度（用户对话 + api接口回复 的文字)，当该键不存在默认值为4096
    
    parameters: # 参数，以下是填写官方给出的参数，具体请查看官方api的参数介绍：
      max_tokens: 4096   # 参考官方给出的参数
      temperature: 0.5  # 参考官方给出的参数
      stream: false     #  是否启用流式返回，建议QQ和微信平台不要启用该功能，回复信息太快容易导致账号异常
  
  ocr_tyqw:
    api_key: "sk-eAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    url: "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    model: "qwen-vl-plus"

  text_to_image_tywx:  # 文本生成图片 通义千问配置
    api_key: "sk-eAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    await_number: 60
    request_time: 3
    url: "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    parameters:  # 参数，以下是填写官方给出的参数，具体请查看官方api的参数介绍：
      model: "wanx-v1"
      style: "<auto>"
      size: "1024*1024"
      n: 1
      
  calculator_tywx: {}
  
  pdf_extracter_tywx: {}
  
  code_interpreter_tywx: {}

  text_to_image_xufei:   # 文本生成图片 讯飞配置
    APPID: "00000000"
    APISecret: "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    APIKey: "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    url: "https://spark-api.cn-huabei-1.xf-yun.com/v2.1/tti"
    parameters:  # 默认参数，填写官方给出的参数，参数会被使用 用户修改
      width: 512
      height: 512


  background_to_image_tywx:  # 背景生成图片 通义千问配置
    api_key: "sk-eAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    await_number: 60
    request_time: 3
    url: "https://dashscope.aliyuncs.com/api/v1/services/aigc/background-generation/generation/"
    model: "wanx-background-generation-v2"
    parameters:  # 参数，以下是填写官方给出的参数，具体请查看官方api的参数介绍：
      n: 1
      noise_level: 300
      ref_prompt_weight: 0.3

  chat_xunfei_web: # 聊天对话 讯飞配置 web端专用
    model: "Lite"   # Lite、Pro、Pro-128K、Max、Max-32K和4.0 Ultra六个版本
    url: "https://spark-api-open.xf-yun.com/v1/chat/completions"
    APIPassword: "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    max_context: 4096   # 对话文本数据的最大长度（用户对话 + api接口回复 的文字)，当该键不存在默认值为4096
    parameters: # 参数，以下是填写官方给出的参数，具体请查看官方api的参数介绍：https://www.xfyun.cn/doc/spark/HTTP调用文档.html#_3-请求说明
      max_tokens: 4096   # 参考官方给出的参数
      temperature: 0.5  # 参考官方给出的参数
      stream: True      #  启用流式返回
"""


