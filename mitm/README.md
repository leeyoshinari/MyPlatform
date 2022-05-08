# MyPlatform/mitm
这是一个拦截指定的http协议请求的工具，然后直接返回响应值。<br>

详细教程，请在服务启动成功后，点击教程按钮查看 <br>

### 功能
1、自定义http协议拦截规则，支持通过域名和url路径拦截<br>
2、可设置任意状态码，响应值可设置成任意字符串，支持设置读取本地文件的路径<br>
3、支持篡改请求参数，或篡改响应值<br>
4、修改规则后，支持手动加载使规则即时生效<br>

### 实现
1、服务端是Django框架，用于提供web服务<br>
2、客户端用户拦截http请求<br>
3、进程间通信：redis <br>

如只想使用拦截功能，[可以在这里单独部署]( https://github.com/leeyoshinari/mitm_mock.git )，进程间通信用的是 queue。

# 使用
1、安装依赖包  `pip3 install -r requirements.txt`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Mac 需要最新版的pip，如果不是最新版本的pip，请先升级pip，执行命令 `pip3 install --upgrade pip`

2、配置mitmproxy环境变量<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Windows 在环境变量的 path 中添加 mitmproxy 的可执行文件路径<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Linux 将 mitmproxy 的可执行文件软连接到 /usr/bin/mitmproxy<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Mac 将 mitmproxy 的可执行文件软连接到 /usr/local/bin/mitmproxy<br>

3、设置系统代理<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Windows设置方法：`打开“设置——>网络和Internet——>代理——>手动设置代理”`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Linux设置方法：`export http_proxy=http://ip:port`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Mac设置方法：`打开“系统偏好设置——>网络——>高级——>代理——>网页代理(HTTP) 或 安全网页代理(HTTPS)”`<br>
<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;取消代理设置<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Windows取消方法：直接在“手动设置代理”的地方关闭即可<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Linux取消方法：`unset http_proxy` <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Mac取消方法：直接在“代理”页面关闭即可<br>


# 注意
1、每次使用时，需开启系统代理；使用完成后，须关闭代理；

2、由于该工具是拦截 http 请求，所以拦截时，目标IP地址和目标端口必须存在，必须能够完成 TCP 三次握手；

3、如果需要拦截（mock）https的请求，需要安装证书，其他操作和http的基本一样；证书在用户目录下的 .mitmproxy 文件夹中，安装 mitmproxy-ca-cert.cer。

