import IPy


def is_exclude_ip(ip):
    """
    判断是否是被排除的ip
    :param ip:
    :return:
    """
    flag = False
    exclude_ips = ['192.168.0.0/16', '10.0.0.0/8', '172.16.0.0/12', '127.0.0.0/8', '0.0.0.0/8']
    for exclude in exclude_ips:
        if ip in IPy.IP(exclude):
            flag = True
    return flag


if __name__ == '__main__':
    print(is_exclude_ip('10.0.0.0/12'))
