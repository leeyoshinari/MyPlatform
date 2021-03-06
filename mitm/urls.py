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

app_name = 'mitm'
urlpatterns = [
    path('', views.home, name='home'),
    path('course', views.course, name='course'),
    path('save', views.save, name='save'),
    path('update', views.update, name='update'),
    path('edit/<int:rule_id>', views.edit, name='edit'),
    path('isRun', views.isRun, name='is_run'),
    path('reload', views.reload, name='reload'),
    path('delete/<int:rule_id>', views.delete, name='delete'),
] if settings.IS_MITMPROXY == 1 else []
