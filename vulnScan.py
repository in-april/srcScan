import time
from gadget.vulnScan import vulnScan


def run_vuln_scan():
    """
    漏洞扫描
    参数为并发数
    :return:
    """
    vulnScan.run(100)


if __name__ == '__main__':
    run_vuln_scan()