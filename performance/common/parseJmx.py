#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import json
import xml.etree.ElementTree as ET


def read_jmeter_from_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    test_plans = get_test_plan(root)
    return test_plans


def read_jmeter_from_byte(file_byte):
    root = ET.fromstring(file_byte.decode())
    test_plans = get_test_plan(root)
    return test_plans


def get_test_plan(parent_node):
    test_plans_list = []
    try:
        test_plan_hash_trees = parent_node.findall('hashTree')
        for test_plan_hash_tree in test_plan_hash_trees:
            test_plans = test_plan_hash_tree.findall('TestPlan')
            for test_plan in test_plans:
                test_plan_dict = {}
                test_plan_dict.update({'testname': test_plan.attrib['testname']})
                test_plan_dict.update({'enabled': test_plan.attrib['enabled']})
                if test_plan.findall('stringProp'):
                    test_plan_dict.update({'comments': test_plan.findall('stringProp')[0].text})
                bool_props = test_plan.findall('boolProp')
                for bool_prop in bool_props:
                    if bool_prop.attrib['name'] == 'TestPlan.tearDown_on_shutdown':
                        test_plan_dict.update({'tearDown_on_shutdown': bool_prop.text})
                    if bool_prop.attrib['name'] == 'TestPlan.serialize_threadgroups':
                        test_plan_dict.update({'serialize_threadgroups': bool_prop.text})
                elementProps = test_plan.findall('elementProp')[0].findall('collectionProp')[0].findall('elementProp')
                arguments = {}
                for ele in elementProps:
                    stringProps = ele.findall('stringProp')
                    for stringProp in stringProps:
                        if stringProp.attrib['name'] == 'Argument.name':
                            argument_name = stringProp.text
                        if stringProp.attrib['name'] == 'Argument.value':
                            argument_value = stringProp.text
                    arguments.update({argument_name: argument_value})

                test_plan_dict.update({'arguments': arguments})
                test_plan_dict.update({'thread_group': get_threah_group(test_plan_hash_tree)})

                test_plans_list.append(test_plan_dict)
    except:
        raise
    return test_plans_list


def get_threah_group(parent_node):
    thread_groups_list = []
    try:
        thread_group_hash_trees = parent_node.findall('hashTree')
        for thread_group_hash_tree in thread_group_hash_trees:
            thread_groups = thread_group_hash_tree.findall('ThreadGroup')
            for thread_group in thread_groups:
                thread_group_dict = {}
                thread_group_dict.update({'testname': thread_group.attrib['testname']})
                thread_group_dict.update({'enabled': thread_group.attrib['enabled']})
                stringProps = thread_group.findall('stringProp')
                for stringProp in stringProps:
                    if stringProp.attrib['name'] == 'ThreadGroup.num_threads':
                        thread_group_dict.update({'num_threads': stringProp.text})
                    if stringProp.attrib['name'] == 'ThreadGroup.ramp_time':
                        thread_group_dict.update({'ramp_time': stringProp.text})
                    if stringProp.attrib['name'] == 'ThreadGroup.duration':
                        thread_group_dict.update({'duration': stringProp.text})
                    if stringProp.attrib['name'] == 'TestPlan.comments':
                        thread_group_dict.update({'comments': stringProp.text})
                thread_group_dict.update({'scheduler': [bool_prop.text for bool_prop in thread_group.findall('boolProp')
                             if bool_prop.attrib['name'] == 'ThreadGroup.scheduler'][0]})

                thread_group_dict.update({'controller': get_controller(thread_group_hash_tree)})
                thread_groups_list.append(thread_group_dict)
    except:
        raise

    return thread_groups_list


def get_controller(parent_node):
    controllers_list = []
    try:
        controller_hash_trees = parent_node.findall('hashTree')
        for controller_hash_tree in controller_hash_trees:
            flag = 0
            controller_dict = {}
            for controller in controller_hash_tree:
                if flag != 1:
                    controller_dict = {}
                if 'Controller' in controller.tag and flag == 0:
                    controller_dict.update({'testname': controller.attrib['testname']})
                    controller_dict.update({'enabled': controller.attrib['enabled']})
                    if controller.findall('stringProp'):
                        controller_dict.update({'comments': controller.findall('stringProp')[0].text})
                    flag += 1
                if controller.tag == 'hashTree' and controller.findall('HTTPSamplerProxy') and flag == 1:
                    flag += 1
                    controller_dict.update({'http_sample': get_http_sample(controller)})

                if flag == 2:
                    controllers_list.append(controller_dict)
                    flag = 0
    except:
        raise

    return controllers_list


