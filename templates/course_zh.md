# 介绍
这是一个主要用于性能测试的平台，先简单介绍一下这个平台具有的功能：<br>
1、服务器管理，可以统一查看服务器的基本信息；<br>
2、Shell 远程连接，支持本地和服务器之间的文件上传和下载；<br>
3、服务器资源监控；<br>
4、Nginx 访问日志流量收集；<br>
5、性能测试工具，提供自动化压测和分布式压测的能力；<br>

# 项目目录
- MyPlatform - 项目文件
- staticfiles - 静态文件
- templates - 模板文件
- templateFilter - 模板自定义过滤器
- common - 通用的方法
- user - 用户相关
- shell - shell 工具
- monitor - 监控工具
- performance - 性能测试平台

# 第三方组件
- 关系型数据库：SQLite3 或 MySQL - 用于存储平台数据
- 时序数据库：InfluxDB - 用于存储监控数据
- 键值数据库：Redis - 用于集群/分布式数据同步
- 文件服务器：MinIO - 用于存储文件
- 性能测试工具：JMeter - 用于执行 JMeter 脚本

# 架构图
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/myPlarform.png)
如需满足较多用户使用，请部署集群；如需高可用，请自行部署keepalive。

### 说明
**collector-agent**<br>
数据收集工具。所有agent的数据都会发给collector-agent，然后由collector-agent统一写InfluxDB/写redis。<br>
这样可以避免：如果每个agent单独连接数据库，可能会导致数据库连接不够用或者超过服务器允许的连接数。但也会有一个问题：如果agent太多，导致collector-agent不能及时写库，那就增大collector-agent的线程池大小，如果还不行，那就集群部署，增加集群节点。

**monitor-agent**<br>
服务器资源监控工具。通过执行Linux命令实时采集服务器的 CPU、内存、磁盘、网络、TCP 等数据。

**nginx-agent**<br>
nginx流量采集工具。通过实时处理nginx的访问日志(access.log)，将接口的访问信息(访问时间、客户端IP、接口名称、请求方法、协议、状态码、响应体大小、响应时间)等存储到数据库。<br>

**jmeter-agent**<br>
性能测试执行工具。通过调用JMeter执行性能测试，支持分布式压测和全链路压测。

# 第三方包
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

# 部署
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

# Shell 工具
该工具可以查看管理服务器，并可以直接在浏览器上远程连接 Linux。
支持权限控制，将用户添加进项目组中，用户就只能看到项目组下的服务器，可以避免未授权的访问。
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/shell_home.JPG)
## 设置项目组
点击 Create Group 创建项目组，需要设置项目组和项目组应用的唯一标识符。唯一标识符一般在整个公司是唯一的，对于在服务器上，通过`ps -ef | grep 唯一标识符 | grep -v grep` 命令可以查找到唯一一个进程。<br>
该按钮仅管理员可见。
## 设置服务器所在机房
点击 Create Server Room 创建机房，设置机房时主要有3个选项，分别是用于应用、用于中间件、用于压测。为什么有这3个呢？<br>
例如一个机房有100台服务器，项目组A用了40台部署自己的服务，项目组B也用了40台部署自己的服务，还有10台服务器部署了中间件，剩余10台可以用于压测，这3个选项就用于区分这些类型。因为这个项目把服务器管理、服务器监控和压测整合在一起了，为了能够区分，所以才加了3个选项；不像大公司的平台都是不同的人开发的不同的应用，只是把前端页面挂在一起。<br>

一般性能测试需要施压机和被测服务所在服务器在同一个机房，如果你就想跨机房压测，可以把不是同一个机房的服务器设置成同一个机房，假装它们在一起。<br>
该按钮仅管理员可见
## 添加服务器
点击 Add Server 创建服务器，这里需要设置服务器所属项目组、所在的机房、以及服务器IP、用户名和登录密码。
## 用户管理
点击 Add User 将用户添加到某个项目组中 或 从某个项目组中移除。添加用户后，该用户就可以看到并访问这个项目组中的所有服务器。管理员默认可以查看所有服务器。<br>
该按钮仅管理员可见
## 服务器列表
每个添加的服务器都会展示在列表中，可以概览服务器的基本信息（系统、CPU、内存、磁盘）。Action 列可以操作服务器，在这里可以打开 Shell 远程连接 Linux；其中的编辑和删除的功能仅创建人和管理员可见。
## 远程连接服务器
点击 OpenShell 即可打开 Shell 远程连接 Linux，可以同时打开很多个页面，如下:
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/shell_ternimal.JPG)

