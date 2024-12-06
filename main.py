# -*- coding: utf-8 -*-
import logging
import time
from configuration import load_config
from manager import Manager


if __name__ == "__main__":
    # 初始化日志记录
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        encoding='utf-8',
        datefmt="%Y-%m-%d %H:%M:%S"
        )

    bot_config = load_config()
    if not bot_config:
        logging.error("配置加载失败")
        time.sleep(5)
        exit()

    manager = Manager(bot_config)

    # 保持进程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("程序终止")