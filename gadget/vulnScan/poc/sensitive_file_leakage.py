import asyncio
import datetime
import re
import sys
import aiohttp

from dataIO import dataAccess

"""
源码泄露poc：
检查项目：git，svn，/WEB-INF/web.xml，/.DS_Store，和一些常用压缩包，如：/www.zip，/1.zip等
payload设计：
content：判断响应体中是否包含所指定的字符串
type：判断content-type字段中的内容是否包含指定字符串
no_type：判断content-type字段中的内容是否不包含指定字符串
status：响应的状态码，等于==，大于>，小于<，三种
"""

payloads = [
    {'path': '/.git/config', 'content': '[core]', 'status': '<300'},
    {'path': '/.git/index', 'type': 'application/octet-stream', 'status': '<300'},
    {'path': '/.git/HEAD', 'content': 'refs/heads/octet-stream', 'status': '<300'},
    {'path': '/.svn/entries', 'content': '-props', 'status': '<300'},
    # {'path': '/WEB-INF/web.xml', 'content': '<?xml', 'status': '<300'},
    {'path': '/www.zip', 'type': 'application/octet-stream', 'status': '<300'},
    {'path': '/1.zip', 'type': 'application/octet-stream', 'status': '<300'},
    {'path': '/123.zip', 'type': 'application/octet-stream', 'status': '<300'},
    {'path': '/111.zip', 'type': 'application/octet-stream', 'status': '<300'},
    {'path': '/web.zip', 'type': 'application/octet-stream', 'status': '<300'},
    {'path': '/tmp.zip', 'type': 'application/octet-stream', 'status': '<300'},
    {'path': '/temp.zip', 'type': 'application/octet-stream', 'status': '<300'},
    {'path': '/backup.zip', 'type': 'application/octet-stream', 'status': '<300'},
    {'path': '/bak.zip', 'type': 'application/octet-stream', 'status': '<300'},
    {'path': '/wwwroot.zip', 'type': 'application/octet-stream', 'status': '<300'},
    {'path': '/uoload.zip', 'type': 'application/octet-stream', 'status': '<300'},
    {'path': '/website.zip', 'type': 'application/octet-stream', 'status': '<300'},
    {'path': '/.DS_Store', 'type': 'application/octet-stream', 'status': '<300'}
]


async def check(ip, port, host=None):
    # 若已知ip对应的域名，则在host字段加入域名，否则加入ip
    if host is None:
        host = ip
    try:
        time_out = aiohttp.ClientTimeout(total=30)
        conn = aiohttp.TCPConnector(ssl=False)
        # 伪造请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/83.0.4103.116 Safari/537.36",
            "Host": host
        }
        async with aiohttp.ClientSession(timeout=time_out, headers=headers, connector=conn) as session:
            for payload in payloads:
                url = 'http://' + ip + ":" + str(port) + payload['path']
                # print(url)
                async with session.request('get', url, allow_redirects=False) as resp:

                    real_content_type = resp.content_type  # 如果没有Content-Type字段，会默认为application/octet-stream
                    if resp.headers.get('Content-Type') is None:
                        real_content_type = ''

                    # if 'content_type' not in resp.headers['content_type']:
                    #     pass
                    real_status = resp.status
                    real_length = resp.content_length

                    content = payload.get('content')
                    status = payload.get('status')
                    resp_type = payload.get('type')
                    resp_no_type = payload.get('no_type')

                    # 若payload中不需要取出content，则不取出
                    real_content = ''
                    if content is not None:
                        real_content = await resp.text()

                    content_judge = 'content in real_content' if content else 'True'
                    status_judge = str(real_status) + status if status else 'True'
                    resp_type_judge = 'resp_type in real_content_type' if resp_type else 'True'
                    resp_no_type_judge = 'resp_type not in real_content_type' if resp_no_type else 'True'

                    expression = content_judge + ' and ' + status_judge + ' and ' + resp_type_judge + ' and ' + \
                                 resp_no_type_judge + ' and real_length > 100'
                    # print(expression)
                    if eval(expression):
                        time_now = datetime.datetime.now()
                        item = {'url': url, 'update': time_now, 'type': '源码泄露'}
                        dataAccess.insert_or_update(item, 'tmp3', 'url')
                        # print(url)

                    # 放入队列末尾，减少对同一站点的请求频率
                    await asyncio.sleep(0)
    except:
        # print(ex)
        pass
    finally:
        pass


async def run(items):
    for item in items:
        service = item['service']
        searchObj = re.search(r'http', service, re.I)
        if searchObj is None:
            continue
        await check(item['ip'], item['port'])


async def async_run(items, task_count=1):
    tasks = [run(items) for _ in range(task_count)]
    await asyncio.gather(*tasks)


def start(items, task_count):
    asyncio.run(async_run(items, task_count))


if __name__ == '__main__':
    pass
