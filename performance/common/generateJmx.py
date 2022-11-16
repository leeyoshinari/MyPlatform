#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import json
import time

def generate_test_plan(plans):
    var_str = ''
    if plans.variables:
        for variable in plans.variables:
            var_str += '<elementProp name="%s" elementType="Argument"><stringProp name="Argument.name">%s</stringProp>' \
                       '<stringProp name="Argument.value">%s</stringProp><stringProp name="Argument.metadata">=' \
                       '</stringProp></elementProp>' %(variable['name'], variable['name'], variable['value'])
    test_plan = '<TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="%s" enabled="%s"><stringProp ' \
               'name="TestPlan.comments">%s</stringProp><boolProp name="TestPlan.functional_mode">false</boolProp>' \
               '<boolProp name="TestPlan.tearDown_on_shutdown">%s</boolProp><boolProp name="TestPlan.serialize' \
               '_threadgroups">%s</boolProp><elementProp name="TestPlan.user_defined_variables" elementType="Arguments" ' \
               'guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">' \
               '<collectionProp name="Arguments.arguments">%s</collectionProp></elementProp><stringProp name=' \
               '"TestPlan.user_define_classpath"></stringProp></TestPlan>' %(plans.name, plans.is_valid,
                plans.comment, plans.tearDown, plans.serialize, var_str)
    return test_plan, plans.duration

def generate_thread_group(tg, num_threads, ramp_time, duration, schedule):
    if schedule == 1: duration += 60
    thread_group = '<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="%s" enabled="%s">' \
                        '<stringProp name="ThreadGroup.on_sample_error">continue</stringProp><elementProp name=' \
                        '"ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" ' \
                        'testclass="LoopController" testname="Loop Controller" enabled="true"><boolProp name="' \
                        'LoopController.continue_forever">false</boolProp><intProp name="LoopController.loops">' \
                        '-1</intProp></elementProp><stringProp name="ThreadGroup.num_threads">%s</stringProp>' \
                        '<stringProp name="ThreadGroup.ramp_time">%s</stringProp><boolProp name="' \
                        'ThreadGroup.scheduler">true</boolProp><stringProp name="ThreadGroup.duration">%s</stringProp>' \
                        '<stringProp name="ThreadGroup.delay"></stringProp><boolProp name="ThreadGroup.same' \
                        '_user_on_next_iteration">false</boolProp></ThreadGroup>' %(tg.name, tg.is_valid, num_threads,
                                                                                    ramp_time, duration)

    return thread_group

def generator_throughput(number_samples):
    throughput_str = '<ConstantThroughputTimer guiclass="TestBeanGUI" testclass="ConstantThroughputTimer" testname=' \
                     '"Constant Throughput Timer" enabled="true"><intProp name="calcMode">2</intProp><stringProp name="throu' \
                     'ghput">${__P(throughput, %d)}</stringProp></ConstantThroughputTimer><hashTree/>' %(number_samples*60)
    return throughput_str


def generate_cookie(cookies):
    cookie_str = ''
    if cookies:
        for coo in cookies:
            cookie_str += '<elementProp name="%s" elementType="Cookie" testname="%s"><stringProp name="Cookie.value"' \
                          '>%s</stringProp><stringProp name="Cookie.domain">%s</stringProp><stringProp name="Cookie' \
                          '.path">%s</stringProp><boolProp name="Cookie.secure">%s</boolProp><longProp name="Cookie' \
                          '.expires">0</longProp><boolProp name="Cookie.path_specified">true</boolProp><boolProp ' \
                          'name="Cookie.domain_specified">true</boolProp></elementProp>' %(coo.name, coo.name, coo.value,
                            coo.domain, coo.path, coo.secure)

    cookie_manager = '<CookieManager guiclass="CookiePanel" testclass="CookieManager" testname="HTTP Cookie管理器" enabled="true">' \
                  '<collectionProp name="CookieManager.cookies">%s</collectionProp><boolProp name="CookieManager.' \
                  'clearEachIteration">false</boolProp><boolProp name="CookieManager.controlledByThreadGroup">' \
                  'true</boolProp></CookieManager><hashTree/>' %cookie_str

    return cookie_manager

