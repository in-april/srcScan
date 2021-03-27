import time
from gadget.serviceProbe import ServiceProbeNmap


def run_service_probe():
    """
    服务识别
    随机取出未进行识别的条目，进行识别
    :return:
    """
    while True:
        ServiceProbeNmap.run(count=10000, task_count=50)
        time.sleep(10)


if __name__ == '__main__':
    run_service_probe()
