def bot_help():
    """机器人帮助
    :return: text
    """
    text = """
    格式：/功能名#参数1#参数2#参数3 描述  \n
    参考格式1: /文本生成图像#3D卡通#1024#1 一直猫，黑色的，有点胖   \n
    参考格式2: /文本生成图像#       \n
    说明：机器人指令以 "/" 开头，然后是指令名称，#代表参数，其中键和值以英文的':'区分，如果没有':',则按默认的键的值进行排序。 \n

    1.图片生成
    2.文字识别
    3.Python代码解释器
    4.计算器
    5.PDF解析
    如果存在需要发文件，先发送指令信息后，再发送文件，发送文件完成需要发送 "/文件发送结束"。

    功能指令是使用其他模型支持特定的功能，目前的功能指令名有：图片生成、文字识别，支持的平台：阿里云的模型服务灵积，
    """
    return text


def bot_menu():
    """ 机器人功能菜单"""
    text = """

    """
    return text


def help_none():
    return '该指令的说明不存在!'


def ocr():
    """
    聊天对话
    :return:
    """
    text = """

    """
    return text


def pdf_extracter():
    """
    PDF生成
    :return:
    """
    text = """

    """
    return text


def calculator():
    """
    聊天对话
    :return:
    """
    text = """

    """
    return text


def code_interpreter():
    """
    聊天对话
    :return:
    """
    text = """

    """
    return text


def background_to_image():
    """
    背景生成图片
    :return:
    """
    text = """

    """
    return text


def text_to_image_xufei():
    """文本生成图像 讯飞使用说明 """
    text = """ 格式:/文本生成图像#宽度#高度 文本内容  \n 参数的位置只能对应，可以不填任何参数或跳过中间的参数，跳过宽度 格式：/文本生成图像##高度 文本内容\n 
        示列：/文本生成图像#512#512 帮我画一条中国龙
    """
    return text