def generator_csv(csv_file):
    csv_data_set = ''
    if csv_file:
        csv_data_file_path = csv_file['file_path'].split('/')[-1]
        recycle = csv_file['recycle']
        stopThread = 'false' if recycle == 'true' else 'true'
        csv_data_set = '<CSVDataSet guiclass="TestBeanGUI" testclass="CSVDataSet" testname="CSV 数据文件设置" ' \
                        'enabled="true"><stringProp name="delimiter">%s</stringProp><stringProp name="fileEncoding"' \
                        '>UTF-8</stringProp><stringProp name="filename">%s</stringProp><boolProp name="ignoreFirstLine"' \
                        '>false</boolProp><boolProp name="quotedData">false</boolProp><boolProp name="recycle">%s</boolProp>' \
                        '<stringProp name="shareMode">%s</stringProp><boolProp name="stopThread">%s</boolProp>' \
                        '<stringProp name="variableNames">%s</stringProp></CSVDataSet><hashTree/>' %(csv_file['delimiter'],
                        csv_data_file_path, recycle, csv_file['share_mode'], stopThread, csv_file['variable_names'])
    return csv_data_set

def generator_controller(controllers):
    controller = '<TransactionController guiclass="TransactionControllerGui" testclass="TransactionController" ' \
                 'testname="%s" enabled="%s"><boolProp name="TransactionController.includeTimers">false</boolProp>' \
                 '<boolProp name="TransactionController.parent">true</boolProp><stringProp name="TestPlan.' \
                 'comments">%s</stringProp></TransactionController>' %(controllers.name, controllers.is_valid, controllers.comment)
    return controller

def generator_samples_and_header(samples, headers):
    http_sample_proxy = generator_samples(samples)
    header_manager = generator_header(headers)
    response_assert = generator_assert(samples.assert_type, samples.assert_content)
    all_extractor = generator_extractor(samples.extractor)
    return http_sample_proxy + '<hashTree>' + header_manager + response_assert + all_extractor + '</hashTree>'

def generator_samples(samples):
    port = samples.port if samples.port else ''
    contentEncoding = samples.contentEncoding if samples.contentEncoding else ''
    path = samples.path if samples.path else ''
    sample_arg_str = generator_sample_arguments(samples.argument)
    sample_str = '<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="%s" ' \
                 'enabled="%s">%s<stringProp name="HTTPSampler.domain">%s</stringProp><stringProp name="HTTPS' \
                 'ampler.port">%s</stringProp><stringProp name="HTTPSampler.protocol">%s</stringProp><stringPro' \
                 'p name="HTTPSampler.contentEncoding">%s</stringProp><stringProp name="HTTPSampler.path">%s</stringProp>' \
                 '<stringProp name="HTTPSampler.method">%s</stringProp><boolProp name="HTTPSampler.follow_redirects' \
                 '">true</boolProp><boolProp name="HTTPSampler.auto_redirects">false</boolProp><boolProp name="' \
                 'HTTPSampler.use_keepalive">true</boolProp><boolProp name="HTTPSampler.DO_MULTIPART_POST">false' \
                 '</boolProp><stringProp name="HTTPSampler.embedded_url_re"></stringProp><stringProp name="HTTP' \
                 'Sampler.connect_timeout"></stringProp><stringProp name="HTTPSampler.response_timeout">' \
                 '</stringProp><stringProp name="TestPlan.comments">%s</stringProp>' \
                 '</HTTPSamplerProxy>' %(samples.name, samples.is_valid, sample_arg_str, samples.domain,
                 port, samples.protocol, contentEncoding, path, samples.method, samples.comment)
    return sample_str

