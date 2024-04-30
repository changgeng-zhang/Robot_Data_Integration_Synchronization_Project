import hashlib
import json
import time
from datetime import datetime

import requests

# 获取当前时间的毫秒数
epoch_milli = int(datetime.now().timestamp() * 1000)
print(epoch_milli)

# 将毫秒数转换为字符串
msg = str(epoch_milli)

# 计算消息的 MD5 哈希值
md5_hash = hashlib.md5(msg.encode('utf-8')).hexdigest()
print(md5_hash)


def requests_get():
    url = 'http://47.100.224.126/des/api/equ/herun/monitor/deviceWorkData'
    timestamp = epoch_milli
    signature = md5_hash
    headers = {"Content-Type": "application/json", "Charset": "UTF-8", "timestamp": str(timestamp), "signature": signature}
    try:
        res = requests.get(url=url, headers=headers)
        if res.status_code == 200:
            try:
                response_content = res.json()
                print(response_content)
            except json.decoder.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
        else:
            print(f"Failed to retrieve data. Status code: {res.status_code}")
    except Exception as err:
        raise err


def call_a_every_second():
    try:
        while True:
            requests_get()  # 调用方法
            time.sleep(1)  # 等待 1 秒钟
    except KeyboardInterrupt as err:
        print("Requests stop.")


# 调用每秒调用一次 a 方法的函数
call_a_every_second()