为了提供更好的使用体验，提供了 Ctrl+C（复制）和 Ctrl+V（粘贴）快捷键，不仅如此，还仍然保留了 Ctrl+C 快捷键在 shell 中的终止前台进程的功能，而绝大部分主流 shell 工具是不支持这种功能的，老板再也不担心你敲命令慢了。<br>

在打开的 Shell 中，可以上传文件到服务器，或者下载文件到本地。为了安全，上传和下载的入口也是可以关闭的。<br>
- 在上传文件时，首先会弹出输入框，需要填入文件上传到哪个目录（绝对路径，不填默认 /home 目录），然后选择文件上传。<br>
- 在下载文件时，也会弹出输入框，需要填入文件的完整路径（绝对路径），必须填文件路径，不能填目录路径，然后可通过浏览器下载到本地。<br>

## 自动部署Agent
点击 Deploy 会打开新的页面，这个页面可以上传部署包、自动部署和卸载。<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/shell_deploy.JPG)
由于一些部署包区分Linux发行版本和CPU架构，故需要先准备好对应的部署包，然后上传到平台，通过该平台进行部署。如果部署包不区分Linux发行版本和CPU架构，上传部署包时可随意选择一种。
该平台下面的所有agent都可以且只能通过该平台自动部署（当前只支持部署 java、jmeter、[collector-agent](https://github.com/leeyoshinari/collector_agent) 、[monitor-agent](https://github.com/leeyoshinari/monitor_agent) 、[jmeter-agent](https://github.com/leeyoshinari/jmeter_agent) 、[nginx-agent](https://github.com/leeyoshinari/nginx_agent) ）。为了方便部署，所有的agent的配置文件已经简化到不能再简化了，一般情况下不需要修改任何配置，所有的配置都从平台自动获取。建议部署顺序：先部署Java(仅施压机部署且没有部署过)，再部署JMeter(仅施压机部署)，再部署collector-agent，剩下就部署其他需要部署的agent了。<br>

在点击部署/卸载前，请仔细核对当前服务器的Linux系统发行版本和CPU架构是否和部署包的Linux系统发行版本和CPU架构一致。<br>
注：极少数情况下需要修改agent配置文件，例如：你的nginx部署方式和99%的人都不一样，无法自动获取nginx的日志路径，这时就需要修改配置文件。

# 服务器资源监控
该工具（[快点我部署](https://github.com/leeyoshinari/monitor_agent) ）主要用于监控服务器资源使用情况，主要有一下功能：
- 监控整个服务器的CPU使用率、io wait、内存使用、磁盘IO、网络带宽和TCP连接数<br>
- 监控端口的 TCP 状态<br>
- 针对java应用，可以监控jvm大小和垃圾回收情况；当Full GC频率过高时，可发送邮件提醒<br>
- 系统CPU使用率过高，或者剩余内存过低时，可发送邮件提醒；可设置自动清理缓存<br>

相较于之前的服务器资源监控工具（[快点我查看](https://github.com/leeyoshinari/performance_monitor) ），此次进行了大刀阔斧地改进，首先不再是单独的工具，而是集成进平台中，和平台中的其他工具可以无缝对接；其次是使用了全新的交互和监控方案，并引入了项目组和机房，更加适用于大规模集群部署的应用。
## 首页
首页展示了所有已经部署监控的服务器，这里可以概览服务器资源的当前使用情况。这个入口仅管理员可以看到，可分项目组查询。
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/monitor_home.JPG)
## 可视化
监控结果可视化，分项目组和机房查看，可选择任意时间段（监控数据保留时长在配置中设置）。<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/monitor_figure.JPG)
主要监控下面数据：<br>
- CPU：CPU 总使用率、iowait 使用率
- 内存：剩余内存、可用内存、JVM内存（仅Java）
- 磁盘：磁盘读写速度、磁盘IO
- 网络：网络上行和下行速度、网络使用率
- TCP：系统的TCP连接总数、TCP重传数，端口的TCP数量、time-wait数量、close-wait数量

查看监控结果时，默认展示指定项目组和机房下的所有服务器资源的平均值，左侧展示的是服务器列表，排列顺序按照CPU、IO、网络使用率权重（5:3:2）排序，颜色也按照这个权重计算展示。点击某个服务器，即可查看该服务器的资源监控数据。页面所有数据每隔10s刷新一次。<br>

# Nginx流量采集工具
该工具（[快点我部署](https://github.com/leeyoshinari/nginx_agent) ）主要用于解析Nginx的access.log，从日志中提取出接口访问数据。<br>
首页页面展示的信息是根据接口聚合后的结果（过滤掉静态文件的请求），默认按照QPS排序，可选按响应时间、响应体大小、响应错误数量排序；可分别查看压测流量和正常流量。
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/nginx_summary.JPG)

点击每个接口，可查看该接口的每秒数据变化图
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/nginx_detail.JPG)
注意：**为了采集到上述数据，需要修改nginx日志格式，详见[nginx-agent部署](https://github.com/leeyoshinari/nginx_agent )**

# 性能测试工具
现在开源的、最好用的性能测试工具是JMeter，很多公司的性能测试平台的底层都用的是JMeter，所以本工具底层也是用JMeter实现的，而且原滋原味的保留了JMeter的所有功能，让您像在本地使用JMeter一样的丝般顺滑，使用体验远超某电商的全链路压测平台。

该工具（[快点我部署](https://github.com/leeyoshinari/jmeter_agent) ）具有以下功能：<br>
- 在页面可以编辑JMeter脚本，也可以导入已有JMeter脚本；
- 支持根据压测情况随时调整TPS，可调整总的TPS，也可以调整每个施压机的TPS；
- 支持分布式压测，可以动态增加/减少施压机，实现施压机热挂载；
- 支持自动执行压测；
- 强大的赋能能力，该工具具有的功能几乎可以用于所有的JMeter脚本；
- 原滋原味的保留了JMeter的所有功能，只要本地能运行的脚本，用该工具都可以运行，因此也支持JMeter所有的扩展插件；

先说一下使用JMeter做HTTP接口性能测试的基本流程：<br>
1、创建jmx文件，编写压测脚本。压测脚本的结构是：`测试计划(Test Plan)—>线程组(Thread Group)—>控制器(Controller)—>取样器(HTTP Sample)`。<br>
另外还有一些辅助的组件例如：CSV数据文件设置、吞吐量控制器、Http Cookie管理器等。<br>
2、确定并发数，设置压测执行时间；<br>
3、执行压测；<br>
4、查看压测结果；<br>
以上，所以该工具的作用就是把上述步骤流程化、便捷化、自动化。<br>

## 在页面新增JMeter脚本
### 添加 Test Plan
在左侧点击 Test Plan，可以查看测试计划，测试计划列表如下：<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/plan_home.JPG)
Server Room 列可以查看该机房里空闲的施压机数量；<br>
Action列具有的一些操作：
- Enabled/Disabled：禁用/启用，对应JMeter右键菜单里的禁用/启用；
- Copy：复制，快速复制一个测试计划；
- Variables：设置全局变量，对应JMeter中的测试计划中的“用户自定义的变量”；
- ThreadGroup：查看测试计划中的所有线程组；
- StartTest：开始执行性能测试。如果是手动执行，则会立即开始压测；如果是自动执行，也会生成一个压测任务，等待压测时间开始执行；

点击 Variables，可以设置全局变量，如下：
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/plan_variable.JPG)

