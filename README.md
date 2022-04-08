# MyPlatform

4、初始化数据库，依次执行下面命令；
```shell script
python3 manage.py migrate
python3 manage.py makemigrations myfiles
python3 manage.py sqlmigrate myfiles 0001
python3 manage.py migrate
```

6、创建管理员账号；
```shell script
python3 manage.py createsuperuser
```

7、处理admin页面的静态文件；
```shell script
python3 manage.py collectstatic
```