def get_http_sample(http_sample):
    https_list = []
    try:
        http_sample_proxys = http_sample.findall('HTTPSamplerProxy')
        http_sample_hash_trees = http_sample.findall('hashTree')
        if len(http_sample_proxys) != len(http_sample_hash_trees):
            raise Exception('不一样')
        for i in range(len(http_sample_proxys)):
            http_dict = {}
            http_dict.update({'testname': http_sample_proxys[i].attrib['testname']})
            http_dict.update({'enabled': http_sample_proxys[i].attrib['enabled']})
            http_dict.update({'arguments': get_arguments(http_sample_proxys[i])})
            http_dict.update({'sample_dict': get_http_sample_dict(http_sample_proxys[i])})
            http_dict.update({'assertion': get_assertion(http_sample_hash_trees[i])})
            http_dict.update({'extractor': get_extractor(http_sample_hash_trees[i])})
            https_list.append(http_dict)
    except:
        raise

    return https_list


def get_arguments(parent_node):
    """get http sample arguments"""
    elementProps = parent_node.findall('elementProp')[0].findall('collectionProp')[0].findall('elementProp')
    arguments = {}
    try:
        for ele in elementProps:
            stringProps = ele.findall('stringProp')
            bool_prop_encode = [bool_prop.text for bool_prop in ele.findall('boolProp')
                                if bool_prop.attrib['name'] == 'HTTPArgument.always_encode'][0]
            argument_name = None
            argument_value = None
            for stringProp in stringProps:
                if stringProp.attrib['name'] == 'Argument.name':
                    argument_name = stringProp.text
                if stringProp.attrib['name'] == 'Argument.value':
                    argument_value = stringProp.text
            if argument_name:
                arguments.update({argument_name: {argument_name: argument_value, 'bool_prop_encode': bool_prop_encode}})
            else:
                arguments.update({'request_body_json': json.loads(argument_value)})
    except:
        raise
    return arguments


def get_http_sample_dict(parent_node):
    """get http sample"""
    stringProps = parent_node.findall('stringProp')
    http_sample_dict = {}
    try:
        for stringProp in stringProps:
            http_sample_dict.update({stringProp.attrib['name'].split('.')[-1]: stringProp.text})
    except:
        raise
    return http_sample_dict


def get_assertion(parent_node):
    """get assert"""
    try:
        response_assertion = parent_node.findall('ResponseAssertion')
        if response_assertion:
            test_type = response_assertion[0].findall('intProp')[0].text  # assert type, 2-contain, 1-match, 8-equal
            test_string = response_assertion[0].findall('collectionProp')[0].findall('stringProp')[0].text
            return {'test_type': test_type, 'test_string': test_string}
        else:
            return {}
    except:
        return {}


def get_extractor(parent_node):
    """get RegexExtractor or get JSONPostProcessor"""
    try:
        regex_extractors = parent_node.findall('RegexExtractor')
        json_extractors = parent_node.findall('JSONPostProcessor')
        regex_extractors_list = []
        json_extractors_list = []
        for regex_extractor in regex_extractors:
            regex_extractor_dict = {}
            string_props = regex_extractor.findall('stringProp')
            bool_prop = regex_extractor.findall('boolProp')[0]
            regex_extractor_dict.update({bool_prop.attrib['name'].split('.')[-1]: bool_prop.text})
            for string_prop in string_props:
                regex_extractor_dict.update({string_prop.attrib['name'].split('.')[-1]: string_prop.text})
            regex_extractors_list.append(regex_extractor_dict)

        for json_extractor in json_extractors:
            json_extractor_dict = {}
            string_props = json_extractor.findall('stringProp')
            for string_prop in string_props:
                json_extractor_dict.update({string_prop.attrib['name'].split('.')[-1]: string_prop.text})
            json_extractors_list.append(json_extractor_dict)

        return {'regex': regex_extractors_list, 'json': json_extractors_list}
    except:
        return {}


if __name__ == '__main__':
    file_path = 'E:\\apache-jmeter-5.4.3\\test.jmx'
    print(read_jmeter_from_file(file_path))