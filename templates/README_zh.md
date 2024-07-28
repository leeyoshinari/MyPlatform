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

15、如需了解更多信息，请[点我](https://blog.ihuster.top)。
