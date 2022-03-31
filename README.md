# MyPlatform

4、初始化数据库，依次执行下面命令；
```shell script
python3 manage.py migrate
python3 manage.py makemigrations myfiles
python3 manage.py sqlmigrate myfiles 0001
python3 manage.py migrate
```
