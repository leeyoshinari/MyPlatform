# MyPlatform
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
- performance - performance testing tool

## Middleware
- Relational Database: SQLite3 or MySQL - used to store platform data
- Time-Series Database: InfluxDB - used to store monitoring data
- Key-value Database: Redis - used to cluster/distributed data synchronization
- File Server: MinIO - used to store files
- Performance Testing tool: JMeter - used to execute JMeter file

## Architecture
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/myPlarform.png)
If you need to satisfy more users, please deploy cluster; if you need high availability, please deploy keepalive.

#### Explain
**collector-agent**<br>
Data Collector. All agents' data will be sent to collector-agent, and then collector-agent writes data to InfluxDB/redis.<br>
It can be avoid a problem: If each agent connects to the database separately, it may cause the database connection to run out or exceed the number of connections allowed by the server. But if too many agents cause the collector-agent to not be able to write database in time, increasing the thread pool size of the collector-agent is needed; if still not, increasing the number of collector-agent cluster nodes is needed.

**monitor-agent**<br>
Server resource monitor. Execute Linux commands to collect the server's CPU, Memory, Disk, Network, TCP, and other data in real time.

**nginx-agent**<br>
Nginx traffic collector. Process Nginx's access log (access.log) in real time, the access information (access time, client IP, interface name, request method, protocol, status code, response body size, response time) is stored in database.

**jmeter-agent**<br>
Performance testing tool. Call JMeter to execute performance testing, and supports distributed performance testing and full-link performance testing.

## Third-party Package
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

## Deploy
1. Clone Repository
    ```shell script
    git clone https://github.com/leeyoshinari/MyPlatform.git
    ``` 

