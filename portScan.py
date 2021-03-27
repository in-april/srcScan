import datetime
import json

from dataIO import dataAccess
from gadget.portScan import PortScanAsync

# C段扫描
def run_task_ip_c():
    PortScanAsync.run(5)


if __name__ == '__main__':
    run_task_ip_c()
