# MyPlatform
这是一个集成了一些工具的平台

## 目录
- MyPlatform - 项目文件
- static - 静态文件
- templates - 模板文件
- templateFilter - 模板自定义过滤器
- common - 通用的函数
- user - 用户相关
- shell - shell 工具
- monitor - 监控工具
- mitm - http 请求拦截工具
- performance - 性能测试平台(doing)


## 其他组件
- 关系型数据库：SQLite3 or MySQL - 用于存储平台数据
- 时序数据库：InfluxDB - 用于存储监控数据
- 键值数据库：Redis - 用于进程间数据传递 和 集群部署数据同步(doing)
- 拦截工具：MitmProxy - 用于拦截 HTTP 请求
- 性能测试工具： JMeter - 用于执行 JMeter 脚本

## 介绍
1、shell<br>
在浏览器上打开 shell 页面，连接linux，可以输入 shell 命令，支持文件上传和下载；[详见README.md](https://github.com/leeyoshinari/MyPlatform/tree/main/shell)

2、monitor<br>
监控服务器资源(CPU、内存、磁盘、网络等)使用情况；[详见README.md](https://github.com/leeyoshinari/MyPlatform/tree/main/monitor)

3、mitm<br>
拦截指定的 HTTP 协议请求，可直接返回响应值，或修改请求参数或响应值；[详见README.md](https://github.com/leeyoshinari/MyPlatform/tree/main/mitm)

4、performance
性能测试工具，底层是JMeter；[详见README.md](https://github.com/leeyoshinari/MyPlatform/tree/main/performance)


## 部署
1、克隆 `git clone https://github.com/leeyoshinari/MyPlatform.git` ；

2、进入目录 `cd MyPlatform`，修改配置文件`config.conf`；

3、数据初始化，依次执行下面命令；<br>
**注意：`config.conf` 中的 `isMonitor` 必须为0，否则数据初始化存在小问题；数据初始化完成后可再修改为1**
```shell script
python3 manage.py migrate
python3 manage.py makemigrations
python3 manage.py migrate
```

4、创建超级管理员账号；
```shell script
python3 manage.py createsuperuser
```

5、数据初始化，不初始化会导致上次jmeter文件报错；
```shell script
python3 manage.py loaddata initdata.json
```

6、处理admin页面的静态文件；
```shell script
python3 manage.py collectstatic
```

7、修改`startup.sh`中的端口号；

8、部署`nginx`，location相关配置如下：(ps: 下面列出的配置中的`tencent`是url上下文，即url前缀，可根据自己需要修改)<br>
（1）静态请求：通过 nginx 直接访问静态文件，配置静态文件路径
```shell script
location /tencent/static {
    alias /home/MyPlatform/static;
}
```
（2）动态http请求：
```shell script
location /tencent {
     proxy_pass  http://127.0.0.1:15200;
     proxy_set_header Host $proxy_host;
     proxy_set_header X-Real-IP $remote_addr;
     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```
（3）websocket协议通信：
```shell script
location /shell {  # 必须是shell
    proxy_pass http://127.0.0.1:15200;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

9、启动
```
sh startup.sh
```

10、访问页面，url是 `http://ip:port/上下文`

11、访问权限控制页面，url是 `http://ip:port/上下文/admin`

