# MyPlatform
[中文文档](https://github.com/leeyoshinari/MyPlatform/blob/main/templates/README_zh.md) 

## Introduction
It is a platform mainly used for performance testing, here are some simple features brief: <br>
1. Server Management, can view server's basic information uniformly<br>
2. Shell Remote Connection, support for files upload and download between local and server<br>
3. Server resource usage monitoring<br>
4. Nginx's access.log traffic collection<br>
5. Performance Testing tool, support for automated and distributed performance testing<br>

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

11. Deploy `nginx`, the `location` configuration is as follows: (ps: The `platform` in the configuration is the prefix, that is the URL prefix in the URL path, which can be modified according to your needs.)<br>
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

15. For more information, please [click me](https://blog.ihuster.top).