2. Install MySQL(SQLite3 can be used directly, doesn't need to be installed), InfluxDB, Redis, MinIO(Optional installation); (ps：InfluxDB2.x is not supported, [ influxdb-1.8.3](https://dl.influxdata.com/influxdb/releases/influxdb-1.8.3.x86_64.rpm ) is recommended.)

3. Install third-packages
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

15. Deploy collector-agent, [please click me](https://github.com/leeyoshinari/collector_agent)

16. Deploy monitor-agent, [please click me](https://github.com/leeyoshinari/monitor_agent)

17. Deploy jmeter-agent, [please click me](https://github.com/leeyoshinari/jmeter_agent)

18. Deploy nginx-agent, [please click me](https://github.com/leeyoshinari/nginx_agent)

## Shell Tool
In Shell Tool, you can view and manage servers, and remote connect Linux on browser directly.
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/shell_home.JPG)

### Usage
#### Setting Project Group
Click `Create Group` to create project, the project name and unique identifier for application of project are needed. Unique identifier is unique throughout the company, for linux server,  use `ps -ef | grep Unique Identifier | grep -v grep` to find a unique process.<br>
The button is visible only to the administrator.
#### Setting the Server Room
Click `Create Server Room` to create server room, there are three options for setting the server room: application, middleware, and pressure test. Why are there three?<br>
For example, there are 100 servers in a server room, and Project group A uses 40 servers to deploy its own services, Project group B uses 40 servers to deploy its own services, and 10 servers to deploy middleware, and remaining 10 servers used to performance testing. Because of this Repository integrates Server Management, Server Monitor and Performance Test together, the three options are added in order to distinguish them. It's not like company's platform that different people develop different services and just hanging the front page together.<br>
The button is visible only to the administrator.
#### Add Servers
Click `Add Server` to create server, you need to set the project to which the server belongs, the server room where the server is, and the server IP address, user name, and login password.
#### User Management
Click `Add User` to add a user to a project or remove a user from a project. After user is added, that user can view and access all servers in the project. Administrator can view all servers by default.<br>
The button is visible only to the administrator.
#### Server's List
Each added server is displayed in the list, giving you an overview of the basic information about the server (system, CPU, memory, disk). The Action column allows you to operate the server, where you can open the Shell to remotely connect to Linux; The edit and delete buttons are visible only to the creator and administrator.
#### Remote Connection to the Server
Click `OpenShell` to open Shell remote connection to Linux, and you can open many pages at the same time, as follows:
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/shell_ternimal.JPG)

To provide a better experience, the Ctrl+C(copy) and Ctrl+V(paste) shortcuts are provided. Not only that, but the Ctrl+C shortcut is still able to terminate foreground processes in the linux shell, which is not supported by most popular shell tools.<br>

In the open Shell, you can upload files to the server or download files from server to local. The entry for uploading and downloading can also be closed for security.<br>
- When uploading file, the input box will pop up firstly, and then need to enter the directory which the folder is uploaded to (absolute path, default `/home`), and then Upload.<br>
- When downloading file, the input box will also pop up, and then need to enter the complete path (absolute path) of the file, and then download to local. You must enter the file path, not the folder path.<br>
#### Deploy Agent
Click `Deploy` to open a new page, in this page, you can upload deployment packages, auto-deploy and uninstall.<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/shell_deploy.JPG)

Owing to deployment packages differ from Linux distribution and CPU architecture. Therefore, you need to prepare the deployment packages and upload them to the platform for deployment. If the deployment package doesn't differentiate between Linux distribution and CPU architecture, you can choose one of them randomly when uploading the deployment package.<br>
All agents can be automatically deployed on this platform (Currently, only [monitor-agent](https://github.com/leeyoshinari/monitor_agent ), [jmeter-agent](https://github.com/leeyoshinari/jmeter_agent ), [nginx-agent](https://github.com/leeyoshinari/nginx_agent ), java, jmeter can be deployed). For the convenience of deployment, all agent configuration files have been simplified. Generally, there is no need to modify any configuration, and all configurations are automatically obtained from the platform. Suggested deployment sequence: first deploy Java (only the pressure machine is deployed and has not been deployed), then deploy JMeter (only the pressure machine is deployed), then deploy the collector-agent, and deploy other agents that need to be deployed.

Before clicking Deploy/Uninstall, please carefully check whether the Linux system release version and CPU architecture of the current server are consistent with the Linux system release version and CPU architecture of the deployment package.<br>
Note: In rare cases, you need to modify the agent configuration file. For example, your nginx deployment method is different from 99% of people. It cannot automatically obtain the nginx log path. In this case, you need to modify the configuration file.

## Server Monitoring
This tool ([click me](https://github.com/leeyoshinari/monitor_agent)) is mainly used to monitor server resource usage, and the functions are:
- Monitor the CPU usage, io wait, memory usage, disk IO, network  and TCP connections of the entire server<br>
- Monitor the TCP state of the port<br>
- For java applications, you can monitor the jvm  and GC; when the frequency of Full GC is too high, an email reminders can be sent<br>
- When the CPU usage of the system is too high, or the remaining memory is too low, an email reminder can be sent; the cache can be automatically cleared<br>

Compared with the previous server resource monitoring tool ([click me](https://github.com/leeyoshinari/performance_monitor)), it has been greatly improved now. First of all, it is no longer a separate tool, but integrated into the platform, which can be seamlessly connected with other tools in the platform; secondly It uses a new interaction and monitoring solution, and introduces project groups and server rooms, which are more suitable for large-scale cluster deployment applications.

### Home Page
The home page shows all the servers that have been monitored, where you can get an overview of the current usage of server resources. This entry can only be seen by the administrator, and can be queried by project group.
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/monitor_home.JPG)

### Visualization
Data visualization, view by project group and server room, you can choose any time period (the monitoring data retention period is set in the configuration).<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/monitor_figure.JPG)

Mainly monitor the following data:<br>
- CPU: total CPU usage, iowait usage
- Memory: remaining memory, available memory, JVM memory (only for Java)
- Disk: disk read and write speed, disk IO
- Network: network uplink and downlink speed, network usage
- TCP: the total number of TCP connections in the system, the number of TCP retransmissions, the number of TCP ports, the number of time-wait, and the number of close-wait

When viewing the monitoring datas, the average value of all server resources under the specified project group and server room is displayed by default. The server list is displayed on the left, sorted according to the weight of CPU, IO, and network usage (5:3:2), and the color is also calculated and displayed according to this weight. Click on a server to view the monitoring data of the server. All data on the page is refreshed every 10s.

## Nginx Flow Collect
This tool ([click me](https://github.com/leeyoshinari/nginx_agent)) is mainly used to parse the access.log of Nginx and extract interface access data from the log.<br>
The information displayed on the home page is based on the aggregated results of interfaces (requests for static files are filtered out), sorted by QPS by default, and optionally sorted by response time, response body size, and number of response errors; you can view performance testing traffic and normal traffic separately.<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/nginx_summary.JPG)

Click on each interface to view the data change graph of the interface per second.
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/nginx_detail.JPG)

Note: **In order to collect the above data, the nginx log format needs to be modified, see [nginx-agent](https://github.com/leeyoshinari/nginx_agent) for details**.

## Performance Testing
Now the open-source and best-used performance testing tool is JMeter. Many companies' performance testing platforms are based on JMeter, so this platform is also based on JMeter, and it retains all the original functions of JMeter, let you use JMeter as silky and smooth as you use locally.

The tool([click me](https://github.com/leeyoshinari/jmeter_agent)) has the following functions:<br>
- JMeter scripts can be edited on the page, or also import existing JMeter scripts;
- Support to adjust TPS at any time according to the performance testing situation, the total TPS can be adjusted, and the TPS of each pressure machine can also be adjusted;
- Support distributed performance testing, can dynamically increase/decrease the pressure machines;
- Support automatic performance testing;
- Powerful enabling ability, the functions of this platform can be used in almost all JMeter scripts;
- The original taste retains all the functions of JMeter. As long as the script can be run locally, it can be run with this tool, so it also supports all extensions of JMeter;

Let's see the basic process of using JMeter to do HTTP interface performance testing:<br>
1. Create a jmx file and write a stress test script. The structure of the stress test script is: `Test Plan—>Thread Group—>Controller—>HTTP Sample`;<br>
In addition, there are some auxiliary components such as: `CSV Data Set Config`, `Constant Throughput Timer`, `HTTP Cookie Manager`, etc.<br>
2. Determine the number of concurrency, and set duration;<br>
3. Execute performance testing;<br>
4. View the performance testing results;<br>
Above, so the function of this platform is to streamline, facilitate and automate the above steps.<br>

### Specific Usage
#### Add JMeter scripts on the page
##### Add Test Plan
Click `Test Plan` on the left to view the test plans. The list of test plans is as follows:<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/plan_home.JPG)

In the `Server Room` column, you can view the number of idle pressure machines in the server room;<br>
Some operations in the `Action` column:
- Enabled/Disabled: corresponding to `Disable/Enable` in the right-click menu of JMeter;
- Copy: quickly copy a test plan;
- Variables: Set global variables, corresponding to the "user-defined variables" in the test plan in JMeter;
- ThreadGroup: View all thread groups in the test plan;
- StartTest: Start performance testing. If it is executed manually, the performance testing will start immediately; if it is executed automatically, a performance testing task will also be generated and wait for the time to start execution;

Click `Variables` to set global variables, as follows:
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/plan_variable.JPG)

Click Add or Edit, and the following page will display: (If you don’t know the meaning of each field, you can click the `question mark` to view the prompt)
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/plan_add.JPG)
- tearDown: Run tearDown Thread Groups after shutdown of main threads;
- Serialize: Run Thread Groups consecutively (i.e. one at a time);
- runType: Specify the running type of the test script, and can choose to run with a specified number of threads or a specified TPS;
- Target TPS/Thread Num: When the running type is the specified TPS, this is the target TPS; when the running type is the specified number of threads, this is the number of threads;
- Duration: The performance testing execution time, unit: seconds; corresponding to the setting "Duration (seconds)" in Thread Group in JMeter;
- Schedule: Execution mode of performance testing, manual execution or automatic execution can be selected. When selecting automatic execution, you need to set the automatic execution time;
- Time Setting: Used to set the automatic execution time, which only takes effect when the Schedule is set to automatic execution. After setting the time, you can click Preview to preview the pressure change curve;
- Server Room: The test script will run on the pressure machines in the set server room (General, performance testing should avoid crossing computer rooms as much as possible to reduce the impact of the network). During the performance testing, the server room must have some available (idle) pressure machines;
- Server Number: The number of pressure machines. During the performance testing, there must be a sufficient number of idle pressure machines in the server room;
- isDebug: If it's Debug mode, the script will generate a `jtl` file during execution, which contains the results of each request. It is recommended to set a non-Debug mode during formal testing to avoid affecting the performance of the pressure machines;

##### Add Thread Group
Click `Thread Group` on the left to view all thread groups; if you click `ThreadGroup` in `Test Plan`, you can view all thread groups under the test plan. The thread groups list is as follows:<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/group_home.JPG)

Some operations in the `Action` column:
- Enabled/Disabled: corresponding to `Disable/Enable` in the right-click menu of JMeter;
- Copy: quickly copy a thread group;
- Cookies: If the performance testing requires cookies, you can set them here; corresponding to the `HTTP Cookie Manager` in JMeter;
- Controller: View all controllers in the thread group;

The Cookies settings page is as follows:
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/group_cookie.JPG)

Click Add or Edit, and the following page will display: (If you don’t know the meaning of each field, you can click the `question mark` to view the prompt)
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/group_add.JPG)
- Plan ID: Bind the thread group to the specified test plan;
- Ramp Time: Start all threads within this time, corresponding to the "Ramp-up period (seconds)" in the JMeter thread group;
- CSVDataSet: Upload the files required for performance testing. It is the same as the `CSV Data Set Config` in JMeter;

##### Add Controller
Click `Controller` on the left to view all controllers; if you click `Controller` in `Thread Group`, you can view all controllers under the thread group. The list of controllers is as follows:<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/controller_home.JPG)

Some operations in the `Action` column:
- Enabled/Disabled: corresponding to `Disable/Enable` in the right-click menu of JMeter;
- Copy: quickly copy a controller;
- HTTPSample: View all samplers in the controller;

##### Add HTTP Sample
Click `HTTP Sample` on the left to view all samplers; if you click `HttpSample` in `Controller`, you can view all samplers under the controller. The list of samplers is as follows:<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/sample_home.JPG)

Click Add or Edit, and the following page will display: (If you don’t know the meaning of each field, you can click the `question mark` to view the prompt)
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/sample_add.JPG)
- Controller ID: Bind the sampler to the specified controller;
- Protocol: optional HTTP or HTTPs;
- Domain Name: domain name or ip;
- Port: port number;
- Path: url path;
- Method: http request method;
- Arguments: HTTP request parameters, the optional request parameter format is json or form, corresponding to the parameter settings of the sampler in JMeter;
- HTTP Header: Select the request header, the request header is configured in the HTTP Header; if there is no request header, it needs to be set in advance;
- Assertion: Optional type is Contain, Equal or Match, corresponding to the response assertion in JMeter;
- Post Extractor: Used to extract the data in the response body, only JSON extractor and regular extractor are supported;
- contentEncoding: Optional None or UTF-8, corresponding to the "Content encoding" in the sampler in JMeter;

