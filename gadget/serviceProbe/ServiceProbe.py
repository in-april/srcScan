import asyncio
import sys

from dataIO import dataAccess

"""
目前废弃
"""


class ServiceProbe(object):

    def __init__(self, task_count=500):
        self.service_list = dataAccess.get_items('property_services')
        self.task_count = task_count
        self.count = 0

    async def service_probe(self):
        for item in self.service_list:
            ip = item['ip']
            port = item['port']
            try:
                item = {"ip": ip, "port": port, "server": None}
                con = asyncio.open_connection(ip, port)
                reader, writer = await asyncio.wait_for(con, timeout=10)
                message = 'test\r\n'
                writer.write(message.encode())
                await writer.drain()
                writer.write_eof()

                data = await asyncio.wait_for(reader.readline(), timeout=10)
                data = data.decode('latin-1').lower()
                # print(data)
                if 'http' in data:
                    item["server"] = "http"
                elif 'mysql' in data:
                    item["server"] = "mysql"
                elif '-ERR unknown comma'.lower() in data:
                    item["server"] = "redis"
                else:
                    item["server"] = "unknown"

            except Exception as e:
                print(e)
            finally:
                self.count += 1
                sys.stdout.write('\r')
                sys.stdout.write('count:' + str(self.count) + '  ')
                writer.close()

    async def async_run(self):
        tasks = [self.service_probe() for _ in range(self.task_count)]
        await asyncio.gather(*tasks)

    def run(self):
        asyncio.run(self.async_run())


if __name__ == '__main__':
    probe = ServiceProbe()
    probe.run()
