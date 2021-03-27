import datetime
from dataIO import dataAccess
from gadget.dnsBrute import DnsBrute


def run_task_subdomain_brute():
    """
    子域名爆破任务运行
    :return:
    """
    # 取出status字段不为completed的数据进行爆破
    condition = {'$or': [{'status': {'$regex': '^((?!completed).)*$'}}, {'status': {'$exists': False}}]}
    for item in dataAccess.get_items('task_subdomain_brute', condition):
        domain = item['domain']
        print(domain)
        DnsBrute.run(domain, 500)
        # 修改任务状态
        item['status'] = 'completed'
        item['update'] = datetime.datetime.now()
        dataAccess.insert_or_update(item, 'task_subdomain_brute', 'domain')


if __name__ == '__main__':
    run_task_subdomain_brute()