All the above settings are the same as the functions in JMeter.

##### Add HTTP Header
Click `HTTP Header` on the left to view all request headers;
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/header_home.JPG)

When setting the request header, just fill in the fields and values. Variables can also be referenced, and the reference format is the same as JMeter.
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/header_add.JPG)
Above, the manual editing of the performance testing script on this platform is completed. If you already have a local JMeter script that has been debugged and follows the structure mentioned above, you can directly click the `Import Plan` button on the `Test Plan` page to import it into the system. After importing, the file will be parsed, and there may be a little modification, which can be checked and modified manually on the page.

#### Upload JMeter
Considering that the stress test scripts of some performance testing scenarios are very complicated, for example, there are BeanShell scripts, for/if, etc., but you still want to use the performance testing capabilities provided by the platform, you can package the JMeter script that has passed local debugging, together with the external files that need to be used, into a zip archive, and then upload the archive on the Upload JMeter page. After uploading successfully, you can use the performance testing capability provided by the platform.<br>
Here is how this tool handles the uploaded zip packages:<br>
1. After uploading, firstly use `zip` command to decompress the package. So, only the zip format is supported.<br>
2. After decompressing, find JMeter scripts(jmx format) directly in the extracted folder, and there must be only one jmx file in the compressed package; When compressing, select files compression instead of selecting folders to compress;<br>
3. After checking, the zip package is uploaded to the file system;<br>
4. Generate a record, and then modify the performance testing parameters on the page, like the `Test Plan`. As follows:<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/upload_home.JPG)

