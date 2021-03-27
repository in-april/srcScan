import os
import pymongo
import datetime
import re

# mongodb配置
MONGODB = 'mongodb://localhost:27017'
DABATASE = 'vuln1'

client = pymongo.MongoClient(MONGODB)
db = client[DABATASE]
dict_path = os.path.dirname(__file__)

def read_dict_file(filename):
    """
    读取字典文件
    :param filename:
    :return: 字典文件的生成器
    """
    with open(filename, 'r') as dict_file:
        yield from dict_file

def insert_item_no_repeat(item, collection_name, *unique_names):
    """
    不重复插入数据，适合新增
    :param item: 一条数据
    :param collection_name:
    :param unique_names: 保证唯一的字段名
    :return:
    """
    collection = db[collection_name]
    condition = {}
    for name in unique_names:
        condition[name] = item[name]
    result = collection.update_one(condition, {'$setOnInsert': item}, True)
    return result


def insert_items(item_list, collection_name):
    """
    批量插入，适合初次导入
    :param item_list:
    :param collection_name:
    :return:
    """
    collection = db[collection_name]
    result = collection.insert_many(item_list)
    return result


def insert_subname_dict(filename='subnames.txt'):
    """
    子域名爆破字典初次导入，速度快，但可能重复
    :param filename:
    :return:
    """
    itemList = []
    abspath = os.path.join(dict_path, filename)
    for subname in read_dict_file(abspath):
        now_date = datetime.datetime.now()
        tmp = {'subname': subname.strip(), 'update': now_date}
        itemList.append(tmp)
    insert_items(itemList, "dict_subnames")
    print('子域名字典导入完成')


def insert_port_dict(filename='port.txt'):
    """
    常用端口导入
    :param filename:
    :return:
    """
    count = 0
    abspath = os.path.join(dict_path, filename)
    for subname in read_dict_file(abspath):
        now_date = datetime.datetime.now()
        tmp = {'port': subname.strip(), 'update': now_date}
        insert_item_no_repeat(tmp, "dict_ports", 'port')
    print('端口字典导入完成')


def insert_src_domain(filename='src.txt'):
    """
    导入主域名
    :param filename:
    :return:
    """
    filepath = os.path.join(dict_path, filename)
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
                insert_item_no_repeat(src, 'task_subdomain_brute', 'domain')
    print('主域名导入完成')


if __name__ == '__main__':
	insert_port_dict()
	insert_subname_dict()
	insert_src_domain()