from gptapi import GeminiApi
s = {
    "model": "gemini-1.5-flash",
    "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" ,
    "api_key": "AAAAAAAAAAAAAAAAAAAAAAAAAAAA"  ,
    "api_versions": 'v1beta' ,
    "proxy": "http://127.0.0.1:1081"  ,

    "max_context": 4096  ,
    "parameters": {
    "max_tokens": 4096  ,
"temperature": 0.5  ,
"stream": False  }

}
text = [{"role": "user","content": "你好，gemini"}]
a = GeminiApi.generate_text(text,s)
print(a)