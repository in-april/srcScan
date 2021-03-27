import random

from dataIO import dataAccess
from gadget.vulnScan.poc import sensitive_file_leakage


def run(task_count=500):
    condition = {'port_state': 'open', 'status': 'completed',
                 '$and': [{'service': {'$ne': 'unknown'}}, {'service': {'$ne': 'tcpwrapped'}},
                          {'service': {'$ne': ''}}]}
    items = dataAccess.get_items('property_services', condition, 'ip', 'port', 'service')

    # 传递给具体的扫描程序
    sensitive_file_leakage.start(items, task_count)