点击添加或编辑，出现下面的页面：（如果不清楚每个字段的意思，可点击问号查看提示）
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/plan_add.JPG)
- tearDown：对应JMeter中的 Test Plan 中的设置“主线程结束后运行tearDown线程组”；
- Serialize：对应JMeter中的 Test Plan 中的设置“独立运行每个线程组（例如在一个组运行结束后启动下一个）”；
- runType：指定压测脚本运行类型，可选指定线程数运行和指定TPS运行；
- Target TPS/Thread Num：当运行类型为指定TPS运行时，这里就是目标TPS；当运行类型为指定线程数运行时，这里就是线程数；
- Duration：压测执行时间，单位：秒；对应JMeter中的 Thread Group 中的设置“持续时间（秒）”；
- Schedule：压测执行方式，可选手动执行或自动执行。当选择自动执行时，需要设置自动执行的时间；
- Time Setting：用于设置自动执行时间，仅当Schedule设置为自动执行时生效。设置时间后，可以点击Preview预览压力变化曲线；
- Server Room：机房，指的是施压机所在的机房，压测脚本会在设置的机房的施压机上运行 (一般性能测试尽可能避免跨机房，减少网络对性能测试的影响)。压测时，该机房必须有可用的(空闲的)施压机；
- Server Number：施压机数，执行压测时，设置的机房里必须有足够数量的空闲的施压机；
- isDebug：如果设置Debug模式，则脚本在执行时候会生成jtl文件，该文件包含每一个请求的结果，正式测试时，建议设置非Debug模式，以免影响施压机性能；


### 添加 Thread Group
在左侧点击 Thread Group，可以查看所有的线程组；如果在 Test Plan 中点击 ThreadGroup，可以查看该测试计划下的所有线程组。线程组列表如下：<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/group_home.JPG)
Action列具有的一些操作：
- Enabled/Disabled：禁用/启用，对应JMeter右键菜单里的禁用/启用；
- Copy：复制，快速复制一个线程组；
- Cookies：如果压测需要cookies，可以在这里设置；对应的是JMeter中的Http Cookie管理器；
- Controller：查看线程组中的所有控制器；

