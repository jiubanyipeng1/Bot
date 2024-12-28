## QQ、微信、网页 对接GPT的接口
> 精力有限，目前仅兼容Windows10、Win11系统（其他Windows未测试），其他系统暂不考虑兼容

[更新说明](https://github.com/jiubanyipeng1/bot/blob/main/ChangeLog.md)

QQ对接平台引用的项目：[NapCatQQ](https://github.com/NapNeko/NapCatQQ)

微信对接平台引用的项目：[WeChatFerry](https://github.com/lich0821/WeChatFerry/)

网页使用python：flask

### 目前支持的功能：
- [x] 文本生成文本
- [x] 文本生成图片
- [ ] 文本生成PPT (等待开发)
- [ ] 背景生成图片 (等待开发)
- [ ] QQ、WX 管理指令 (等待开发)
### 目前支持的GPT平台接口：
> 注意：由于资金问题，部分的平台GPT对接的功能没有实现
- [x] OpenAI (目前仅支持文本生成文本)
- [x] Gemini (目前仅支持文本生成文本)
- [x] 讯飞  (目前支持文本生成文本、文本生成图片)
- [x] 智谱  (目前仅支持文本生成文本)
- [x] 通义千问  (目前仅支持文本生成文本)


### 使用：
> 如果你不懂开发环境安装，直接下载集成环境[releases](https://github.com/jiubanyipeng1/Bot/releases/)，里面有64位系统windows运行程序，其他版本暂时不考虑提供。

直接运行 main.py 即可，对应库请自行进行安装
### 开发：
> 版本不一致问题可能存在不兼容

开发环境版本 Python：3.9 、 napcat: 9.9.16-29927 、 WeChatFerry：39.3.3.0

[文档（未完善...）](#文件夹结构)

[QQ群939531887](https://qm.qq.com/q/UUKOU48AwM) 
#### 文件夹结构
<pre>
gptapi: GPT接口，所有的GPT平台接口都在这个文件夹下
static: 静态文件，存放图片等，主要用于存放web
templates: 模板文件，存放网页模板
napcat.29927.onekey: napcat QQ的模块接口文件夹
wcferry: WCFerry 微信的模块接口文件夹

config.yaml: 配置文件
cache_manager.py: 缓存管理器
configuration.py:当配置文件不存在时会生成配置文件
functions.py: 功能函数的集合
help.py: 帮助指令文档
main.py: 主程序入口
manager.py: 管理器，用于管理QQ、微信、网页等平台的对接
session_handler.py: 会话处理器，用于处理QQ、微信、网页等平台的会话
session_manager.py: 会话管理器，用于管理QQ、微信、网页等平台的会话
qq_bot.py: QQ机器人运行启动
web_bot.py: 网页运行启动
weixin_bot.py: 微信机器人运行启动

WEB平台独立出来，不使用管理器（管理器、会话处理器、会话管理器）。
</pre>
### 免责声明
#### 本项目中的所有第三方平台仅供参考，项目不对这些平台的可用性或安全性负责。
#### 本项目仅用于学习和交流目的，使用者或开发者应确保遵守相关法律法规，不得将本项目用于任何违法违规的行为或活动。
#### 本项目引用的第三方项目，会存在封号等账号相关安全的危险可能，请自行考虑是否使用，产生的后果自行承担。

