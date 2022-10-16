from django.db import models
from django.contrib.auth.models import Group
from shell.models import ServerRoom
# Create your models here.

class TestPlan(models.Model):
    id = models.CharField(max_length=16, verbose_name='Test Plan ID', primary_key=True)
    name = models.CharField(null=True, max_length=100, verbose_name='Plan Name')
    comment = models.CharField(null=True, max_length=200, verbose_name='comment')
    tearDown = models.CharField(max_length=8, default='true', verbose_name='tearDown_on_shutdown')
    serialize = models.CharField(max_length=8, default='true', verbose_name='serialize_threadgroups')
    type = models.IntegerField(default=1, verbose_name='run type, 0-Thread, 1-TPS')
    schedule = models.IntegerField(default=0, verbose_name='schedule type, 0-Manual, 1-Automatic')
    target_num = models.IntegerField(default=1, verbose_name='target num')
    duration = models.IntegerField(default=1800, verbose_name='duration (second)')
    time_setting = models.JSONField(null=True, verbose_name='time setting run')
    is_valid = models.CharField(max_length=8, verbose_name='true, false')
    is_debug = models.IntegerField(default=0, verbose_name='0-Not debug, 1-debug')
    variables = models.JSONField(null=True, verbose_name='variables')
    server_room = models.ForeignKey(ServerRoom, default=520, on_delete=models.CASCADE, verbose_name='server room')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='group name')
    server_number = models.IntegerField(default=1, verbose_name='number of pressure servers')
    is_file = models.IntegerField(default=0, verbose_name='is Jmeter file, 0-import Jmeter file, 1-upload Jmeter file')
    file_path = models.CharField(null=True, max_length=125, verbose_name='file path if is_file=1')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='Create time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'jmeter_test_plan'


class ThreadGroup(models.Model):
    id = models.CharField(max_length=16, verbose_name='thread group id', primary_key=True)
    plan = models.ForeignKey(TestPlan, on_delete=models.PROTECT, verbose_name='test plan id')
    group = models.IntegerField(null=True, verbose_name='group id')
    name = models.CharField(null=True, max_length=100, verbose_name='thread group name')
    is_valid = models.CharField(max_length=8, verbose_name='true, false')
    ramp_time = models.IntegerField(null=True, verbose_name='ramp_time')
    cookie = models.JSONField(null=True, verbose_name='cookie')
    file = models.JSONField(null=True, verbose_name='CSVDataSet')
    comment = models.CharField(null=True, max_length=200, verbose_name='comment')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='Create time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'jmeter_thread_group'
        indexes = [models.Index(fields=['group'])]


class TransactionController(models.Model):
    id = models.CharField(max_length=16, verbose_name='Controller id', primary_key=True)
    thread_group = models.ForeignKey(ThreadGroup, on_delete=models.CASCADE, verbose_name='thread group id')
    group = models.IntegerField(null=True, verbose_name='group id')
    name = models.CharField(null=True, max_length=100, verbose_name='Controller name')
    is_valid = models.CharField(max_length=8, verbose_name='true, false')
    comment = models.CharField(null=True, max_length=200, verbose_name='comment')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='Create time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'jmeter_controller'
        indexes = [models.Index(fields=['group'])]


class HTTPRequestHeader(models.Model):
    id = models.CharField(max_length=16, verbose_name='http header id', primary_key=True)
    name = models.CharField(null=True, max_length=100, verbose_name='name')
    method = models.CharField(max_length=8, verbose_name='method')
    value = models.JSONField(null=True, verbose_name='value')
    comment = models.CharField(null=True, max_length=200, verbose_name='comment')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='Create time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'jmeter_http_header'


class HTTPSampleProxy(models.Model):
    id = models.CharField(max_length=16, verbose_name='http sample id', primary_key=True)
    controller = models.ForeignKey(TransactionController, on_delete=models.CASCADE, verbose_name='controller id')
    group = models.IntegerField(null=True, verbose_name='group id')
    name = models.CharField(null=True, max_length=100, verbose_name='http sample name')
    is_valid = models.CharField(max_length=8, verbose_name='true, false')
    comment = models.CharField(null=True, max_length=200, verbose_name='comment')
    domain = models.CharField(null=True, max_length=20, verbose_name='domian or host')
    port = models.CharField(null=True, max_length=6, verbose_name='port')
    protocol = models.CharField(max_length=8, verbose_name='protocol')
    path = models.CharField(null=True, max_length=64, verbose_name='path')
    method = models.CharField(max_length=8, verbose_name='request method')
    contentEncoding = models.CharField(null=True, max_length=8, verbose_name='contentEncoding')
    argument = models.JSONField(null=True, verbose_name='request arguments')
    http_header = models.ForeignKey(HTTPRequestHeader, on_delete=models.PROTECT, verbose_name='http header id')
    assert_type = models.IntegerField(null=True, verbose_name='test type, 2-contain, 1-match, 8-equal')
    assert_content = models.CharField(null=True, max_length=32, verbose_name='test strings')
    extractor = models.JSONField(null=True, verbose_name='post extractor')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='Create time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'jmeter_http_sample'
        indexes = [models.Index(fields=['group'])]


class PerformanceTestTask(models.Model):
    id = models.CharField(max_length=16, verbose_name='task id', primary_key=True)
    plan = models.ForeignKey(TestPlan, on_delete=models.CASCADE, verbose_name='plan id')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='group name')
    number_samples = models.IntegerField(default=1, verbose_name='number of http samples')
    ratio = models.FloatField(verbose_name='ratio, target_num * ratio')
    status = models.IntegerField(verbose_name='status, 0-pending run, 1-running, 2-stopped, 3-failure, 4-cancel')
    samples = models.IntegerField(default=0, verbose_name='# Samples')
    average_rt = models.FloatField(default=0, verbose_name='Average Response Time (ms)')
    tps = models.FloatField(default=0, verbose_name='TPS (/s)')
    min_rt = models.FloatField(default=0, verbose_name='min Response Time (ms)')
    max_rt = models.FloatField(default=0, verbose_name='max Response Time (ms)')
    error = models.FloatField(default=0, verbose_name='error(%)')
    path = models.CharField(null=True, max_length=128, verbose_name='all files used to test, *.zip')
    server_room = models.ForeignKey(ServerRoom, on_delete=models.CASCADE, verbose_name='server room')
    running_num = models.IntegerField(default=0, verbose_name='pressure server running number')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='Create time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='Update time')
    start_time = models.DateTimeField(null=True, verbose_name='task start time')
    end_time = models.DateTimeField(null=True, verbose_name='task end time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'jmeter_test_task'


class TestTaskLogs(models.Model):
    id = models.CharField(max_length=16, verbose_name='log id', primary_key=True)
    task = models.ForeignKey(PerformanceTestTask, on_delete=models.CASCADE, verbose_name='task id')
    action = models.IntegerField(null=True, verbose_name='action, 0-change TPS, 1-add server, 2-del server')
    value = models.CharField(max_length=20, verbose_name='action value')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='Create Time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'jmeter_test_task_log'
