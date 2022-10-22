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
    path('get/server', views.get_server, name='get_server'),
    path('edit/server', views.edit_server, name='edit_server'),
    path('add/user', views.add_user, name='add_user'),
    path('create/group', views.create_group, name='create_group'),
    path('get/group', views.get_all_group, name='get_group'),
    path('create/room', views.create_room, name='create_room'),
    path('get/room', views.get_all_room, name='get_room'),
    path('delete/server', views.delete_server, name='delete_server'),
    path('search/server', views.search_server, name='search_server'),
    path('file/upload', views.upload_file, name='upload_file'),
    path('file/download', views.download_file, name='download_file'),

    path('package/home', views.package_home, name='package_home'),
    path('package/delete', views.delete_package, name='delete_package'),
    path('package/deploy', views.deploy_package, name='deploy_package'),
    path('package/stop', views.uninstall_deploy, name='stop_package'),
    path('package/upload', views.package_upload, name='upload_package'),
]
