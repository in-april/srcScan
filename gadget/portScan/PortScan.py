import os
from multiprocessing import Process, Pipe
import subprocess
from commonTools import ipTools
from config import config
from dataIO import dataAccess

"""
目前废弃
"""


class PortScan(object):

    def __init__(self, ip, rate=10000, create_new_console=False):
        self.ip = ip
        self.output_filename = os.path.join(config.TMP_FILE_PATH, ip.replace('/', '_') + '.json')
        self.rate = rate
        self.masscan_path = os.path.join(config.ROOT_PATH, 'gadget', 'portScan', 'masscan.exe')
        # masscan是否创建新窗体，默认false
        self.create_new_console = create_new_console

    def start(self, conn):
        # 过滤内网ip段
        if ipTools.is_exclude_ip(self.ip):
            conn.send(None)
            return

        # 读取常用端口列表
        ports = dataAccess.get_items('dict_ports', {}, 'port')
        port_list = ','.join([str(item['port']) for item in ports])
        cmd = [self.masscan_path] + ['--max-rate', str(self.rate)] + ['-p', port_list] + ['-oJ',
                                                                                          self.output_filename] + [
                  self.ip]
        print(cmd)

        if not self.create_new_console:
            subprocess.call(cmd)
        else:
            subprocess.call(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        conn.send(self.output_filename)


def run(ip, rate=10000):
    """
    接收要扫描的c段ip，返回masscan扫描结果
    :param ip:
    :param rate:
    :return:
    """
    parent_conn, child_conn = Pipe()
    scan = PortScan(ip, rate)
    p = Process(target=scan.start, args=(child_conn,))
    p.start()
    p.join()
    return parent_conn.recv()


if __name__ == '__main__':
    run('39.156.69.79')
