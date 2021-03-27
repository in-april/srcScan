import asyncio
import datetime
import re

from dataIO import dataAccess


class ServiceProbe(object):

    def __init__(self, item_list, task_count=100):
        self.item_list = item_list
        self.task_count = task_count
        self.compile = re.compile(r'Ports: (?:\d+)/(.*?)/(.*?)//(.*?)//(.*?)/')

    async def _run(self):
        for item in self.item_list:
            ip = item['ip']
            port = item['port']
            # print(item)
            # 跳过主机发现，不进行dns解析，扫描具体版本
            cmd = f'nmap -Pn -T4 -n {ip} -p {port} -sV -oG -'
            # cmd = f'nmap -Pn -T4 0.1.2.3 -p 8000 -sV -oG -'

            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)

            stdout, stderr = await proc.communicate()
            result = stdout.decode()
            # print(result)

            searchObj = self.compile.search(result)

            # 写入识别后的信息
            item['port_state'] = searchObj.group(1)
            item['protocol'] = searchObj.group(2)
            item['service'] = searchObj.group(3)
            item['version'] = searchObj.group(4)
            item['update'] = datetime.datetime.now()
            item['status'] = 'completed'

            print(item)
            dataAccess.insert_or_update(item, 'property_services', 'ip', 'port')

    async def async_run(self):
        tasks = [self._run() for _ in range(self.task_count)]
        await asyncio.gather(*tasks)

    def start(self):
        asyncio.run(self.async_run())


def run(count=10000, task_count=100):
    services_list = dataAccess.get_items_random('property_services', count)
    scan = ServiceProbe(services_list, task_count)
    scan.start()


if __name__ == '__main__':
    run()