def generator_sample_arguments(arguments):
    argument_str = ''
    if arguments:
        if arguments.get('request_body_json'):
            argument_str = '<boolProp name="HTTPSampler.postBodyRaw">true</boolProp><elementProp name="HTTPsampler.' \
                           'Arguments" elementType="Arguments"><collectionProp name="Arguments.arguments">' \
                           '<elementProp name="" elementType="HTTPArgument"><boolProp name="HTTPArgument.always_' \
                           'encode">false</boolProp><stringProp name="Argument.value">%s</stringProp><stringProp name' \
                           '="Argument.metadata">=</stringProp></elementProp></collectionProp>' \
                           '</elementProp>' %json.dumps(arguments.get('request_body_json'))
        else:
            arg_str = ''
            for k, v in arguments.items():
                arg_str += '<elementProp name="%s" elementType="HTTPArgument"><boolProp name="HTTPArgument.always_' \
                           'encode">%s</boolProp><stringProp name="Argument.name">%s</stringProp><stringProp name="' \
                           'Argument.value">%s</stringProp><stringProp name="Argument.metadata">=</stringProp>' \
                           '<boolProp name="HTTPArgument.use_equals">true</boolProp></elementProp>' %(k, v['bool_prop_encode'], k, v[k])
            argument_str = '<elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArguments' \
                           'Panel" testclass="Arguments" enabled="true"><collectionProp name="Arguments.argument' \
                           's">%s</collectionProp></elementProp>' %arg_str
    return argument_str

def generator_header(headers):
    h_str = '<elementProp name="User-Agent" elementType="Header"><stringProp name="Header.name">User-Agent</stringProp>' \
            '<stringProp name="Header.value">PerformanceTest</stringProp></elementProp>'
    for k, v in headers.value.items():
        h_str += '<elementProp name="%s" elementType="Header"><stringProp name="Header.name">%s</stringProp>' \
                 '<stringProp name="Header.value">%s</stringProp></elementProp>' %(k, k, v)
    header = '<HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP信息头管理器" ' \
             'enabled="true"><collectionProp name="HeaderManager.headers">%s</collectionProp>' \
             '</HeaderManager><hashTree/>' % h_str

    return header

def generator_assert(assert_type, assert_value):
    assert_str = ''
    if assert_type and assert_value:
        assert_str = '<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="响应断言" e' \
                     'nabled="true"><collectionProp name="Asserion.test_strings"><stringProp name="%s">%s</stringProp>' \
                     '</collectionProp><stringProp name="Assertion.custom_message"></stringProp><stringProp name=' \
                     '"Assertion.test_field">Assertion.response_data</stringProp><boolProp name="Assertion.assume' \
                     '_success">false</boolProp><intProp name="Assertion.test_type">%s</intProp></ResponseAssertion>' \
                     '<hashTree/>' %(int(time.time()), assert_value, assert_type)
    return assert_str

def generator_extractor(extractors):
    regex_str = ''
    json_str = ''
    if extractors.get('regex'):
        for extr in extractors.get('regex'):
            regex_str += '<RegexExtractor guiclass="RegexExtractorGui" testclass="RegexExtractor" testname="正则表达式' \
                     '提取器" enabled="true"><stringProp name="RegexExtractor.useHeaders">false</stringProp>' \
                     '<stringProp name="RegexExtractor.refname">%s</stringProp><stringProp name="RegexExtractor.' \
                     'regex">%s</stringProp><stringProp name="RegexExtractor.template">%s</stringProp>' \
                     '<stringProp name="RegexExtractor.default"></stringProp><stringProp name="RegexExtractor.match' \
                     '_number">%s</stringProp><boolProp name="RegexExtractor.default_empty_value">true</boolProp>' \
                     '</RegexExtractor><hashTree/>' %(extr['refname'], extr['regex'], extr['template'], extr['match_number'])

    if extractors.get('json'):
        for extr in extractors.get('json'):
            json_str += '<JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" test' \
                        'name="JSON提取器" enabled="true"><stringProp name="JSONPostProcessor.referenceNames">%s</s' \
                        'tringProp><stringProp name="JSONPostProcessor.jsonPathExprs">%s</stringProp><stringPro' \
                        'p name="JSONPostProcessor.match_numbers">%s</stringProp></JSONPostProcessor>' \
                        '<hashTree/>' %(extr['referenceNames'], extr['jsonPathExprs'], extr['match_numbers'])

    return regex_str + json_str
