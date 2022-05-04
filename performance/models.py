from django.db import models

# Create your models here.

class TestPlan(models.Model):
    id = models.IntegerField(verbose_name='Test Plan ID', primary_key=True)
    name = models.CharField(null=True, max_length=100, verbose_name='Plan Name')
    comment = models.CharField(null=True, max_length=200, verbose_name='comment')
    tearDown = models.CharField(max_length=8, verbose_name='tearDown_on_shutdown')
    serialize = models.CharField(max_length=8, verbose_name='serialize_threadgroups')
    is_valid = models.CharField(max_length=8, verbose_name='true, false')
    create_time = models.DateTimeField(verbose_name='Create time')
    update_time = models.DateTimeField(verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'jmeter_test_plan'


class GlobalVariable(models.Model):
    id = models.IntegerField(verbose_name='variable id', primary_key=True)
    plan = models.ForeignKey(TestPlan, on_delete=models.CASCADE, verbose_name='test plan id')
    name = models.CharField(max_length=32, verbose_name='variable name')
    value = models.CharField(max_length=64, verbose_name='variable value')
    comment = models.CharField(null=True, max_length=200, verbose_name='comment')
    create_time = models.DateTimeField(verbose_name='Create time')
    update_time = models.DateTimeField(verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'jmeter_variable'


class ThreadGroup(models.Model):
    id = models.IntegerField(verbose_name='thread group id', primary_key=True)
    plan = models.ForeignKey(TestPlan, on_delete=models.PROTECT, verbose_name='test plan id')
    name = models.CharField(null=True, max_length=100, verbose_name='thread group name')
    is_valid = models.CharField(max_length=8, verbose_name='true, false')
    num_threads = models.IntegerField(null=True, verbose_name='num_threads')
    ramp_time = models.IntegerField(null=True, verbose_name='ramp_time')
    duration = models.IntegerField(null=True, verbose_name='duration')
    scheduler = models.CharField(null=True, max_length=8, verbose_name='scheduler')
    comment = models.CharField(null=True, max_length=200, verbose_name='comment')
    create_time = models.DateTimeField(verbose_name='Create time')
    update_time = models.DateTimeField(verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'jmeter_thread_group'


class TransactionController(models.Model):
    id = models.IntegerField(verbose_name='Controller id', primary_key=True)
    thread_group = models.ForeignKey(ThreadGroup, on_delete=models.PROTECT, verbose_name='thread group id')
    name = models.CharField(null=True, max_length=100, verbose_name='Controller name')
    is_valid = models.CharField(max_length=8, verbose_name='true, false')
    comment = models.CharField(null=True, max_length=200, verbose_name='comment')
    create_time = models.DateTimeField(verbose_name='Create time')
    update_time = models.DateTimeField(verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'jmeter_controller'


class HTTPRequestHeader(models.Model):
    id = models.IntegerField(verbose_name='http header id', primary_key=True)
    name = models.CharField(null=True, max_length=100, verbose_name='name')
    method = models.CharField(max_length=8, verbose_name='method')
    value = models.JSONField(verbose_name='value')
    create_time = models.DateTimeField(verbose_name='Create time')
    update_time = models.DateTimeField(verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'jmeter_http_header'


class HTTPSampleProxy(models.Model):
    id = models.IntegerField(verbose_name='http sample id', primary_key=True)
    controller = models.ForeignKey(TransactionController, on_delete=models.PROTECT, verbose_name='controller id')
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
    create_time = models.DateTimeField(verbose_name='Create time')
    update_time = models.DateTimeField(verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'jmeter_http_sample'


class PerformanceTestTask(models.Model):
    id = models.IntegerField(verbose_name='task id', primary_key=True)
    name = models.CharField(null=True, max_length=100, verbose_name='task name')
    plan_id = models.IntegerField(verbose_name='plan id')
    type = models.IntegerField(verbose_name='run type, 0-thread, 1-QPS')
    schedule = models.IntegerField(verbose_name='schedule type, 0-regular, 1-time setting')
    init_num = models.IntegerField(verbose_name='init num')
    current_num = models.IntegerField(verbose_name='init num')
    status = models.IntegerField(verbose_name='status, 0-pending run, 1-running, 2-run success, 3-run failure')
    time_setting = models.CharField(max_length=8, verbose_name='time setting run')
    create_time = models.DateTimeField(verbose_name='Create time')
    update_time = models.DateTimeField(verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'jmeter_test_task'
