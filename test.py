import os

import function

config = {
    'filepath': './data',
}
keys = ['wx', 'p', 'c']
# 假设这是 instruct_message 方法的一部分
save_path = function.filepath(os.path.join(
    config.get('filepath', './'),
    *keys,
    'image',
     'unknown.jpg'
))

print(save_path)