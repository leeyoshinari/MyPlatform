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
    path('', views.home, name='home'),
    path('startMonitor', views.start_monitor, name='start_monitor'),
    # path('getMonitor', views.get_monitor, name='get_monitor'),
    path('visualize', views.visualize, name='visualize'),
    # path('course_zh_CN', views.course_zh_CN, name='course_zh_CN'),
    # path('course_en', views.course_en, name='course_en'),
    path('register', views.registers, name='register'),
    path('register/first', views.register_first, name='register_first'),
    path('getPortAndDisk', views.get_port_disk, name='get_port_disk'),
    path('runMonitor', views.run_monitor, name='run_monitor'),
    path('plotMonitor', views.plot_monitor, name='plot_monitor'),
] if settings.IS_MONITOR == 1 else []
