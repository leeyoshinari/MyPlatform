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
from . import taskViews
from . import threadViews
from . import controllerViews
from . import sampleViews
from . import headerViews
from . import jmeterViews

app_name = 'perf'
urlpatterns = [
    path('home', taskViews.home, name='home'),
    path('delete', views.delete, name='delete'),
    path('setStatus', views.is_valid, name='set_status'),

    path('plan', planViews.home, name='plan_home'),
    path('plan/add', planViews.add, name='plan_add'),
    path('plan/edit', planViews.edit, name='plan_edit'),
    path('plan/copy', planViews.copy_plan, name='plan_copy'),
    path('plan/file/upload', planViews.upload_file, name='plan_upload_file'),
    path('plan/variable', planViews.edit_variable, name='plan_variable'),

    path('task', taskViews.home, name='task_home'),
    path('task/register', taskViews.register, name='agent_register'),
    path('task/status', taskViews.get_running_status, name='task_status'),
    path('task/add', taskViews.add_to_task, name='task_add'),
    path('task/delete', taskViews.delete_task, name='task_delete'),
    path('task/start', taskViews.start_task, name='task_start'),
    path('task/stop', taskViews.stop_task, name='task_stop'),
    path('task/download', taskViews.download_file, name='task_download'),
    path('task/download/log', taskViews.download_log, name='task_download_log'),
    path('task/change', taskViews.change_tps, name='change_tps'),
    path('task/register/getMessage', taskViews.set_message, name='task_set_message'),
    path('task/query', taskViews.query_data, name='task_query'),
    path('task/detail', taskViews.view_task_detail, name='task_detail'),
    path('task/getIdleServer', taskViews.get_idle_server, name='get_idle_server'),
    path('task/getUsedServer', taskViews.get_used_server, name='get_used_server'),
    path('task/getRunningServer', taskViews.get_running_server, name='get_running_server'),
    path('task/autoRun', views.request_auto_run, name='auto_run_test'),

    path('group', threadViews.home, name='group_home'),
    path('group/add', threadViews.add_group, name='group_add'),
    path('group/edit', threadViews.edit_group, name='group_edit'),
    path('group/copy', threadViews.copy_group, name='group_copy'),
    path('group/cookie', threadViews.edit_cookie, name='group_cookie'),
    path('group/file/upload', threadViews.upload_file, name='group_upload_file'),
    path('group/file/delete', threadViews.delete_file, name='group_delete_file'),

    path('controller', controllerViews.home, name='controller_home'),
    path('controller/add', controllerViews.add_group, name='controller_add'),
    path('controller/copy', controllerViews.copy_controller, name='controller_copy'),
    path('controller/edit', controllerViews.edit_group, name='controller_edit'),

    path('sample', sampleViews.home, name='sample_home'),
    path('sample/header', sampleViews.get_from_header, name='sample_header_home'),
    path('sample/add', sampleViews.add_sample, name='sample_add'),
    path('sample/edit', sampleViews.edit_sample, name='sample_edit'),
    path('sample/copy', sampleViews.copy_sample, name='sample_copy'),
    path('header/getByMehtod', sampleViews.get_header_by_method, name='get_header_by_method'),

    path('header', headerViews.home, name='header_home'),
    path('header/add', headerViews.add_header, name='header_add'),
    path('header/edit', headerViews.edit_header, name='header_edit'),
    path('header/copy', headerViews.copy_header, name='header_copy'),

    path('jmeter', jmeterViews.home, name='jmeter_home'),
    path('jmeter/edit', jmeterViews.edit, name='jmeter_edit'),
    path('jmeter/upload', jmeterViews.upload_file, name='jmeter_upload'),
    path('jmeter/start', jmeterViews.add_to_task, name='jmeter_add'),

] if settings.IS_PERF == 1 else []
