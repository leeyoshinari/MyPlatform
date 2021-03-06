"""webssh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = 'shell'
urlpatterns = [
    path('', views.index, name='index'),
    path('open', views.openssh, name='open_shell'),
    path('add/server', views.add_server, name='add_server'),
    path('add/user', views.add_user, name='add_user'),
    path('create/group', views.create_group, name='create_group'),
    path('delete/server', views.delete_server, name='delete_server'),
    path('search/server', views.search_server, name='search_server'),
    path('file/upload', views.upload_file, name='upload_file'),
    path('file/download', views.download_file, name='download_file'),
    path('monitor/deploy', views.deploy_monitor, name='deploy_monitor'),
    path('monitor/stop', views.stop_monitor, name='stop_monitor')
]
