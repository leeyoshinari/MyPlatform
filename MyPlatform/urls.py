"""MyPlatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from user.views import home, course, register_first

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home', home, name='home'),
    path('course', course, name='course'),
    path('register/first', register_first, name='register_first'),
    path('user/', include('user.urls'), name='user'),
    path('shell/', include('shell.urls'), name='shell'),
    path('monitor/', include('monitor.urls'), name='monitor'),
    path('performance/', include('performance.urls'), name='perf'),
]

urlpatterns = [
    path(f'{settings.PREFIX}/', include(urlpatterns))
]
