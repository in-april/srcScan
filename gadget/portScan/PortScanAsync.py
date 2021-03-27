import asyncio
import datetime
import json
import os
from commonTools import ipTools
from config import config
from dataIO import dataAccess


class PortScan(object):

    def __init__(self, item_list, task_count=10, rate=1000):
        self.rate = rate
        self.masscan_path = os.path.join(config.ROOT_PATH, 'gadget', 'portScan', 'masscan.exe')
        self.item_list = item_list
        self.task_count = task_count

    async def _run(self):
        for item in self.item_list:
            ip = item['ip_c']
            output_filename = os.path.join(config.TMP_FILE_PATH, ip.replace('/', '_') + '.json')

            # 过滤内网ip段
            if ipTools.is_exclude_ip(ip):
                return

            # 读取常用端口列表
            ports = dataAccess.get_items('dict_ports', {}, 'port')
            port_list = ','.join([str(item['port']) for item in ports])
            cmd = [self.masscan_path] + ['--max-rate', str(self.rate)] + ['-p', port_list] + ['-oJ',
                                                                                              output_filename] + [ip]
            cmd = ' '.join(cmd)
            print(f'[start] [{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]', ip)

            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)

            stdout, stderr = await proc.communicate()
            # result = stdout.decode()

            time_now = datetime.datetime.now()
            time_now_string = time_now.strftime('%Y-%m-%d %H:%M:%S')

            with open(output_filename, 'r') as file:
                try:
                    result_list = json.loads(file.read())
                    for tmp in result_list:
                        service = {'ip': tmp['ip'], 'port': tmp['ports'][0]['port'], 'update': time_now}
                        dataAccess.insert_or_update(service, 'property_services', 'ip', 'port')
                except json.decoder.JSONDecodeError:
                    pass
                finally:
                    print(f'[completed] [{time_now_string}]', ip)

            # 修改任务状态
            item['status'] = 'completed'
            item['update'] = datetime.datetime.now()
            dataAccess.insert_or_update(item, 'task_ip_c', 'ip_c')

            # 删除临时文件
            os.remove(output_filename)

    async def async_run(self):
        tasks = [self._run() for _ in range(self.task_count)]
        await asyncio.gather(*tasks)

    def start(self):
        asyncio.run(self.async_run())


def run(task_count=10):
    # 取出status字段不为completed的数据进行爆破
    condition = {'$or': [{'status': {'$regex': '^((?!completed).)*$'}}, {'status': {'$exists': False}}]}
    scan = PortScan(dataAccess.get_items_no_cursor('task_ip_c', condition), task_count)
    scan.start()


if __name__ == '__main__':
    run()
