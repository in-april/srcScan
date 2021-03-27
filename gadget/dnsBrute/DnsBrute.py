import asyncio
import random
import time
import datetime
import aiodns
import platform
import sys
import re
from collections import defaultdict

from commonTools import ipTools
from dataIO import dataAccess
from config import config

if platform.system() == 'Windows':
    if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class SubNameBrute(object):

    def __init__(self, domain_url, task_count=500):
        self.domain_list = []
        self.count = defaultdict(int)
        self.flag = False
        self.ips = set()
        self.sum = 0
        self.subdomains = dataAccess.get_items('dict_subnames', {}, 'subname')
        self.dns_map = config.DNS_MAP.copy()

        self.domain_url = domain_url.strip()
        self.task_count = task_count

    def _dns_select(self):
        """
        根据权重选择dns
        :return: string
        """
        total = sum(self.dns_map.values())
        rad = random.randint(1, total)

        cur_total = 0
        res = ""
        for k, v in self.dns_map.items():
            cur_total += v
            if rad <= cur_total:
                res = k
                break
        return res

    async def _run(self):
        resolver = aiodns.DNSResolver()
        for subdomain in self.subdomains:
            subdomain = subdomain['subname']
            cur_domain = subdomain + '.' + self.domain_url
            try:
                nameserver = self._dns_select()
                resolver.nameservers = [nameserver]
                answers = await resolver.query(cur_domain, 'A')

                hosts = [answer.host for answer in answers]

                # A记录不存在，则跳过
                if len(hosts) == 0:
                    continue

                # 域名泛解析处理，同一ip出现10次，则不记录
                for host in hosts:
                    if host in self.ips:
                        self.count[str(host)] += 1
                    self.ips.add(host)
                    if self.count[str(host)] > 10:
                        self.flag = True
                if self.flag:
                    self.flag = False
                    continue

                dns_item = {'url': cur_domain, 'hosts': hosts, 'update': datetime.datetime.now()}
                self.domain_list.append(dns_item)
                # 存入数据库
                dataAccess.insert_item_no_repeat(dns_item, 'property_domain', 'url')
                # 增加字典权重
                dataAccess.update_dict_weight({'subname': subdomain}, 'dict_subnames')
                # 实时打印子域名
                # print(item.__repr__())
            except aiodns.error.DNSError as e:
                pass
            finally:
                # 动态改变dns权重
                self.dns_map[nameserver] += 1
                # 统计
                self.sum += 1
                sys.stdout.write('\r')
                sys.stdout.write('count:' + str(self.sum) + '  ')
                sys.stdout.write(self.dns_map.__repr__())
                sys.stdout.flush()

    async def async_run(self):
        tasks = [self._run() for _ in range(self.task_count)]
        await asyncio.gather(*tasks)

    def start(self):
        asyncio.run(self.async_run())


def run(domain, task_count=500):
    task = SubNameBrute(domain, task_count)
    task.start()

    # 生成c段，并保存
    c_list = set()
    for ip in task.ips:
        c_list.add(re.findall(r'\d+\.\d+\.\d+\.', ip)[0] + '0/24')
    for c in c_list:
        # 过滤内网ip段
        if ipTools.is_exclude_ip(c):
            continue
        now_date = datetime.datetime.now()
        item = {'ip_c': c.strip(), 'update': now_date}
        dataAccess.insert_item_no_repeat(item, 'task_ip_c', 'ip_c')

    print('\n' + domain.strip() + ' is complete.')


if __name__ == '__main__':
    start = time.perf_counter()
    run('baidu.com')
    print(f'Cost: {time.perf_counter() - start}')
