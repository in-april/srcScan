import os

# 路径信息
_current = os.path.dirname(__file__)
ROOT_PATH = os.path.abspath(os.path.join(_current, '..'))
TMP_FILE_PATH = os.path.abspath(os.path.join(_current, '..', 'tempfiles'))


# mongodb配置
MONGODB = 'mongodb://localhost:27017'
DABATASE = 'vuln'


# DNS服务器配置，数字为原始权重
DNS_MAP = {
    '119.29.29.29': 5,
    '114.114.114.114': 5,
    '223.5.5.5': 5,
    '223.6.6.6': 5,
    '180.76.76.76': 5,
    '8.8.8.8': 5,
    '8.8.4.4': 5,
    '123.125.81.6': 5
}

