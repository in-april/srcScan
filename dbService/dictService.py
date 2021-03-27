import os
import sys
import time
import datetime
from dataIO import dataAccess
from config import config

dict_path = config.TMP_FILE_PATH


def insert_subname_dict_no_repeat(filename='subnames.txt'):
    """
    子域名爆破字典增量导入，重复则不添加，速度较慢
    :param filename:
    :return:
    """
    count = 0
    abspath = os.path.join(dict_path, filename)
    for subname in dataAccess.read_dict_file(abspath):
        now_date = datetime.datetime.now()
        tmp = {'subname': subname.strip(), 'update': now_date}
        dataAccess.insert_item_no_repeat(tmp, "dict_subnames", 'subname')

        # 计数
        count += 1
        sys.stdout.write('\r')
        sys.stdout.write('count:' + str(count) + '  ')


def insert_subname_dict(filename='subnames.txt'):
    """
    子域名爆破字典初次导入，速度快，但可能重复
    :param filename:
    :return:
    """
    itemList = []
    abspath = os.path.join(dict_path, filename)
    for subname in dataAccess.read_dict_file(abspath):
        now_date = datetime.datetime.now()
        tmp = {'subname': subname, 'update': now_date}
        itemList.append(tmp)
    dataAccess.insert_items(itemList, "dict_subnames")


def insert_port_dict(filename='port.txt'):
    """
    常用端口导入
    :param filename:
    :return:
    """
    count = 0
    abspath = os.path.join(dict_path, filename)
    for subname in dataAccess.read_dict_file(abspath):
        now_date = datetime.datetime.now()
        tmp = {'port': subname.strip(), 'update': now_date}
        dataAccess.insert_item_no_repeat(tmp, "dict_ports", 'port')

        # 计数
        count += 1
        sys.stdout.write('\r')
        sys.stdout.write('count:' + str(count) + '  ')


if __name__ == '__main__':
    start = time.perf_counter()
    # 字典导入
    # insert_subname_dict_no_repeat()
    # 常用端口导入
    insert_port_dict()
    print(f'Cost: {time.perf_counter() - start}')
