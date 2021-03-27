# srcScan 
## src自动挖掘工具
    特点：适合大范围扫描漏洞，由于范围大，访问分散，所以几乎不会出现被封ip的情况。
    使用了mongo数据库，方便信息的统一管理
    整体使用了异步io的方式实现，执行效率高

## 功能介绍
    功能模块分为：子域名爆破，端口扫描，服务探测，漏洞扫描
    子域名爆破：根据字典爆破子域名，可根据dns服务器的响应速度动态调整dns服务器
    端口扫描：使用了masscan，将任务分配给多个masscan进程
    服务探测：使用了nmap，将任务分配给多个nmap进程
    漏洞扫描：目前只实现了对敏感文件的扫描

## 数据库结构介绍
    dict_ports：常用端口字典，用于masscan端口扫描
    dict_ports：子域名字典，用于子域名爆破
    property_domain：爆破出的子域名信息，url与ip一对多
    property_hosts：为了操作方便生成的ip域名对应表，ip与url一对多
    property_services：masscan和nmap生成的结果，包括ip，端口，服务名
    task_subdomain_brute：初始的主域名，程序的后续操作数据都是根据主域名展开的。
    task_ip_c：子域名爆破后，根据ip生成对应的c段地址，用于masscan的端口扫描
    tmp：漏洞扫描的结果

## 使用方法
    安装依赖：pip install -r requirements.txt
    运行 初始化脚本/init.py （初始化数据库，src.txt中为默认的主域名，根据需要更改，要先配置好mongodb）
    依次运行：
    subdomainBrute.py（子域名爆破）
    portScan.py（端口扫描，linux环境要先安装masscan）
    serviceProbe.py（服务探测，要先安装好nmap）
    vulnScan.py（漏洞扫描）
