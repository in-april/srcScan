import pymongo
from config import config

client = pymongo.MongoClient(config.MONGODB)
db = client[config.DABATASE]


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


def insert_or_update(item, collection_name, *unique_names):
    """
    条件给出的数据存在则更新，不存在则插入
    :param item: 一条数据
    :param collection_name:
    :param unique_names: 保证唯一的字段名
    :return:
    """
    collection = db[collection_name]
    condition = {}
    for name in unique_names:
        condition[name] = item[name]
    result = collection.update_one(condition, {'$set': item}, True)
    return result


def update_dict_weight(condition, collection_name):
    """
    字典权重加一
    :param condition:
    :param collection_name:
    :return:
    """
    collection = db[collection_name]
    collection.update_one(condition, {'$inc': {'weight': 1}}, True)


def delete_item(collection_name, condition):
    """
    删除指定条目
    :param collection_name:
    :param condition:
    :return:
    """
    collection = db[collection_name]
    result = collection.delete_one(condition)
    return result


def get_items(collection_name, condition=None, *select_name):
    """
    获取查询游标
    :param collection_name: 集合名称
    :param condition: 筛选条件
    :param select_name: 要显示的列
    :return:
    """
    collection = db[collection_name]
    fields = {'_id': 0}
    for name in select_name:
        fields[name] = 1
    cursor = collection.find(condition, fields, no_cursor_timeout=True).batch_size(10000)
    yield from cursor
    cursor.close()


def get_items_no_cursor(collection_name, condition=None, *select_name):
    """
    获取查询游标
    :param collection_name: 集合名称
    :param condition: 筛选条件
    :param select_name: 要显示的列
    :return:
    """
    collection = db[collection_name]
    fields = {'_id': 0}
    for name in select_name:
        fields[name] = 1
    cursor = collection.find(condition, fields)
    return [item for item in cursor]


def get_items_random(collection_name, count, condition=None, *select_name):
    """
    随机取出count条数据，condition默认为status不存在或不包含'completed'
    :param collection_name:
    :param count:
    :param condition:
    :return:
    """
    fields = {'_id': 0}
    for name in select_name:
        fields[name] = 1

    if condition is None:
        condition = {'$match': {'$or': [{'status': {'$regex': '^((?!completed).)*$'}}, {'status': {'$exists': False}}]}}

    collection = db[collection_name]
    cursor = collection.aggregate([
        condition,
        {'$sample': {'size': count}},
        {'$project': fields},
    ])

    yield from [item for item in cursor]
    cursor.close()


def get_aggregate(collection_name, lookup):
    collection = db[collection_name]
    cursor = collection.aggregate([{'$lookup': lookup}])
    return [item for item in cursor]


if __name__ == '__main__':
    # update_dict_weight({'subname': 'www'}, 'dict_subnames')
    lookup = {
        'from': "property_hosts",
        'localField': "ip",
        'foreignField': "host",
        'as': 'tmp'
    }
    items = get_aggregate('property_services', lookup)
    pass
