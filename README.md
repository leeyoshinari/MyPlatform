# MyPlatform
[中文文档](https://github.com/leeyoshinari/MyPlatform/blob/main/templates/README_zh.md)

## Introduction
It is a platform mainly used for performance test, here are some simple features brief: <br>
1. Server Management, can view server's basic information uniformly<br>
2. Shell Remote Connection, support for files upload and download between local and server<br>
3. Server resource usage monitoring<br>
4. Nginx's access.log traffic collection<br>
5. Performance Test tool, support for automated and distributed performance test<br>

## Directory
- MyPlatform - project files
- staticfiles - static files
- templates - html templates files
- templateFilter - custom filter
- common - generic functions
- user - user related
- shell - shell tool
- monitor - monitor tool
- performance - performance test tool

## Middleware
- Relational Database: SQLite3 or MySQL - used to store platform data
- Time-Series Database: InfluxDB - used to store monitoring data
- Key-value Database: Redis - used to cluster/distributed data synchronization
- File Server: MinIO - used to store files
- Performance Test tool: JMeter - used to execute JMeter file

## Architecture
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/myPlarform.png)
&emsp;&emsp;If you need to satisfy more users, please deploy cluster; if you need high availability, please deploy keepalive.

#### Explain
**collector-agent**<br>
&emsp;&emsp;Data Collector. All agents' data will be sent to collector-agent, and then collector-agent writes data to InfluxDB/redis.<br>
&emsp;&emsp;It can be avoid a problem: If each agent connects to the database separately, it may cause the database connection to run out or exceed the number of connections allowed by the server. <br>
&emsp;&emsp;But if too many agents cause the collector-agent to not be able to write database in time, increasing the thread pool size of the collector-agent is needed; if still not, increasing the number of collector-agent cluster nodes is needed.

**monitor-agent**<br>
&emsp;&emsp;Server resource monitor. Execute Linux commands to collect the server's CPU, Memory, Disk, Network, TCP, and other data in real time.

**nginx-agent**<br>
&emsp;&emsp;Nginx traffic collector. Process Nginx's access log (access.log) in real time, the access information (access time, client IP, interface name, request method, protocol, status code, response body size, response time) is stored in database.

**jmeter-agent**<br>
&emsp;&emsp;Performance test tool. Call JMeter to execute performance test, and supports distributed performance test and full-link performance test.

## Deploy
1. Clone Repository
    ```shell script
    git clone https://github.com/leeyoshinari/MyPlatform.git
    ``` 

2. Install MySQL(SQLite3 can be used directly, doesn't need to be installed), InfluxDB, Redis, MinIO(Optional installation); (ps：InfluxDB2.x is not supported, [ influxdb-1.8.3](https://dl.influxdata.com/influxdb/releases/influxdb-1.8.3.x86_64.rpm ) is recommended.)

3. Install third-party packages
    ```shell script
    pip3 install -r requirements.txt
    ```

4. Modify `config.conf`；

5. Initialize database, and execute commands
    ```shell script
    python3 manage.py migrate
    python3 manage.py makemigrations shell performance
    python3 manage.py migrate
    ```

6. Create super administrator
    ```shell script
    python3 manage.py createsuperuser
    ```

7. Initialize data
    ```shell script
    python3 manage.py loaddata initdata.json
    ```

8. Collect all static files
    ```shell script
    python3 manage.py collectstatic --clear --noinput
    ```

9. Compress static files (css and js)
    ```shell script
    python3 manage.py compress --force
    ```

10. Modify Port in `startup.sh`

11. Deploy `nginx`, the location configuration is as follows: (ps: The `platform` in the configuration is the prefix, that is the URL prefix in the URL path, which can be modified according to your needs.)<br>
    (1) upstream configuration:
    ```shell script
    upstream myplatform-server {
        server 127.0.0.1:15200;
        server 127.0.0.1:15201;
    }
    ```
    (2) static request: Use Nginx to access static files directly
    ```shell script
    location /platform/static {
        alias /home/MyPlatform/static;
    }
    ```
    (3) dynamic request:
    ```shell script
    location /platform {
         proxy_pass  http://myplatform-server;
         proxy_set_header Host $proxy_host;
         proxy_set_header X-Real-IP $remote_addr;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    ```
    (4) websocket protocol:
    ```shell script
    location /shell {  # must be shell, don't modify it
        proxy_pass http://myplatform-server;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    ```

12. Startup
    ```shell script
    sh startup.sh
    ```
    Run `sh shutdown.sh` to stop.

13. Access home page, url: `http://ip:port/(prefix in config.conf)`
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/home.JPG)

14. Access permission management page, url: `http://ip:port/(prefix in config.conf)/admin`

15. Deploy collector-agent, [please click me](https://github.com/leeyoshinari/collector_agent)

16. Deploy monitor-agent, [please click me](https://github.com/leeyoshinari/monitor_agent)

17. Deploy jmeter-agent, [please click me](https://github.com/leeyoshinari/jmeter_agent)

18. Deploy nginx-agent, [please click me](https://github.com/leeyoshinari/nginx_agent)

## Note
1. For more information, [please click me](https://github.com/leeyoshinari/MyPlatform/blob/main/templates/course_en.md) or view course after deployment.

## Requirements
Local dev environment:
- python 3.9.10

Third-party packages version:
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