When starting the performance testing, the JMeter file will be modified, as follows:<br>
1. Download the package from the file system and decompress it;<br>
2. If the running type is `Specify TPS`, a `Constant Throughput Timer` is added to the JMeter script. If the running type is `Specified number of threads`, the parameters of the `Thread Group` in the JMeter script will be modified;<br>
3. Package the modified jmx file, and other dependent files, then start performance testing;<br>

#### Test Task
Click `Test Task` on the left to view all test tasks, all pending, executing, and stopped test tasks are displayed here, Only performance testing is completed, the Sample, TPS, RT, and Error will be displayed.<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/task_home.JPG)

In the `Actions` column, the JMeter files for each task execution can be downloaded. If something goes wrong with the performance testing, you can download the file to see what went wrong.

##### View Detail
You can view the performance testing details during or after the performance testing is executed.<br>
When the performance testing is started, it automatically redirects to the Detail page of performance testing. Since it takes time to initialize the performance testing and generate the results, you will need to wait a while before you see the data on the page.<br>
![](https://github.com/leeyoshinari/MyPlatform/blob/main/staticfiles/img/task_detail.JPG)

The operations on the performance testing details page are as follows (upper-right corner of the page):
- Stop: Stop performance testing immediately;
- Change TPS: Adjust TPS of all pressure machines uniformly;
- Download File: Download JMeter script of the test task;

The operations of every pressure machines are as follows:
- View: View test result of a single pressure machine;
- Start: Start performance testing. It takes a little time for starting performance testing, and when it starts, the TPS of the pressure machine can be adjusted;
- Stop: Stop the pressure machine, and the other pressure machines do not stop;
- Download logs: Download the JMeter log of the pressure machine;
- Change TPS: Adjust the TPS of a single pressure machine;

### Distributed performance testing
Redis is used to synchronize the distributed performance testing of the data between the each pressure machine. Each pressure machine's data and all pressure machines' data are provided by InfluxDB. It breaks through the limitation that the system time, Java version, and JMeter version of each pressure machine must be the same when using JMeter for distributed performance testing, which can make distributed performance testing more convenient.

### Hot mounting of the pressure machine
Also implemented using Redis. When it is found that the pressure is not enough during the performance testing and the pressure machine needs to be added, you only need to start a pressure machine under the current performance testing task (that is, view the performance testing details page), instead of opening another performance testing task separately (the data between the two tasks is independent). When you need to drop a pressure machine, you can directly click the stop button of the pressure machine to immediately go offline, pressure can be adjusted more flexibly.

## QAQ：
### Why does the `shell` often remind `Session is in closed status`?
To avoid possible invalid connections consuming server resources, close connections that have not any interaction for more than 10 minutes. At the same time, due to client network problems or other various exceptions, the server also needs to close invalid connections promptly.<br>

### Why does the automatic `agent` deployment fail?
First, check whether the Linux system distribution version and CPU architecture are consistent with the deployment package, then review the deployment logs. The deployment path is `deployPath` in the `config.conf`.<br>

### How can I determine whether to increase the number of cluster nodes?
For platform: When connecting to Linux remotely, if the response speed of commands often can't keep up with your hand speed due to non-network reasons and server stuttering, then you should increase the number of cluster nodes of the platform;<br>
For collector-agent: Since server resource monitoring is second-level and near real-time, when viewing the monitoring result, if the display time is 5 to 10 seconds later than the current time after refreshing the page, then you need to increase the number of collector-agent cluster nodes.<br>
Please increase the number of cluster nodes reasonably according to the actual situation.

### How much QPS does a single pressure machine support?
The QPS for each pressure machine is recommended not to exceed 3000/s. If the pressure doesn't come up, please eliminate the problem of the pressure machine and the system, and then add a pressure machine.

### How does the performance testing distinguish between pressure flow and normal flow?
If you edit the script manually on the page, and when the script executes, the value of `User-Agent` in the request header will be automatically set to `PerformanceTest`, so the performance testing flow can be distinguished according to the `User-Agent`.<br>
If you are manually uploading the local debugged script on the `Upload JMeter` page, then the request header in the script must contain the `User-Agent` field. When the script is executed, the value of `User-Agent` in the request header is automatically replaced with `PerformanceTest`. So the request header in local script must contain the `User-Agent` field.

### How can an interface of performance testing be mock or written to shadow tables/shadow databases?
The platform only provides general performance testing capabilities, which can distinguish whether it is a performance testing traffic according to the `User-Agent` of the request header. Due to the different deployment architecture, language, and business, it is impossible to provide probes in each language. You can write probes based on actual situations to implement mock functions, or write data to shadow tables/databases, or shadow links.

### Server resource monitoring has been running, but why do I get an error message when querying the monitoring results?
Generally, this situation occurs because the project group and server room which the server belongs to have been modified after the monitor-agent is running. The modified information is not synchronized to the monitor-agent, resulting in inconsistent data. So, you need to restart the monitor-agent or redeploy it.