Cookies 设置页面如下：
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/group_cookie.JPG)

点击添加或编辑，出现下面的页面：（如果不清楚每个字段的意思，可点击问号查看提示）
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/group_add.JPG)
- Plan ID：将该线程组绑定到指定的测试计划；
- Ramp Time：在这个时间内启动所有的线程，对应JMeter线程组中的“Ramp-Up时间（秒）”；
- CSVDataSet：上传压测需要的文件，需要设置变量名称（英文逗号分割）、分隔符、遇到文件结束符是否继续、线程共享模式，这里的设置和JMeter中的CSV数据文件设置一样；

### 添加控制器
在左侧点击 Controller，可以查看所有的控制器；如果在 Thread Group 中点击 Controller，可以查看该线程组下的所有控制器。控制器列表如下：<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/controller_home.JPG)
Action列具有的一些操作：
- Enabled/Disabled：禁用/启用，对应JMeter右键菜单里的禁用/启用；
- Copy：复制，快速复制一个控制器；
- HTTPSample：查看控制器中的所有取样器；

### 添加取样器
在左侧点击 HTTP Sample，可以查看所有的取样器；如果在 Controller 中点击 HttpSample，可以查看该控制器下的所有取样器。取样器列表如下：<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/sample_home.JPG)

点击添加或编辑，出现下面的页面：（如果不清楚每个字段的意思，可点击问号查看提示）
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/sample_add.JPG)
- Controller ID：把该取样器绑定到指定的控制器；
- Protocol：协议，可选HTTP或HTTPs；
- Domain Name：域名或ip；
- Port：端口号；
- Path：url 路径；
- Method：http请求方法；
- Arguments：http请求参数，可选请求参数格式为json或form表单，对应JMeter中的取样器的参数设置；
- HTTP Header：下拉选择对应的请求头，请求头配置在HTTP Header中；如果没有请求头，需要提前设置好；
- Assertion：断言，可选类型为Contain(包含)、Equal(相等)或Match(匹配)，对应JMeter中的响应断言；
- Post Extractor：后置处理器，用于提取响应值中的数据，仅支持JSON提取器和正则表达式提取器；
- contentEncoding：内容编码格式，可选None或UTF-8，对应JMeter中的取样器中的“内容编码”；

以上设置和在JMeter中的取样器中的设置一样，也可以引用变量，后置处理器也可以设置变量。

### 添加请求头
在左侧点击 HTTP Header，可以查看所有的请求头；
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/header_home.JPG)

在设置请求头时，只需要把字段和值填入即可，这里也可以引用变量，引用格式和JMeter一样。
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/header_add.JPG)
以上，就完成了在这个工具上手动编写压测脚本。如果已有本地的已经调试好的JMeter脚本，且是按照上面说的结构，可以在 Test Plan 页面直接点击 Import Plan 按钮导入进系统中。导入后会对文件进行解析，可能会有少许修改，可以在页面手动核对和修改。

## Upload JMeter
考虑到有些性能测试场景的压测脚本很复杂，例如有BeanShell脚本、for/if等控制语句，但仍想使用压测工具赋予的压测能力，可以把本地调试通过的JMeter脚本，连同需要使用的外部文件，打包成zip压缩包，然后在 Upload JMeter 页面上传该压缩包，上传成功后就可以使用工具赋予的压测能力了。<br>
这里说一下这个工具对上传的压缩包是怎么处理的：<br>
1、压缩包上传后，首先使用zip命令解压，故只支持zip格式压缩；<br>
2、解压后，直接在解压的文件夹中寻找jmx格式的JMeter脚本，压缩包里必须有且仅有一个jmx格式的文件；由于是直接在解压的文件中寻找jmx文件，故压缩文件时，选择需要压缩的文件，然后压缩，而不是选择文件夹进行压缩；<br>
3、经过一系列校验后，压缩包会被上传到文件系统；<br>
4、生成一条记录，然后可以在页面修改压测参数，和 Test Plan 一样，如下：<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/upload_home.JPG)

当需要压测的时候，会对JMeter文件进行修改，如下：<br>
1、从文件系统中下载文件，并解压；<br>
2、如果运行类型设置为指定TPS运行，则会往JMeter脚本中添加一个吞吐量控制器；如果运行类型设置为指定线程数运行，则会修改JMeter脚本中的 Thread Group 的参数；<br>
3、把修改后的jmx文件和其他依赖的文件一起打包，然后开始压测；<br>

