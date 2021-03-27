import os
import json
import datetime
from dataIO import dataAccess
from config import config

result_path = config.TMP_FILE_PATH


def insert_masscan_result(filename='result.json'):
    """
    从masscan中导入主机和端口列表
    :param filename:
    :return:
    """
    services = []
    abspath = os.path.join(result_path, filename)
    with open(abspath, 'r') as masscan_file:
        for item in json.loads(masscan_file.read()):
            service = {'ip': item['ip'], 'port': item['ports'][0]['port'], 'update': datetime.datetime.now()}
            services.append(service)
    dataAccess.insert_items(services, 'property_services')


def insert_dns_result(filename):
    """
    导入子域名数据
    :param filename:
    :return:
    """
    with open(filename, 'r') as dns_file:
        for item in json.loads(dns_file.read()):
            dns = {'url': item['url'], 'hosts': item['hosts'], 'update': datetime.datetime.now()}
            print(dns)
            dataAccess.insert_item_no_repeat(dns, 'property_domain', 'url')


def generate_property_hosts():
    """
    生成主机表，用于存储主机信息，包括主机ip，域名列表，时间等
    :return:
    """
    for result in dataAccess.get_items('property_domain'):
        hosts = result['hosts']
        for host in hosts:
            item = {'host': host, 'update': datetime.datetime.now()}
            dataAccess.insert_item_no_repeat(item, 'property_hosts', 'host')

    for result in dataAccess.get_items('property_hosts'):
        host = result['host']
        domains = result.get('domains')
        if domains is None:
            domains = []
        oldset = set(domains)

        for item in dataAccess.get_items('property_domain', {'hosts': {'$in': [host]}}):
            oldset.add(item['url'])

        new_domains = list(oldset)
        result['domains'] = new_domains
        dataAccess.insert_or_update(result, 'property_hosts', 'host')


if __name__ == '__main__':
    generate_property_hosts()
