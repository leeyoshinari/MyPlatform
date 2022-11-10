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
from django.conf import settings
from . import views

app_name = 'monitor'
urlpatterns = [
    path('register/getinfo', views.get_room_group_by_host, name='get_room_group_by_host'),
    path('server/home', views.home, name='home'),
    path('server/visualize', views.visualize, name='visualize'),
    path('server/register', views.registers, name='register'),
    #path('server/register/first', views.register_first, name='register_first'),
    path('server/getPortAndDisk', views.get_port_disk, name='get_port_disk'),
    path('server/plotMonitor', views.plot_monitor, name='plot_monitor'),
    path('register/notification', views.notice, name='notification'),
    path('server/change/group', views.change_group, name='change_group'),
    path('server/change/room', views.change_room, name='change_room'),
    path('nginx/home', views.nginx_home, name='nginx_home'),
    path('nginx/summary', views.query_nginx_summary, name='nginx_summary'),
    path('nginx/detail', views.query_nginx_detail, name='nginx_detail'),
] if settings.IS_MONITOR == 1 else []