## Test Task
在左侧点击 Test Task 可以查看所有的测试任务，所有待执行、执行中、已停止的测试记录都会显示在这里，只有测试完成后，才会显示Sample、TPS、RT、Error等数据。<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/task_home.JPG)
在Actions列，可以下载每个任务执行的JMeter文件，如果压测出现问题，可以下载文件看看是哪里出现问题了。

### 查看压测详情
在压测执行时或压测结束后，可以查看压测详情。当开始执行压测后，首先会生成压测所需要的文件，然后传给施压机，施压机会执行压测文件。此时页面会自动跳转到查看压测详情页面，由于压测初始化和产生压测结果需要时间，故需要等待一会儿才会在页面看到数据。<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/task_detail.JPG)
在压测详情页面可以的操作（页面右上角）：
- Stop：会立即停止压测；
- Change TPS：统一调整所有施压机的TPS；
- Download File：下载该任务执行的JMeter文件；

每个施压机可以的操作：
- View：查看单个施压机的压测数据；
- Start：启动该施压机开始压测，施压机启动需要一点时间，当启动后，就可以调整该施压机的TPS；
- Stop：停止该施压机的压测，其他施压机不停；
- Download logs：下载该施压机的JMeter执行的日志；
- Change TPS：调整单个施压机的TPS；

### 分布式压测
借用Redis实现分布式压测时各施压机之间的数据同步，各施压机的数据和所有施压机汇总数据的时间全部以InfluxDB的时间为准；这就突破了使用JMeter进行分布式压测时需要各施压机的系统时间、Java版本、JMeter版本必须一样的限制，可以更加方便进行分布式压测。

### 施压机热挂载
同样也是借用Redis实现的。当在性能测试过程中，发现压力不够，需要增加施压机时，只需要在当前压测任务下（即查看压测详情页面）启动一个施压机即可，而不需要单独另开启一个压测任务（两个任务之间的数据是独立的）；当需要下掉一个施压机时，直接点击施压机的停止按钮即可立即下线；可以更加灵活地调整压力。


# QAQ：
## 为什么shell会经常提醒 Session is in closed status？
为了避免可能的无效连接占用服务器资源，对超过10分钟没有任何数据交互的连接进行关闭；同时由于客户端网络问题或其他各种异常，服务端也需要及时关闭无效连接。<br>

## 为什么自动部署agent包时一直不成功？
首先核对Linux系统发行版本和CPU架构是否和部署包一致，然后查看部署日志。部署路径是配置文件`config.conf`中的`deployPath`。<br>

## 怎么判断是否需要增加集群节点数？
对于该平台的集群：在远程连接Linux时，如果由于非网络原因和服务器卡顿的原因导致命令的响应速度经常跟不上你的手速，那么应该增加平台的集群节点数；<br>
对于collector-agent：因为服务器资源监控是秒级，且近似实时，在查看服务器资源监控图时，如果刷新页面后展示的时间比当前时间晚5~10秒，那么就需要增加 collector-agent 集群节点数。<br>
以上纯属个人建议，请根据实际情况合理增加集群节点数。

## 单台施压机支持的QPS多少？
建议每台施压机的QPS不要超过3000/s（需要结合实际情况）。如果发现压力上不来，请先排除施压机和被测系统问题后，再增加一台施压机。<br>

## 性能测试怎么区分压测流量和正常流量？
如果你是在页面上手动编写的脚本，那么当脚本执行时，会自动把请求头中的 `User-Agent` 的值设置成 `PerformanceTest`，故可根据 `User-Agent` 区分压测流量。<br>
如果你是在`Upload JMeter`页面手动上传本地调试好的脚本，那么脚本中的请求头必须包含 `User-Agent` 字段，当执行脚本时，会自动把请求头中的 `User-Agent` 的值替换成 `PerformanceTest`。所以你的本地脚本中的请求头必须包含 `User-Agent` 字段。

## 性能测试的某个接口的请求怎么mock，或者写入影子表/影子库？
本工具只提供通用的压测能力，可根据请求头的 `User-Agent` 区分是否是压测流量。由于服务端的部署架构、语言和业务的不同，因此没法提供各语言的探针，可自己结合实际情况编写探针，来实现mock功能，或将数据写入影子表/影子库，或走影子链路。

## 服务器资源监控一直在运行，但为什么查询监控结果会有错误提示？
一般出现这种情况是因为服务器资源监控运行后，该服务器所属的项目组和机房被修改过，修改后的信息没有同步到资源监控工具，导致数据不一致。因此需要重启服务器资源监控工具，或者重新部署。
