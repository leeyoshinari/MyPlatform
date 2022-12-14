# MyPlatform
[English Document](https://github.com/leeyoshinari/MyPlatform/blob/main/README.md)

## 介绍
这是一个主要用于性能测试的平台，先简单介绍一下这个平台具有的功能：<br>
1、服务器管理，可以统一查看服务器的基本信息；<br>
2、Shell 远程连接，支持本地和服务器之间的文件上传和下载；<br>
3、服务器资源监控；<br>
4、Nginx 访问日志流量收集；<br>
5、性能测试工具，提供自动化压测和分布式压测的能力；<br>

## 项目目录
- MyPlatform - 项目文件
- staticfiles - 静态文件
- templates - 模板文件
- templateFilter - 模板自定义过滤器
- common - 通用的方法
- user - 用户相关
- shell - shell 工具
- monitor - 监控工具
- performance - 性能测试平台

## 第三方组件
- 关系型数据库：SQLite3 或 MySQL - 用于存储平台数据
- 时序数据库：InfluxDB - 用于存储监控数据
- 键值数据库：Redis - 用于集群/分布式数据同步
- 文件服务器：MinIO - 用于存储文件
- 性能测试工具：JMeter - 用于执行 JMeter 脚本

## 架构图
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/myPlarform.png)
如需满足较多用户使用，请部署集群；如需高可用，请自行部署keepalive。

#### 说明
**[collector-agent](https://github.com/leeyoshinari/collector_agent )**<br>
数据收集工具。所有agent的数据都会发给collector-agent，然后由collector-agent统一写InfluxDB/写redis。<br>
这样可以避免：如果每个agent单独连接数据库，可能会导致数据库连接不够用或者超过服务器允许的连接数。但也会有一个问题：如果agent太多，导致collector-agent不能及时写库，那就增大collector-agent的线程池大小，如果还不行，那就集群部署，增加集群节点。

**[monitor-agent](https://github.com/leeyoshinari/monitor_agent )**<br>
服务器资源监控工具。通过执行Linux命令实时采集服务器的 CPU、内存、磁盘、网络、TCP 等数据。

**[nginx-agent](https://github.com/leeyoshinari/nginx_agent )**<br>
nginx流量采集工具。通过实时处理nginx的访问日志(access.log)，将接口的访问信息(访问时间、客户端IP、接口名称、请求方法、协议、状态码、响应体大小、响应时间)等存储到数据库。<br>

**[jmeter-agent](https://github.com/leeyoshinari/jmeter_agent )**<br>
性能测试执行工具。通过调用JMeter执行性能测试，支持分布式压测和全链路压测。

## 部署
1、克隆 
```shell script
git clone https://github.com/leeyoshinari/MyPlatform.git
``` 

2、安装 MySQL(SQLite3不用安装，可直接使用)、InfluxDB、Redis、MinIO(可选安装，不安装文件存本地)；（ps：暂不支持 InfluxDB2.x 版本，建议安装[ influxdb-1.8.3](https://dl.influxdata.com/influxdb/releases/influxdb-1.8.3.x86_64.rpm )）

3、安装第三方依赖包 
```shell script
pip3 install -r requirements.txt
```

4、修改配置文件`config.conf`；

5、数据库初始化，依次执行下面命令；
```shell script
python3 manage.py migrate
python3 manage.py makemigrations shell performance
python3 manage.py migrate
```

6、创建超级管理员账号；
```shell script
python3 manage.py createsuperuser
```

7、数据初始化，不初始化会导致报错；
```shell script
python3 manage.py loaddata initdata.json
```

8、处理所有静态文件；
```shell script
python3 manage.py collectstatic --clear --noinput
```

9、压缩静态文件（css 和 js）；
```shell script
python3 manage.py compress --force
```

10、修改`startup.sh`中的端口号；

11、部署`nginx`，location相关配置如下：(ps: 下面列出的配置中的`platform`是url路径中的prefix，即url前缀，可根据自己需要修改)<br>
（1）upstream 配置
```shell script
upstream myplatform-server {
    server 127.0.0.1:15200;
    server 127.0.0.1:15201;
}
```
（2）静态请求：通过 nginx 直接访问静态文件，配置静态文件路径
```shell script
location /platform/static {
    alias /home/MyPlatform/static;
}
```
（3）动态http请求：
```shell script
location /platform {
     proxy_pass  http://myplatform-server;
     proxy_set_header Host $proxy_host;
     proxy_set_header X-Real-IP $remote_addr;
     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```
（4）websocket协议通信：
```shell script
location /shell {  # 必须是shell，不能修改
    proxy_pass http://myplatform-server;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

12、启动
```shell script
sh startup.sh
```
   停止请执行 `sh shutdown.sh`

13、访问页面，url是 `http://ip:port/config.conf中的prefix`
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/home.JPG)

14、访问权限控制页面，url是 `http://ip:port/config.conf中的prefix/admin`

15、部署数据收集工具，[快点我](https://github.com/leeyoshinari/collector_agent)

16、部署服务器资源监控执行工具，[快点我](https://github.com/leeyoshinari/monitor_agent)

17、部署性能测试执行工具，[快点我](https://github.com/leeyoshinari/jmeter_agent)

18、部署Nginx流量采集工具，[快点我](https://github.com/leeyoshinari/nginx_agent)

## 注意
1、如需了解更多消息，[请点我](https://github.com/leeyoshinari/MyPlatform/blob/main/templates/course_zh.md) ，或者部署后查看教程。

2、由于本人只有一台云服务器，故未进行大规模集群验证和大规模分布式、全链路压测验证，仅验证集群功能和分布式压测功能。如您在使用中发现问题，欢迎反馈。

## Requirements
本地开发环境：
- python 3.9.10

第三方包的版本：
- aiohttp==3.7.4.post0
- aiohttp-jinja2==1.5
- channels==3.0.4
- daphne==3.0.2
- Django==4.0.1
- django-compressor==4.1
- influxdb==2.6.0
- Jinja2==3.0.3
- minio==7.1.3
- paramiko==2.10.3
- PyMySQL==1.0.2
- redis==4.1.1
- requests==2.27.1
- sqlparse==0.4.2
