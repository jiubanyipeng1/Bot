# import os
# from gptapi import Grok
#
#
# s = {
#     "model": "grok-2-1212",
#     "url": "https://api.x.ai/v1/chat/completions"  ,
#     "api_key": "xai-v电饭锅单方事故森岛帆高送达方刚Gp" ,
#     "proxy": "http://127.0.0.1:1081"  ,
#     "max_context": 4096  ,
#     "parameters":  {
#     "max_tokens": 4096  ,
#     "temperature": 0.5  ,
#     "stream": False }
# }
# text = [{"role": "user","content": "你好，Grok"}]
# result=  Grok.generate_text(text, s)
# print(result)
# if isinstance(result["data"], str):  # 处理非流式响应
#     print(result["data"])
# elif isinstance(result["data"], dict):
#     print('报错')
#     print(result)
# elif hasattr(result["data"], '__iter__'):
#     # 处理流式响应
#     for item in result["data"]:
#         print(item)
#



