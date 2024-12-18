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
        exit(1)  # 使用非零状态码表示异常退出
    manager = None
    try:
        manager = Manager(bot_config)
    except Exception as e:
        logging.error(f"初始化失败: {e}")
    finally:
        # 确保在程序退出时关闭会话处理的线程池
        if manager and manager.session_manager and manager.session_manager.session_handler:
            manager.session_manager.session_handler.shutdown()

