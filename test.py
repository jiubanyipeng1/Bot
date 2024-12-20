
import os

# 获取 napcat 文件夹及其所有子目录和文件
napcat_files = []
for root, dirs, files in os.walk('napcat.29927.onekey'):
    for file in files:
        source_path = os.path.join(root, file)
        relative_path = os.path.relpath(root, 'napcat.29927.onekey')
        # 确保 target_path 是相对于 napcat 的相对路径
        target_path = os.path.join('napcat.29927.onekey', relative_path)
        napcat_files.append((source_path, target_path))

other_files = [('gptapi', '.'), ('cache_manager.py', '.'), ('configuration.py', '.'),
               ('function.py', '.'), ('help.py', '.')
, ('manager.py', '.'), ('qq_bot.py', '.'), ('session_handler.py', '.'),
                ('session_manager.py', '.'), ('web_bot.py', '.'), ('weixin_bot.py', '.')]

files = napcat_files + other_files

print(files)