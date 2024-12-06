from  gptapi import ZhiPuApi
a =  [{"role": "user","content": "你好，讯飞星火"}]
b =  {
        "model": "glm-4-flash" ,
        "url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "APIkeys": "49a3bedf0ce0313c15d744aca547ad65.vzBtj69KT91zMiBm",
        "max_context": 4096,
        "parameters": {
            "max_tokens": 4096,
            "temperature": 0.5,
            "stream": True

        }
    }

result = ZhiPuApi.generate_text(a,b)
print(result)
for item in result["data"]:
    print(item)