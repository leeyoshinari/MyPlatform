"""
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
from . import planViews
from . import threadViews
from . import controllerViews
from . import sampleViews
from . import headerViews

app_name = 'perf'
urlpatterns = [
    path('home', views.parse_jmx),
    path('delete', views.delete, name='delete'),
    path('setStatus', views.is_valid, name='set_status'),

    path('plan', planViews.home, name='plan_home'),
    path('plan/add', planViews.add, name='plan_add'),
    path('plan/edit', planViews.edit, name='plan_edit'),
    path('plan/copy', planViews.copy_plan, name='plan_copy'),
    path('plan/file/upload', planViews.upload_file, name='plan_upload_file'),
    path('plan/variable', planViews.variable, name='plan_variable'),
    path('plan/variable/add', planViews.add_variable, name='plan_add_variable'),
    path('plan/variable/edit', planViews.edit_variable, name='plan_edit_variable'),

    path('task', planViews.task_home, name='task_home'),
    path('task/add', planViews.add_to_task, name='task_add'),
    path('task/start', planViews.start_task, name='task_start'),
    path('task/stop', planViews.stop_task, name='task_stop'),

    path('group', threadViews.home, name='group_home'),
    path('group/add', threadViews.add_group, name='group_add'),
    path('group/edit', threadViews.edit_group, name='group_edit'),
    path('group/copy', threadViews.copy_group, name='group_copy'),
    path('group/cookie', threadViews.edit_cookie, name='group_cookie'),
    path('group/file/upload', threadViews.upload_file, name='group_upload_file'),

    path('controller', controllerViews.home, name='controller_home'),
    path('controller/add', controllerViews.add_group, name='controller_add'),
    path('controller/copy', controllerViews.copy_controller, name='controller_copy'),
    path('controller/edit', controllerViews.edit_group, name='controller_edit'),

    path('sample', sampleViews.home, name='sample_home'),
    path('sample/header', sampleViews.get_from_header, name='sample_header_home'),
    path('sample/add', sampleViews.add_sample, name='sample_add'),
    path('sample/edit', sampleViews.edit_sample, name='sample_edit'),
    path('sample/copy', sampleViews.copy_sample, name='sample_copy'),

    path('header', headerViews.home, name='header_home'),
    path('header/add', headerViews.add_header, name='header_add'),
    path('header/edit', headerViews.edit_header, name='header_edit'),
    path('header/copy', headerViews.copy_header, name='header_copy'),

] if settings.IS_PERF == 1 else []
