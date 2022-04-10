# MyPlatform

## 功能
- 服务器基本信息统一查看<br>
- 通过浏览器打开服务器shell<br>
- 文件上传到服务器，或从服务器下载文件<br>
- 集成服务器资源监控服务<br>
- 支持权限控制<br>

## 技术选型
- 系统框架：django<br>
- 数据库：django支持的所有关系型数据库<br>

## 部署
1、克隆 `git clone https://github.com/leeyoshinari/MyPlatform.git` ；

2、进入目录 `cd MyPlatform`，修改配置文件`config.conf`；

3、数据初始化，依次执行下面命令；<br>
**注意：`config.conf` 中的 `isMonitor` 必须为0，否则数据初始化存在小问题；数据初始化完成后可再修改为1**
```shell script
python3 manage.py migrate
python3 manage.py makemigrations shell
python3 manage.py sqlmigrate shell 0001
python3 manage.py migrate
```

4、创建超级管理员账号；
```shell script
python3 manage.py createsuperuser
```

5、修改`startup.sh`中的端口号；

6、部署`nginx`，location相关配置如下：(ps: 下面列出的配置中的`tencent`是url上下文，即url前缀，可根据自己需要修改)<br>
（1）静态请求：通过nginx直接访问静态文件，配置静态文件路径
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

7、启动
```
sh startup.sh
```

8、访问页面，url是 `http://ip:port/上下文`
![]()

9、访问权限控制页面，url是 `http://ip:port/上下文/admin`

## 使用
1、创建用户：使用超级管理员账号登陆权限管理页面，创建用户；

2、创建用户组：登陆系统，创建用户组；

3、把用户添加到用户组中，管理员用户默认添加到所有用户组中；

4、录入服务器连接信息；设置服务器所属的用户组；

5、用户登陆系统后，用户只能看到自己组中的服务器；

6、点击`OpenShell`，即可打开 shell；

7、上传/下载文件，需要输入文件要上传的路径和下载的文件的路径；

8、部署服务器监控，点击`DeployMonitor`，部署成功后，可点击`ViewMonitor`查看监控，也可点击`StopMonitor`停止监控；

9、点击`Delete`，即可从用户组中删除服务器信息；

## Requirements
- Django>=4.0.1
- PyMySQL>=1.0.2
- paramiko>=2.10.3
- channels>=3.0.4
- python 3.7+
