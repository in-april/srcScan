import datetime
import json
import os
import re

from config import config
from dataIO import dataAccess
from commonTools import ipTools

result_path = config.TMP_FILE_PATH


def insert_ip_c():
    """
    导入待扫描的c段ip，TMP_FILE_PATH目录下的*_c.txt文件
    :return:
    """
    for name in os.listdir(result_path):
        filepath = os.path.join(result_path, name)
        if os.path.isfile(filepath):
            if filepath.endswith("_c.txt"):
                with open(filepath, 'r') as ip_c_file:
                    for item in ip_c_file:
                        item = item.strip()
                        ip_c = {'ip_c': item, 'status': 'completed', 'update': datetime.datetime.now()}
                        print(ip_c)
                        dataAccess.insert_item_no_repeat(ip_c, 'task_ip_c', 'ip_c')


def insert_src_domain(filename='src.txt'):
    """
    导入主域名
    :param filename:
    :return:
    """
    filepath = os.path.join(result_path, filename)
    with open(filepath, 'r', encoding='utf-8') as src_file:
        for item in src_file:
            item = item.strip()
            tmps = re.split(r' +', item)
            # print(tmps)
            src = {'belong': tmps[0]}
            for tmp in tmps[1:]:
                src['domain'] = tmp
                src['update'] = datetime.datetime.now()
                src['status'] = 'not_started'
                dataAccess.insert_item_no_repeat(src, 'task_subdomain_brute', 'domain')


def filter_ip_c():
    """
    过滤数据库中的内网C段
    :return:
    """
    for item in dataAccess.get_items('task_ip_c', {}, 'ip_c'):
        if ipTools.is_exclude_ip(item['ip_c']):
            print(item)
            dataAccess.delete_item('task_ip_c', item)


if __name__ == '__main__':
    filter_ip_c()
